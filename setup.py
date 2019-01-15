

# a bug workaround.  http://bugs.python.org/issue15881
try:
    import multiprocessing
except ImportError:
    pass

import setuptools
import ryu.hooks


ryu.hooks.save_orig()
setuptools.setup(name='ryu',
                 setup_requires=['pbr'],
                 pbr=True)
