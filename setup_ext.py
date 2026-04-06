"""
Build script for Cython extensions.

Usage:
    python setup_ext.py build_ext --inplace

This compiles the optional Cython extensions for logarithma.  If Cython or
a C compiler is not available the package still works via pure-Python fallback.
"""

from setuptools import setup, Extension

try:
    from Cython.Build import cythonize
    USE_CYTHON = True
except ImportError:
    USE_CYTHON = False

_ext_dir = "src/logarithma/algorithms/shortest_path"

if USE_CYTHON:
    extensions = cythonize(
        [
            Extension(
                "logarithma.algorithms.shortest_path.block_heap_cy",
                sources=[f"{_ext_dir}/block_heap.pyx"],
                language="c",
            ),
            Extension(
                "logarithma.algorithms.shortest_path.breaking_barrier_core",
                sources=[f"{_ext_dir}/breaking_barrier_core.pyx"],
                language="c",
            ),
        ],
        compiler_directives={
            "language_level": "3",
            "boundscheck": False,
            "wraparound": False,
            "cdivision": True,
        },
        annotate=False,
    )
else:
    extensions = []

setup(
    name="logarithma-ext",
    ext_modules=extensions,
)
