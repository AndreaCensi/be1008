from procgraph.core.model_loadsave import make_sure_dir_exists
from collections import namedtuple
import os, math, sys, yaml

from docutils.core import publish_string #@UnresolvedImport

from httplib import HTTP 
from urlparse import urlparse 
from .procgraph_intersphinx import get_known_blocks

def rst2htmlfragment(text):
    html = publish_string(
           source=text,
           writer_name='html')
    html = html[html.find('<body>') + 6:html.find('</body>')].strip()
    return html

def URL_exists(url): 
    
    verbose = False
    
    ''' Checks that a URL exists (answer != 404) and returns the size.
    
    Returns None if does not exists, the size in bytes otherwise.
     ''' 
    if verbose:
        sys.stderr.write('Checking %s ' % url)
     
    p = urlparse(url) 
    h = HTTP(p[1]) 
    h.putrequest('HEAD', p[2]) 
    h.endheaders() 
    
    code, status, message = h.getreply() #@UnusedVariable

    if verbose:
        sys.stderr.write('\t%d\n' % code)
    
    
    if code == 404: 
        return None
    else: 
        return int(message['content-length'])

   
Video = namedtuple('Video', 'id title long_desc path model') 

def main():
    
    block2url = get_known_blocks()

    
    yaml_file = sys.argv[1]
    
    config = yaml.load(open(yaml_file)) 
     

    
    data_url_prefix = config['data_url_prefix']
    desc_url_prefix = config['desc_url_prefix']
    out_latex_commands = config['out_latex_commands']
    out_latex_commands_test = config['out_latex_commands_test']
    out_html = config['out_html']
    out_html_header = config['header']
    logs = config['logs']
    
    videos = []
    for entry in config['videos']:
        id = entry['id']
        title = entry['short']
        long = entry['long']
        path = entry['path']
        model = entry['model']
#        title = 'Video %s' % id
#        url = data_url_prefix + '/Bicocca_2009-02-26a/out/' + partial_url
#        desc_url = desc_url_prefix + '#' + id
        videos.append(Video(id, title, long, path, model))
        
    
    make_sure_dir_exists(out_latex_commands)
    
    print "Writing on %s" % out_latex_commands
    f = open(out_latex_commands, 'w')
    for video in videos:
        cmd_name = 'Ref' + video.id
        desc_url = desc_url_prefix + '#' + id
        url = desc_url.replace('#', '\\#')
        #title = video.title
        title = url[0:]
        cmd_body = """%%
        \\href{%s}{\\texttt{\\footnotesize video:%s}}\\footnote{ \\href{%s}{%s} } %% 
        """ % (url, video.id, url, title)
        f.write('\\newcommand{\\%s}{%%\n%s%%\n}\n' % (cmd_name, cmd_body))

    print "Writing on %s" % out_latex_commands_test
    f = open(out_latex_commands_test, 'w')
    f.write("""
    \\documentclass{ieeeconf}
    \\usepackage{hyperref}
    \\input{%s}
    \\begin{document}
    
    """ % os.path.basename(out_latex_commands))
    for video in videos:
        cmd_name = 'Ref' + video.id
        cmd = "\\%s" % cmd_name
        f.write('Look at this%s.\n\n' % cmd)
    f.write('\\end{document}\n')


    print "Writing on %s" % out_html
    f = open(out_html, 'w')
    
    f.write("""
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
      <html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
        <head>
        <title>Supplemental videos for bootstrapping paper.</title>
        <script type="text/javascript" src="flowplayer-3.2.4.min.js"></script>
        <style type="text/css">
        body {
            padding-top: 2em;
            padding-left: 3em;
            font-family: Georgia, Verdana, Arial, serif;
            font-size: 16px;
        }
        div.video {
            clear: both;
            padding: 1em;
        }
        .video h2 {
            padding-top: 2em;
            border-bottom: solid 2px black;
        }
        .video .others {
        margin-left: 1em;
        }
        
        .video .generated { clear: both; }
        
        .video .widget {
            float:left; display:block; width:520px; height:330px;
            background-color: #aad;
            margin: 1em;
        }
        
        .video A.play {
            font-weight: bold;
            color: red;
            margin-right: 2em;
            margin-left: 2em;
            text-decoration: none !important;
        }
        
        body  P { max-width: 50em }
        
        </style>
        </head>
        <body> 
         
    """)
    
    f.write(out_html_header)

    for video in videos:
        id = video.id
        title = video.title
        model = video.model
        
        has_desc = video.long_desc[0] != 'o'
        desc = rst2htmlfragment(video.long_desc) if has_desc else "" 
        
        f.write('''
        <div class="video">
        <h2 id="{id}">{id} - {title}</h2>
        
         {desc} 
        
        <a  class="widget"  id = "Anchor{id}" > </a> 

        '''.format(**locals()))
        
        f.write('''
            <div class='others'>
            
        ''')
        found = False
        for log in logs:
            url = data_url_prefix + '/' + log + '/out/' + video.path
            
            
            f.write('%s ' % log)
            
            size_bytes = URL_exists(url) 
            if size_bytes is not None:
                size = math.ceil(size_bytes / (10.0 ** 6))
                
                play_string = '''flowplayer("Anchor{id}", "flowplayer-3.2.4.swf",{{'''\
                '''clip: {{ scaling: "fit", url:"{url}"}} }});''' .format(**locals())      
                
                target = '#%s' % id
                f.write("<a class='play' href='%s' onclick='%s'> play </a> " % 
                        (target, play_string))
           
                f.write(' <a class="download" href="%s"> download (%dMB mp4) </a> ' % 
                        (url, size))
                
                found = True
            else:
                f.write('<span class="missing"> not generated </span>')
                
            
            f.write('<br/>\n')
            
        if not found:
            print 'Warning, no files for ', video.path
        
        f.write('''</div>''')
        
        if model in block2url:
            model_url = block2url[model]
            f.write(''' <p class='generated'> Generated by model <a href='%s'>%s</a>. </p> ''' % 
                    (model_url, model))
            #sys.stderr.write('Found %s %s\n' % (model, model_url)) 
        else:
            sys.stderr.write('No model ref found for %s\n' % model)
        
        f.write('''</div>''')
    
    f.write('</body></html>')
