from procgraph.core.model_loadsave import make_sure_dir_exists
from collections import namedtuple
import os
import math

from httplib import HTTP 
from urlparse import urlparse 
import sys

def URL_exists(url):
    verbose = True
    
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


PREFIX = ''
# used to verify files exist
#local_url = '/Volumes/nessa 1/public_html/pub/research/2010-bevideos/'
data_url_prefix = 'http://www.cds.caltech.edu/~andrea/pub/research/2010-bevideos/'
desc_url_prefix = 'http://purl.org/censi/2010/be'
outdir = 'out/be_materials'
out_latex_commands = '%s/video_ref.tex' % outdir
out_latex_commands_test = '%s/video_ref_test.tex' % outdir
out_html = '%s/be_materials.html' % outdir



logs = """
Bicocca_2009-02-25a
Bicocca_2009-02-25b
Bicocca_2009-02-26a
Bicocca_2009-02-26b
Bicocca_2009-02-27a
Bovisa_2008-09-01
Bovisa_2008-10-04
Bovisa_2008-10-06
Bovisa_2008-10-07
Bovisa_2008-10-11a
Bovisa_2008-10-11b
""".split()

# http://juliensimon.blogspot.com/2009/01/howto-ffmpeg-x264-presets.html

data = """
LaserDisplay                   laser_display/sick.mp4                        rawseeds_laser_display
LaserCorr                      laser_corr/corr.mp4                           rawseeds_laser_corr
LaserBDSLearning               laser_bds_boot/movie.mp4                           rawseeds_laser_corr
RGB                            camera_display/rgb.mp4                        rawseeds_camera_display
RGBMean                        camera_mean/mean.mp4                          rawseeds_camera_mean
Gray                           camera_display/gray.mp4                       rawseeds_camera_display
GrayDeriv                      camera_display/gray_dot.mp4                   rawseeds_camera_display
GrayVar                        camera_var/var.mp4                            rawseeds_camera_mean
Contrast                       camera_display_contrast/contrast.mp4                   rawseeds_camera_display_contrast
ContrastDeriv                  camera_display_contrast/contrast_dot.mp4               rawseeds_camera_display_contrast
ContrastMean                   camera_mean_contrast/mean.mp4                 rawseeds_camera_mean_contrast
ContrastVar                    camera_var_contrast/var.mp4                   rawseeds_camera_var_contrast
GrayIdIdLearningSignal         camera_bgds_boot/gray/GI_DI/tensors_k.mp4     rawseeds_camera_bgds_boot_all
GrayIdIdLearningResult         camera_bgds_boot/gray/GI_DI/tensors.mp4       rawseeds_camera_bgds_boot_all
GrayIdIdPrediction             camera_bgds_predict/gray_GI_DI/y_dot.mp4      rawseeds_camera_bgds_predict_all
GrayIdIdError                  camera_bgds_predict/gray_GI_DI/prod.mp4       rawseeds_camera_bgds_predict_all
GrayIdIdErrorStats             camera_bgds_predict/gray_GI_DI/prod_stats.mp4 rawseeds_camera_bgds_predict_all
ContrastSSLearningSignal       camera_bgds_boot/contrast/GS_DS/tensors_k.mp4     rawseeds_camera_bgds_boot_all
ContrastSSLearningResult       camera_bgds_boot/contrast/GS_DS/tensors.mp4       rawseeds_camera_bgds_boot_all
ContrastSSPrediction           camera_bgds_predict/contrast_GS_DS/y_dot.mp4      rawseeds_camera_bgds_predict_all
ContrastSSError                camera_bgds_predict/contrast_GS_DS/prod.mp4       rawseeds_camera_bgds_predict_all
ContrastSSErrorStats           camera_bgds_predict/contrast_GS_DS/prod_stats.mp4 rawseeds_camera_bgds_predict_all
LaserSSLearningResult          laser_bgds_boot/GS_DS/movie.mp4 rawseeds_laser_bgds_boot
LaserIdIdLearningResult        laser_bgds_boot/GI_DI/movie.mp4 rawseeds_laser_bgds_boot
LaserPrediction                laser_bgds_predict/II_fps6_smooth8/movie.mp4            rawseeds_laser_bgds_predict
"""
#GraySSLearningSignal   camera_bgds_boot/gray/GS_DS/tensors_k.mp4     rawseeds_camera_bgds_boot_all
#GraySSLearningResult   camera_bgds_boot/gray/GS_DS/tensors.mp4       rawseeds_camera_bgds_boot_all
#GraySSPrediction        camera_bgds_predict/gray_GS_DS/y_dot.mp4      rawseeds_camera_bgds_predict_all
#GraySSError             camera_bgds_predict/gray_GS_DS/prod.mp4       rawseeds_camera_bgds_predict_all
#GraySSErrorStats       camera_bgds_predict/gray_GS_DS/prod_stats.mp4 rawseeds_camera_bgds_predict_all

Video = namedtuple('Video', 'id title desc_url url script partial_url') 

def main():
    
    videos = []
    for line in data.split('\n'):
        if not line: continue
        id, partial_url, script = line.split()
        title = 'Video %s' % id
        url = data_url_prefix + '/Bicocca_2009-02-26a/out/' + partial_url
        desc_url = desc_url_prefix + '#' + id
        id = PREFIX + id
        videos.append(Video(id, title, desc_url, url, script, partial_url))
        
    
    make_sure_dir_exists(out_latex_commands)
    
    print "Writing on %s" % out_latex_commands
    f = open(out_latex_commands, 'w')
    for video in videos:
        cmd_name = 'Ref' + video.id
        url = (video.desc_url).replace('#', '\\#')
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
        <html>
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
        
        .video .widget {
            float:left; display:block; width:520px; height:330px;
            background-color: gray;
            margin: 1em;
        }
        
        .video A.play {
            font-weight: bold;
            color: red;
            margin-right: 2em;
            margin-left: 2em;
            text-decoration: none !important;
        }
        
        </style>
        </head>
        <body>
        <h1> Supplemental videos  </h1>

        <p> This page describes the supplemental videos for a couple 
            of recent papers on bootstrapping, as well as more recent
            work and experiments. </p>
        
        <p> See <a href="http://purl.org/censi/2010/boot">http://purl.org/censi/2010/boot</a>
            for more information and pointers to the source code. </p>
        
        <h3> Videos format </h3>
        
        <p> The videos are in .mp4 format with x264 encoding. They should 
            play on any recent player, so let us know if it doesn't work for you. 
        </p>
        
        <p> Players that are known to work include: MPlayer, VLC, Quicktime. </p>
        
        <p>
            Note that most of these videos are very large (hundreds of MBs).
            A flash widget is included as well.
        </p> 
    
        
         
    """)

    for video in videos:
        video_url = video.url
        id = video.id
        f.write('''
        <div class="video">
        <h2 id="{id}">{id}</h2>
        
        
        <a  class="widget"  id = "Anchor{id}" > </a> 

        '''.format(**locals()))
        
        f.write('''
            <div class='others'>
            
        ''')
        found = False
        for log in logs:
            url = data_url_prefix + '/' + log + '/out/' + video.partial_url
            
            
            play_string = '''javascript:flowplayer("Anchor{id}", "flowplayer-3.2.4.swf",{{'''\
                '''clip: {{ url:"{url}"}} }});''' .format(**locals())
                      
            f.write('%s ' % log)
            
            #local_file = local_url + '/' + log + '/out/' + video.partial_url
            #print local_file
            size_bytes = URL_exists(url) 
            if size_bytes is not None:
                size = math.ceil(size_bytes / (10.0 ** 6))
                
                target = '#%s' % id
                f.write("<a class='play' href='%s' OnClick='%s'> play </a> " % 
                        (target, play_string))
           
                f.write(' <a class="download" href="%s"> download (%dMB mp4) </a> ' % 
                        (url, size))
                
                found = True
            else:
                f.write('<span class="missing"> not generated </span>')
                
            
            f.write('<br/>\n')
            
        if not found:
            print 'Warning, no files for ', video.partial_url
        
        f.write('''
            </div>
        ''')
    
        f.write('''
            <p class='instructions'>  Click "play" on the right to play the video with a flash widget,
            or right-click "download" for the direct link to the .mp4 file. </p>
        
            </div>
        ''')

    f.write('</body></html>')
