from procgraph import pg, register_model_spec
import os
from optparse import OptionParser


dirs = """
20100604/20100604_194126
20100604/20100604_200813
20100604/20100604_201538
20100604/20100604_202216
20100604/20100604_202246
20100604/20100604_202726
20100605/20100605_172139
20100605/20100605_172710
20100605/20100605_173337
20100605/20100605_173504
20100605/20100605_173833
20100615/20100615_184406
20100615/20100615_201500
20100615/20100615_202030
20100615/20100615_202107
20100615/20100615_202321
20100615/20100615_202916
20100615/20100615_203552
20100615/20100615_233658
20100615/20100615_234934
20100615/20100615_235829
20100615/20100616_000059
20100616/20100616_175627
20100616/20100616_182001
""".split()

register_model_spec('''
--- model er1convert
config logdir 
config outdir 

|npyread file="${logdir}/angular_velocity.npy"| --> angular_velocity
|npyread file="${logdir}/linear_velocity.npy"| --> linear_velocity

|npyread file="${logdir}/odometry.npy"| --> odometry
|npyread file="${logdir}/video0.npy"| --> video0
|npyread file="${logdir}/video1.npy"| --> video1

odometry, angular_velocity, linear_velocity --> \
    |hdfwrite file="${outdir}/small_data.h5"|
video0 --> |mencoder file="${outdir}/video0.avi"|
video1 --> |mencoder file="${outdir}/video1.avi"|

''')


register_model_spec('''
--- model er1convert_simpler
config logdir 
config outdir 

|npyread file="${logdir}/odometry.npy"| --> odometry
|npyread file="${logdir}/video0.npy"| --> video0
|npyread file="${logdir}/video1.npy"| --> video1

odometry --> \
    |hdfwrite file="${outdir}/small_data.h5"|
video0 --> |mencoder file="${outdir}/video0.avi"|
video1 --> |mencoder file="${outdir}/video1.avi"|

''')


def main():
    usage = 'Convert the old ER1 logs into the new format'
    
    parser = OptionParser(usage=usage)
    
    parser.add_option("--out", help="Destination base directory")
    
    (options, args) = parser.parse_args()
    

    if options.out is None:
        raise Exception('Please supply out')

    for logdir in  dirs:
        logname = os.path.basename(logdir)
        outdir = os.path.join(options.out, logname)
        done_file = os.path.join(outdir, 'finished.txt')
        if os.path.exists(done_file):
            print('Skipping %r' % logdir)
            continue

        try:
            pg('er1convert', dict(logdir=logdir, outdir=outdir))

            with open(done_file, 'w') as f:
                f.write('done :-)\n')
        except Exception as e:
            print e
            continue

if __name__ == '__main__':
    main()
    








