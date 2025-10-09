from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy as np

ext_modules = [
    Extension(
        "gravitation2",                 # import name
        ["gravitation2.pyx"],
        extra_compile_args=[],
        extra_link_args=[],
    )
]

ext_modules = [
    Extension(
        "collision_cy",
        ["collision_cy.pyx"],
        extra_compile_args=[],
        extra_link_args=[],
    )
]

setup(
    ext_modules=cythonize(ext_modules, language_level="3", annotate=False),
    include_dirs=[np.get_include()],
)
