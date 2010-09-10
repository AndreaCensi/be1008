import numpy, os, fnmatch
from reprep import Node
from reprep.out.html import node_to_html_document
from reprep.out.platex import makecmd, Latex
from be1008.camera_figure import makelabel, write_graphics
from be1008.utils import my_pickle_load



def main():
    
    def find_in_path(path, pattern):
        for root, dirs, files in os.walk(path): #@UnusedVariable
            for f in files: 
                if fnmatch.fnmatch(f, pattern):
                    yield os.path.join(root, f)
               
    dir = 'Bicocca_2009-02-25a/out/camera_bgds_predict/gray_GI_DI/' 
    files = list(find_in_path(dir, '*.??.pickle*'))
    if not files:
        raise Exception('No files found.')
    

    for f in files:
        print 'Loading {0}'.format(f)
        data = my_pickle_load(f)
        basename, ext = os.path.splitext(f)
        out_html = basename + '/report.html'
        out_pickle = basename + '/report.pickle'

        if not os.path.exists(basename):
            os.makedirs(basename)
        
        logdir = data['logdir']
        time = data['time']
        y = data['y']
        y_dot = data['y_dot']
        y_dot_pred = data['y_dot_pred']
        y_dot_s = data['y_dot_s']
        y_dot_pred_s = data['y_dot_pred_s']
        
        report = Node('{logdir}-{time:.2f}'.format(logdir=logdir, time=time))
        prod = -numpy.minimum(0, y_dot_s * y_dot_pred_s)
        
        report.data('y', y)
        report.data('y_dot', y_dot)
        report.data('y_dot_pred', y_dot_pred)
        report.data('y_dot_s', y_dot_s)
        report.data('y_dot_pred_s', y_dot_pred_s)
        report.data('prod', prod)
        
        f = report.figure('display') 
        f.sub('y', display='rgb')
        f.sub('y_dot', display='posneg')
        f.sub('y_dot_pred', display='posneg')
        f.sub('y_dot_s', display='posneg')
        f.sub('y_dot_pred_s', display='posneg')
        f.sub('prod', display='scale')
        
        zones = [
                 ('ZoneA', range(95, 181), range(55, 140)),
                 ('ZoneB', range(80, 111), range(480, 510)),
                 ('ZoneC', range(50, 181), range(330, 460))
                ]
        
        for zone in zones:
            name, y, x = zone
            
            zr = report.node(name)
            zf = zr.figure()
            for var in ['y', 'y_dot', 'y_dot_pred', 'y_dot_s', 'y_dot_pred_s',
                        'prod']:
                zd = data[var][y, :][:, x]
                zr.data(var, zd)
                
                if var == 'y':
                    disp = {'display': 'rgb'}
                elif var == 'prod':
                    disp = {'display': 'scale'}
                else:
                    disp = {'display': 'posneg'}

                zf.sub(var, **disp)
        
            outdir = basename + '/' + name 
            id = "%s:%.2f:%s" % (logdir, time, name)
            print id
            create_latex_frag(outdir, zr, id)
        
        print 'Writing on %s' % out_html
        node_to_html_document(report, out_html)
        
        print 'Writing on %s' % out_pickle
        my_pickle_dump(report, out_pickle)
    
def create_latex_frag(outdir, report, id):
    if not os.path.exists(outdir):
        os.makedirs(outdir)
     
    frag_file = os.path.join(outdir, 'index.tex')
    graphics_path = outdir
    
    w1 = "2cm"
    with Latex.fragment(frag_file, graphics_path=graphics_path) as frag:
        
        with frag.figure(caption=makecmd(frag, id + 'demo'),
                         label=makelabel(id + ':demo')) as fig:
            fig.hfill()
            with fig.subfigure(caption=makecmd(frag, 'graysignal')) as sub:
                data = report.resolve_url('y/rgb')
                write_graphics(sub, data, w1)
            fig.hfill()
            with fig.subfigure(caption=makecmd(frag, 'graysignal_dot')) as sub:
                data = report.resolve_url('y_dot/posneg')
                write_graphics(sub, data, w1)
            fig.hfill()
            with fig.subfigure(caption=makecmd(frag, 'graysignal_dot_pred')) as sub:
                data = report.resolve_url('y_dot_pred/posneg')
                write_graphics(sub, data, w1)
            fig.hfill()
            with fig.subfigure(caption=makecmd(frag, 'graysignal_detect')) as sub:
                data = report.resolve_url('prod/scale')
                write_graphics(sub, data, w1)
            
        
    
    
    
    
        

