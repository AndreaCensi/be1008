import cPickle as pickle
from reprep.out.platex import Latex, latexify, makeupcmd


def write_graphics(frag, node, width, border=True):
    if border:
        frag.tex('\\setlength\\fboxsep{0pt}\\fbox{')
    frag.graphics_data(node.raw_data, node.mime, width=width, id=node.get_complete_id())
    
    if border:
        frag.tex('}')
    
def makelabel(name):
    name = name.replace('_', '')
    return name

def main():
    '''
    
    Reads:
    
     out/camera_bgds_boot/report.pickle
    
    Writes:
    
     out/camera_figures/<variant>.tex
    
    '''

    
    input1 = 'out/camera_bgds_boot/report.pickle'
    output_pattern = 'out/camera_figures/{variant}.tex'
    graphics_path = 'out/camera_figures/images'
    
    
    print "Loading %s" % input1
    report = pickle.load(open(input1))
    report.print_tree()
    
    w1 = "4cm"
    
    summary = output_pattern.format(variant='summary')
    with Latex.document(summary, document_class='ieeeconf', graphics_path=graphics_path) as doc:
        for variant_report in report.children:
            doc.input(variant_report.id)


    for variant_report in report.children:
        variant = variant_report.id    
        frag_file = output_pattern.format(variant=variant)

        variant = variant.replace('_', '')
        
        with Latex.fragment(frag_file, graphics_path=graphics_path) as frag:
            
            with frag.figure(caption=makecmd(frag, variant + 'GCaption'),
                             label=makelabel(variant + ':G'), double=True) as fig:
                fig.hfill()
                with fig.subfigure(caption=makecmd(frag, 'Gxl')) as sub:
                    data = variant_report.resolve_url('Gxl/posneg')
                    write_graphics(sub, data, w1)
                fig.hfill()
                with fig.subfigure(caption=makecmd(frag, 'Gyl')) as sub:
                    data = variant_report.resolve_url('Gyl/posneg')
                    write_graphics(sub, data, w1)
                fig.hfill()
                with fig.subfigure(caption=makecmd(frag, 'Gxa')) as sub:
                    data = variant_report.resolve_url('Gxa/posneg')
                    write_graphics(sub, data, w1)
                fig.hfill()
                with fig.subfigure(caption=makecmd(frag, 'Gya')) as sub:
                    data = variant_report.resolve_url('Gya/posneg')
                    write_graphics(sub, data, w1)
                fig.hfill()

            with frag.figure(caption=makecmd(frag, variant + 'GnormCaption'),
                             label=makelabel(variant + ':Gnorm'), double=True) as fig:
                fig.hfill()
                with fig.subfigure(caption=makecmd(frag, 'Gxl_norm')) as sub:
                    data = variant_report.resolve_url('Gxl_norm/posneg')
                    write_graphics(sub, data, w1)
                fig.hfill()
                with fig.subfigure(caption=makecmd(frag, 'Gyl_norm')) as sub:
                    data = variant_report.resolve_url('Gyl_norm/posneg')
                    write_graphics(sub, data, w1)
                fig.hfill()
                with fig.subfigure(caption=makecmd(frag, 'Gxa_norm')) as sub:
                    data = variant_report.resolve_url('Gxa_norm/posneg')
                    write_graphics(sub, data, w1)
                fig.hfill()
                with fig.subfigure(caption=makecmd(frag, 'Gya_norm')) as sub:
                    data = variant_report.resolve_url('Gya_norm/posneg')
                    write_graphics(sub, data, w1)
                fig.hfill() 
  
            with frag.figure(caption=makecmd(frag, variant + 'StatsCaption'),
                             label=makelabel(variant + ':Stats'), double=True) as fig:
                fig.hfill()
                with fig.subfigure(caption=makecmd(frag, 'y_dot_var')) as sub:
                    data = variant_report.resolve_url('y_dot_var/scale')
                    write_graphics(sub, data, w1)
                fig.hfill()
                with fig.subfigure(caption=makecmd(frag, 'gx_var')) as sub:
                    data = variant_report.resolve_url('gx_var/scale')
                    write_graphics(sub, data, w1)
                fig.hfill()
                with fig.subfigure(caption=makecmd(frag, 'gy_var')) as sub:
                    data = variant_report.resolve_url('gy_var/scale')
                    write_graphics(sub, data, w1)
                fig.hfill()
 
