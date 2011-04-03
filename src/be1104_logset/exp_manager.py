from optparse import OptionParser
import yaml
import os 
import sys
import glob
 
from procgraph.core.registrar import default_library
from procgraph.core.model_loader import pg_look_for_models
from procgraph.block_utils.file_io import make_sure_dir_exists

def model_info(block_type, library=default_library):
    gen = library.get_generator_for_block_type(block_type)
    return gen

def block_name_config(x):
    if not 'model' in x:
        msg = 'Invalid config %r' % x
        raise Exception(msg)

    model = x['model']
    if isinstance(model, list): # [model, {args}]
        return model[0], model[1]
    else: 
        return model, {}


def names(signals):
    return [x.name for x in signals]
        
def write_string_to_file(s, filename):
    make_sure_dir_exists(filename)
    with open(filename, 'w') as f:
        f.write(s) 

def block_name_from_conf(x):
    if not 'model' in x:
        msg = 'Invalid config %r' % x
        raise Exception(msg)
    model = x['model']
    assert isinstance(model, list) and len(model) == 2
    return model[0]
    

def exp_run(config):
    outdir = config['outdir']
    source = config['source']
    pres = config['presentation']
        
    write_string_to_file(create_source_model(source),
                         os.path.join(outdir, '%s.pg' % source['id']))

    serialized_vars = []
    for i, stage in enumerate(config['stages']):
        stage_model_name = '%s_stage%d' % (config['id'], i)
        stage_model = create_stage_model(stage_model_name,
                                                source, pres, stage,
                                                serialized_vars,
                                                outdir)
        write_string_to_file(stage_model,
                             os.path.join(outdir, '%s.pg' % stage_model_name))

def create_stage_model(stage_model_name, source, pres, stage, serialized_vars, outdir):
    source_block_name = 'source'
    source_block_type = block_name_from_conf(source['play'][0])
    source_block_generator = model_info(source_block_type)
    source_block_output = names(source_block_generator.output) 

    pres_block_name = 'presentation'
    pres_block_type = block_name_from_conf(pres)
    pres_block_generator = model_info(pres_block_type)
    pres_block_input = names(pres_block_generator.input) 
    pres_block_output = names(pres_block_generator.output) 
    
    stage_block_name = 'stage'
    stage_block_type = block_name_from_conf(stage)
    stage_block_generator = model_info(stage_block_type)
    stage_block_input = names(stage_block_generator.input) 
    stage_block_output = names(stage_block_generator.output) 
    
    
    M = '''--- model %s \n''' % stage_model_name
    # First add the source
    M += model_string(source_block_name, source['id'], {}) + '\n\n'
    
    # Now add the presentation stage
    pres_block_connections = []
    for s in pres_block_input:
        if not s in source_block_output:
            raise Exception('Could not find signal %r in %r.' % 
                            (s, source_block_output))
        pres_block_connections.append((source_block_name, s, s))
         
    M += (signals_string(pres_block_connections) + 
          ' --> ' + 
          model_string_from_spec(pres_block_name, pres) + 
          '\n\n')
    
    def serialization_filename(signal):
        return os.path.join(outdir, 'variables', '%s.pickle' % signal) 

    # Signals that we need for the processing stage
    signal2serialization_blocks = {}
    connections = [] 
    for input_signal in stage_block_input:
        if input_signal in source_block_output:
            connections.append((source_block_name, input_signal, input_signal))
        elif input_signal in pres_block_output:
            connections.append((pres_block_name, input_signal, input_signal))
        elif input_signal in serialized_vars:
            if not input_signal in signal2serialization_blocks:
                s_block_name = 'ser_%s' % input_signal
                signal2serialization_blocks[input_signal] = s_block_name
                M += model_string(s_block_name, 'pickle_load',
                                  {'file': serialization_filename(input_signal)})
                M += '\n\n'
            s_block_name = signal2serialization_blocks[input_signal]
            connections.append((s_block_name, 0, input_signal))
        else: 
            msg = 'Could not find candidate for signal %r.' % input_signal
            raise Exception(msg)
    M += (signals_string(connections) + 
          ' --> ' + 
          model_string_from_spec(stage_block_name, stage)) + '\n\n'
    
    # Now serialize the outputs of the stage
    for output_signal in stage_block_output: 
        assert not output_signal in serialized_vars
        serialized_vars.append(output_signal)
        connections = [(stage_block_name, output_signal, 0)]
        filename = serialization_filename(output_signal)
        M += (signals_string(connections) + 
              ' --> ' + 
              model_string('ser_%s' % output_signal,
                           'pickle', {'file': filename})) + '\n\n'
    return M

def signals_string(signals):
    return ", \\\n".join(['%s.%s[%s]' % (source, source_signal, dest) 
                      for (source, source_signal, dest) in signals])

def model_string(name, block_type, config):
    params = " ".join(['%s=%r' % (k, v) for (k, v) in config.items()])
    return '|%s:%s %s|' % (name, block_type, params)

def model_string_from_spec(block_name, spec):
    block_type, block_config = block_name_config(spec)
    params = " ".join(['%s=%r' % (k, v) for (k, v) in block_config.items()])
    return '|%s:%s %s|' % (block_name, block_type, params)

def create_source_model(source):
    model_name = source['id']
    M = """--- model %s\n\n""" % model_name

    gen = model_info(block_name_from_conf(source['play'][0]))
    source_out = names(gen.output)

    for s in source_out:
        M += 'output %s \n' % s
        
    M += '\n'
        
        
    for n, log in enumerate(source['play']):
        M += model_string_from_spec('source%d' % n, log) + '\n'
        
    M += '\n'
    
    nlogs = len(source['play']) 
    for s in source_out:
        signals = ", ".join(['source%d.%s' % (i, s) for i in range(nlogs)])
        mux = '%s --> |any_%s:any| --> |output name=%s|\n' % (signals, s, s) 
        M += mux 
        
    return M
    

def exp_manager(configuration, outdir):
    '''
        Main manager for running a set of experiments.
        
        :param configuration: YAML configuration file
        :param outdir: Main outdir file
    ''' 
    
    with open(configuration) as f:
        config = yaml.load(f)
    
    # Load sources configuration files
    dirname = os.path.dirname(configuration)
    
    pg_look_for_models(default_library, additional_paths=[dirname])

    
    sources, presentations = load_sources_config([dirname]) 

    for k in config:
        c = config[k]
        c['id'] = k
        source = c['source']
        if not source in sources:
            raise Exception('Unknown source %r in %r.' % (source, sources))
        c['source'] = sources[source]
        
        pres = c['presentation']
        if not pres in presentations:
            raise Exception('Unknown pres %r in %r.' % (pres, presentations))
        c['presentation'] = presentations[pres]

        c['outdir'] = os.path.join(outdir, c['id'])
        exp_run(c) 
        
def load_sources_config(dirs):
    sources = {}            
    presentation = {}

    for d in dirs:
        for f in glob.glob(os.path.join(d, '*.sources.yaml')):
            with open(f) as g:
                contents = yaml.load(g)
                for k in contents:
                    assert k not in sources
                    sources[k] = contents[k]
                    sources[k]['id'] = k 
        
        for f in glob.glob(os.path.join(d, '*.presentation.yaml')):
            with open(f) as g:
                contents = yaml.load(g)
                for k in contents:
                    assert k not in sources
                    presentation[k] = contents[k]
                    presentation[k]['id'] = k
    
    return sources, presentation

def main():
    usage = 'Main manager for running a set of experiments with analysis.'
    
    parser = OptionParser(usage=usage)
    
    parser.add_option("--config", help="YAML configuration file")
    parser.add_option("--outdir", help="Output base directory")
    
    (options, args) = parser.parse_args()
    
    try:
        if args: raise Exception('Spurious args: %r' % args)
        if options.config is None: raise Exception('Please specify --config.')
        if options.outdir is None: raise Exception('Please specify --outdir.')
        
    except Exception as e:
        print(e)
        sys.exit(1)
    
    outdir = os.path.realpath(options.outdir)
    exp_manager(options.config, outdir)
    
    
if __name__ == '__main__':
    main()
