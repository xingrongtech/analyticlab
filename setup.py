# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 19:15:17 2018

@author: xingrongtech
"""

from distutils.core import setup

setup(name = 'analyticlab',
      version = '0.1.17',
      description='A library for experimental data calculation, treatment and display, which can be used for College Physics Experiment, Analytical Chemistry, etc.', 
      author = 'xingrongtech',
      author_email = 'wzv100@163.com',
      license='MIT License',
      install_requires = ['numpy', 'scipy', 'sympy'],
      packages=['analyticlab', 'analyticlab.lookup', 
                'analyticlab.system', 'analyticlab.uncertainty'],
      keywords=['calculation', 'analysis', 'display'],
      url='https://github.com/xingrongtech/analyticlab',
      classifiers=[
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
      ],
      )
