# setup.py
# Build configuration for the ZEGA proprietary funct C-extension module
# Requires: NumPy, OpenMP-enabled compiler (e.g., gcc with -fopenmp), AVX2 support

import numpy
from setuptools import setup, Extension

funct_module = Extension(
    name="funct",
    sources=["main.cpp"],
    include_dirs=[numpy.get_include()],
    extra_compile_args=[
        "-O3",
        "-march=native",
        "-fopenmp",
        "-mavx2",
        "-mfma",
        "-ffast-math",
        "-std=c++17"
    ],
    extra_link_args=["-fopenmp"],
    language="c++",
    define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]
)

setup(
    name="zega_funct",
    version="1.0.0",
    author="ZEGA MegaHQ Engineering",
    description="ZEGA Proprietary High-Performance Spreadsheet Engine — Excel Killer",
    long_description="Monolithic C++ engine with OpenMP, AVX-256, and advanced algorithms.",
    ext_modules=[funct_module],
    zip_safe=False,
    python_requires=">=3.8",
)