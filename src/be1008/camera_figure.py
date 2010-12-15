from reprep.out.platex import Latex, makecmd

from .utils import my_pickle_load


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
        to be called by camera_bgds_boot    
    '''
    input1 = 'out/camera_bgds_boot/report.pickle'
    report = my_pickle_load(input1)
    #report.print_tree()
    
    camera_figures(report)
    
    
def camera_figures(report):
    output_pattern_conf = 'out/camera_figures/conf_{variant}.tex'
    output_pattern_rep = 'out/camera_figures/report_{variant}.tex'
    graphics_path = 'out/camera_figures/'
    
    summary = 'out/camera_figures/conf_summary.tex'
    with Latex.document(summary, document_class='ieeeconf',
                        graphics_path=graphics_path) as doc:
        for variant_report in report.children:
            doc.input('conf_' + variant_report.id)

    summary = 'out/camera_figures/report_summary.tex'
    with Latex.document(summary, document_class='article',
                        graphics_path=graphics_path) as doc:
        for variant_report in report.children:
            doc.input('report_' + variant_report.id)


    for variant_report in report.children:
        variant = variant_report.id 
        
        frag_file = output_pattern_conf.format(variant=variant)
        write_variant(frag_file, variant_report, variant, graphics_path, conference=True)

        frag_file = output_pattern_rep.format(variant=variant)
        write_variant(frag_file, variant_report, variant, graphics_path, conference=False)
        
        
def write_variant(frag_file, variant_report, variant, graphics_path, conference):
    if conference:
        w1 = "4cm" 
    else:
        w1 = "5.5cm"
    
    with Latex.fragment(frag_file, graphics_path=graphics_path) as frag:
        with frag.figure(caption=makecmd(frag, variant + 'StatsCaption'),
                         label=makelabel(variant + ':Stats'), double=True) as fig:
            fig.hfill()
            with fig.subfigure(caption=makecmd(frag, 'y_mean')) as sub:
                data = variant_report.resolve_url('y_mean/scale')
                write_graphics(sub, data, w1)
            fig.hfill()
            with fig.subfigure(caption=makecmd(frag, 'y_var')) as sub:
                data = variant_report.resolve_url('y_var/scale')
                write_graphics(sub, data, w1)
            fig.hfill()
            
            if not conference:
                fig.parbreak()
                fig.hfill()
            
            with fig.subfigure(caption=makecmd(frag, 'y_dot_var')) as sub:
                data = variant_report.resolve_url('y_dot_var/scale')
                write_graphics(sub, data, w1)
            fig.hfill()
            with fig.subfigure(caption=makecmd(frag, 'gx_var')) as sub:
                data = variant_report.resolve_url('gx_var/scale')
                write_graphics(sub, data, w1)
            fig.hfill()
#            with fig.subfigure(caption=makecmd(frag, 'gy_var')) as sub:
#                data = variant_report.resolve_url('gy_var/scale')
#                write_graphics(sub, data, w1)
#            fig.hfill()
#            
        if not conference:
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
    
                if not conference:
                    fig.parbreak()
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
            
            if not conference:
                fig.parbreak()
                fig.hfill()

            with fig.subfigure(caption=makecmd(frag, 'Gxa_norm')) as sub:
                data = variant_report.resolve_url('Gxa_norm/posneg')
                write_graphics(sub, data, w1)
            fig.hfill()
            with fig.subfigure(caption=makecmd(frag, 'Gya_norm')) as sub:
                data = variant_report.resolve_url('Gya_norm/posneg')
                write_graphics(sub, data, w1)
            fig.hfill() 

        print "ciaop"
          

