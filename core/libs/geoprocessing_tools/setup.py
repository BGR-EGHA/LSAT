import numpy
from distutils.core import setup
import setuptools
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("geoprocessing.pyx"),
    include_dirs=[numpy.get_include()]
)
