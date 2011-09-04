from collection import namedtuple

L = namedtuple('L', 'logname logdir configuration')

def list_logs(basedir):
    