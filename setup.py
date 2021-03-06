#!/usr/bin/python2
# -*- coding: utf-8 -*-
#
# This file is part of occmodel - See LICENSE.txt
#
VERSION = 1,1,0

import sys
import os
import glob
import shutil
import subprocess

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

def version_str():
    return str(VERSION)[1:-1].replace(', ', '.')

def build_libocc():
    subprocess.check_call('cd occmodel; make', shell=True)

class OCCBuild(build_ext):
    def run(self):
        build_libocc()
        build_ext.run(self) 

# create config file
sys.dont_write_bytecode = True

CONFIG = 'occmodel/src/Config.pxi'
if not os.path.exists(CONFIG) and 'sdist' not in sys.argv:
    with open(CONFIG, 'w') as fh:
        fh.write("__version__ = '%s'\n" % version_str())
        fh.write("__version_info__ = (%d,%d,%d)\n" % VERSION)

OCC = \
'''FWOSPlugin PTKernel TKAdvTools TKBO TKBRep TKBinL TKBool TKCDF TKFeat TKFillet
TKG2d TKG3d TKGeomAlgo TKGeomBase TKHLR TKIGES TKLCAF TKMath TKMesh TKOffset
TKPLCAF TKPShape TKPrim TKSTEP TKSTEP209 TKSTEPAttr TKSTEPBase TKSTL TKShHealing
TKShapeSchema TKStdLSchema TKTObj TKTopAlgo TKXMesh TKXSBase TKXmlL TKernel
'''

# platform specific settings
SOURCES = ["occmodel/occmodel.pyx"]

OBJECTS, LIBS, LINK_ARGS, COMPILE_ARGS = [],[],[],[]
if sys.platform == 'win32':
    COMPILE_ARGS.append('/EHsc')
    OCCINCLUDE = r"C:\vs9include\oce"
    OCCLIBS = []
    OBJECTS = [name + '.lib' for name in OCC.split()] + ['occmodel.lib',]
    
elif sys.platform == 'darwin':
    SOURCES += glob.glob("occmodel/src/*.cpp")
    OCCINCLUDE = '/usr/include/oce'
    OCCLIBS = OCC.split()
    COMPILE_ARGS.append("-fpermissive")
    
else:
    OCCINCLUDE = '/usr/include/oce'
    OCCLIBS = OCC.split()
    OBJECTS = ["occmodel/liboccmodel.a"]
    COMPILE_ARGS.append("-fpermissive")

EXTENSIONS = [
    Extension("geotools",
              sources = ["occmodel/geotools/geotools.pyx",],
              depends = glob.glob("occmodel/geotools/*.pxi") + \
              glob.glob("occmodel/geotools/*.pxd") + \
              glob.glob("occmodel/geotools/*.h"),
              include_dirs = ['occmodel/geotools/',],
          ),
    Extension("occmodel",
              sources = SOURCES,
              depends = glob.glob("occmodel/src/*.pxd") + glob.glob("occmodel/src/*.pxi"),
              include_dirs       = ['occmodel/src', OCCINCLUDE],
              library_dirs       = ['/lib/','occmodel'],
              libraries          = LIBS + OCCLIBS,
              extra_link_args    = LINK_ARGS,
              extra_compile_args = COMPILE_ARGS,
              extra_objects = OBJECTS,
              language="c++"
          )
]

classifiers = '''\
Development Status :: 4 - Beta
Environment :: MacOS X
Environment :: Win32 (MS Windows)
Environment :: X11 Applications
Intended Audience :: Science/Research
License :: OSI Approved :: GNU General Public License v2 (GPLv2)
Operating System :: OS Independent
Programming Language :: Cython
Topic :: Scientific/Engineering
'''

setup(
    name             = 'occmodel',
    version          = version_str(),
    description      = 'Easy access to the OpenCASCADE library',
    long_description =  \
    '''**occmodel** is a small library which gives a high level access
    to the OpenCASCADE modelling kernel.

    For most users a direct use of the OpenCASCADE modelling
    kernel can be quite a hurdle as it is a huge library.

    The geometry can be visualized with the included viewer.
    This viewer is utilizing modern OpenGL methods like GLSL
    shaders and vertex buffers to ensure visual quality and
    maximum speed. To use the viewer OpenGL version 2.1 is
    needed.

    In order to complete the installation OpenCASCADE must be installed
    on the system. Check the home page or the README file for details.
    ''',
    classifiers  = [value for value in classifiers.split("\n") if value],
    author       = 'Runar Tenfjord',
    author_email = 'runar.tenfjord@gmail.com',
    license      = 'GPLv2',
    download_url = 'http://pypi.python.org/pypi/occmodel/',
    url          = 'http://github.com/tenko/occmodel',
    platforms    = ['any'],
    ext_modules  = EXTENSIONS,
    cmdclass     = {'build_ext': OCCBuild}
)
