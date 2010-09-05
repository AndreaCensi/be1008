import os
import fnmatch
import pickle
from procgraph.core.model_loadsave import make_sure_dir_exists
from reprep import Node
from reprep.out.html import node_to_html_document
import numpy
from procgraph.components.cv.opencv_utils import smooth



def memories_display():
    
    def find_in_path(path, pattern):
        for root, dirs, files in os.walk(path): #@UnusedVariable
            for f in files: 
                if fnmatch.fnmatch(f, pattern):
                    yield os.path.join(root, f)
               
               
    files = list(find_in_path('out/memories', '*.pickle'))
    if not files:
        raise Exception('No files found.')
    

    for f in files:
        print 'Loading {0}'.format(f)
        data = pickle.load(open(f))
        basename = 'out/memories_display/{logdir}/{time}'.format(**data)
        make_sure_dir_exists(basename)        
        
        report = Node('{logdir}-{time}'.format(**data))
        
        y = data['y']
        y_dot = data['y_dot']
        y_dot_pred = data['y_dot_pred']
        y_dot_s = data['y_dot_s']
        y_dot_pred_s = data['y_dot_pred_s']
        
        prod = -numpy.minimum(0, y_dot_s * y_dot_pred_s)
        # numpy.minimum(0, x) takes the negative part


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
        
        node_to_html_document(report, basename + '.html')
        
        
        

