# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 19:15:17 2018

@author: xingrongtech
"""

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="analyticlab",
    version="0.3.1-dev2",
    author="xingrongtech",
    author_email="wzv100@163.com",
    description="A library for experimental data calculation, treatment and display, which can be used for College Physics Experiment, Analytical Chemistry, etc.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xingrongtech/analyticlab",
    install_requires = ['numpy', 'scipy', 'sympy', 'quantities'],
    keywords=['calculation', 'analysis', 'measure', 'uncertainty', 'display'],
    packages=['analyticlab', 'analyticlab.lookup', 
              'analyticlab.system', 'analyticlab.measure'],
    license='MIT License',
    classifiers=(
              'Development Status :: 4 - Beta',
              'Operating System :: OS Independent',
              'Intended Audience :: Developers',
              'License :: OSI Approved :: BSD License',
              'Programming Language :: Python',
              'Programming Language :: Python :: Implementation',
              'Programming Language :: Python :: 3.4',
              'Programming Language :: Python :: 3.5',
              'Programming Language :: Python :: 3.6',
              'Topic :: Software Development :: Libraries'
    ),
)
