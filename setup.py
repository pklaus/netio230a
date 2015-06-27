# -*- coding: utf-8 -*-

"""
Copyright (c) 2015, Philipp Klaus. All rights reserved.

License: GPLv3
"""

from distutils.core import setup

setup(name='netio230a',
      version = '1.1.9',
      description = 'Python package to control the Koukaam NETIO-230A',
      long_description = 'Python software to access the Koukaam NETIO-230A and NETIO-230B: power distribution units / controllable power outlets with Ethernet interface',
      author = 'Philipp Klaus',
      author_email = 'philipp.l.klaus@web.de',
      url = 'https://github.com/pklaus/netio230a',
      license = 'GPL3+',
      packages = ['netio230a'],
      scripts = ['scripts/netio230a_cli', 'scripts/netio230a_discovery', 'scripts/netio230a_fakeserver'],
      zip_safe = True,
      platforms = 'any',
      keywords = 'Netio230A Koukaam PDU',
      classifiers = [
          'Development Status :: 4 - Beta',
          'Operating System :: OS Independent',
          'License :: OSI Approved :: GPL License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
      ]
)


