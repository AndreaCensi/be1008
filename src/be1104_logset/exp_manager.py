from optparse import OptionParser
import yaml
import os 
import sys
import glob

import procgraph
from procgraph.core.registrar import default_library
from procgraph.core.model_loader import pg_look_for_models
from procgraph.block_utils.file_io import make_sure_dir_exists

def model_info(block_type, library=default_library):
    gen = library.get_generator_for_block_type(block_type)
    return gen

def block_name_config(x):
    model = x['model']
    if isinstance(model, list): # [model, {args}]
        return model[0], model[1]
    else: 
        return model, {}


def names(signals):
    return [x.name for x in signals]
    

    
def block_name_from_conf(x):
    model = x['model']
    if isinstance(model, list): # [model, {args}]
        return model[0]
    else: return model


def exp_run(config):
    outdir = config['outdir']
    source = config['source']
    pres = config['presentation']
    
    def get_source_signals():
        gen = model_info(block_name_from_conf(source['play'][0]))
        return names(gen.output) 
    
    def get_pres_signals():
        gen = model_info(block_name_from_conf(pres))
        return names(gen.input), names(gen.output) 
        
    # let's find the source signals
    source_out = get_source_signals()
    pres_in, pres_out = get_pres_signals()
    
    for x in pres_in:
        if not x in source_out:
            msg = 'Signal %r not found in %r.' % (x, source_out)
            raise Exception(msg)
    
    print('Info about %r' % config['id'])
    print('- source %r has signals: %r' % (source['id'], source_out))
    print('-   pres %r has signals: %r, %r' % (pres['id'], pres_in, pres_out))
        
    M = create_source_model(source)
    filename = os.path.join(outdir, '%s.pg' % source['id'])
    make_sure_dir_exists(filename)
    with open(filename, 'w') as f:
        f.write(M) 


    signals_so_far = list(pres_out) + list(source_out)
    serialization = []
    for i, stage in enumerate(config['stages']):
        block = block_name_from_conf(stage)
        gen = model_info(block)
        inputs, outputs = names(gen.input), names(gen.output)
        
        for x in inputs:
            if not x in pres_out:
                msg = 'Signal %r not found in %r.' % (x, pres_out)
                raise Exception(msg)
        
        signals_so_far.extend(outputs)
        print(' * stage %d ' % i)
        print('    - block %r has signals %r %r' % (block, inputs, outputs))
        
      

def create_source_model(source):
    model_name = source['id']
    M = """--- model %s\n\n""" % model_name

    gen = model_info(block_name_from_conf(source['play'][0]))
    source_out = names(gen.output)

    for s in source_out:
        M += 'output %s \n' % s
        
    M += '\n'
        
    def model_string(name, block_type, config):
        params = " ".join(['%s=%r' % (k, v) for (k, v) in config.items()])
        return '|%s:%s %s|' % (name, block_type, params)
        
    for n, log in enumerate(source['play']):
        btype, bconfig = block_name_config(log)
        M += model_string('source%d' % n, btype, bconfig) + '\n'
        
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
           
#    results = {}
#    for d, f in itertools.product(data, filters):
#        source = d['source']
#        presentation = d['presentation']
#        
#        filter_name = f['model']
#         
#        key = (source, presentation, filter_name)
#        results[key] = comp(exp_run, source, presentation, f)
#        
#    for d, f, a in itertools.product(data, filters):
        
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
    
    exp_manager(options.config, options.outdir)
    
    
if __name__ == '__main__':
    main()
