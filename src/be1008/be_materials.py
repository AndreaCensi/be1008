from procgraph.core.model_loadsave import make_sure_dir_exists
from collections import namedtuple
import os


PREFIX = ''
url_prefix = 'http://www.cds.caltech.edu/~andrea/pub/research/2010-be/'
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
RGB                            camera_display/rgb.mp4                        rawseeds_camera_display
RGBMean                        camera_mean/mean.mp4                          rawseeds_camera_mean
Gray                           camera_display/gray.mp4                       rawseeds_camera_display
GrayDeriv                     camera_display/gray_dot.mp4                   rawseeds_camera_display
GrayVar                       camera_var/var.mp4                            rawseeds_camera_mean
Contrast                       camera_display/contrast.mp4                   rawseeds_camera_display_contrast
ContrastDeriv                 camera_display/contrast_dot.mp4               rawseeds_camera_display_contrast
ContrastMean                  camera_mean_contrast/mean.mp4                 rawseeds_camera_mean_contrast
ContrastVar                   camera_var_contrast/var.mp4                   rawseeds_camera_var_contrast
GrayIdIdLearningSignal     camera_bgds_boot/gray/GI_DI/tensors_k.mp4     rawseeds_camera_bgds_boot_all
GrayIdIdLearningResult    camera_bgds_boot/gray/GI_DI/tensors.mp4       rawseeds_camera_bgds_boot_all
GrayIdIdPrediction        camera_bgds_predict/gray_GI_DI/y_dot.mp4      rawseeds_camera_bgds_predict_all
GrayIdIdError             camera_bgds_predict/gray_GI_DI/prod.mp4       rawseeds_camera_bgds_predict_all
GrayIdIdErrorStats       camera_bgds_predict/gray_GI_DI/prod_stats.mp4 rawseeds_camera_bgds_predict_all
GraySSLearningSignal   camera_bgds_boot/gray/GS_DS/tensors_k.mp4     rawseeds_camera_bgds_boot_all
GraySSLearningResult   camera_bgds_boot/gray/GS_DS/tensors.mp4       rawseeds_camera_bgds_boot_all
GraySSPrediction        camera_bgds_predict/gray_GS_DS/y_dot.mp4      rawseeds_camera_bgds_predict_all
GraySSError             camera_bgds_predict/gray_GS_DS/prod.mp4       rawseeds_camera_bgds_predict_all
GraySSErrorStats       camera_bgds_predict/gray_GS_DS/prod_stats.mp4 rawseeds_camera_bgds_predict_all
LaserDisplay                  laser_display/sick.mp4                        rawseeds_laser_display
LaserPrediction        laser_bgds_predict/II_fps6_smooth8/movie.mp4            rawseeds_laser_bgds_predict
LaserCorr                     laser_corr/corr.mp4                           rawseeds_laser_corr
"""

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
        \\footnote{ \\href{%s}{%s} } %% 
        """ % (url, title)
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
        </style>
        </head>
        <body>
        <h1> Supplemental videos </h1>

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
        <a  
             href = "{video_url}"  
             style = "float:left; display:block;width:520px;height:330px"  
             id = "Anchor{id}" > 
        </a> 
    
        <script> 
            flowplayer("Anchor{id}", "flowplayer-3.2.4.swf",{{
    clip: {{
        autoPlay: false        // aplies to all Clips in the playlist
        }} }}
    );
        </script> 
        '''.format(**locals()))
        
        f.write('''
            <div class='others'>
            
        ''')
        for log in logs:
            url = data_url_prefix + '/' + log + '/out/' + video.partial_url
            f.write(' <a href="%s"> %s (.mp4) </a> <br/>' % (url, log))
        
        f.write('''
            </div>
        ''')
    
        f.write('''
            </div>
        ''')

    f.write('</body></html>')
