#
#   Copyright (c) 2014, Scott J Maddox
#
#   This file is part of Plot Liberator.
#
#   Plot Liberator is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published
#   by the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   Plot Liberator is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with Plot Liberator.  If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

# std lib imports
import sys
import os.path

# third party imports
import glob
from setuptools import setup, find_packages

# read in __version__
exec(open('src/simplepl/version.py').read())


# If on Mac OS X, build an app bundle using py2app
if sys.platform == 'darwin':
    # extra arguments for mac py2app to associate files
    plist = dict(
                 CFBundleName='SimplePL',
                 CFBundleShortVersionString=__version__,
                 CFBundleIdentifier='org.python.simplepl',
                 )
    py2app_opts = dict(
                       argv_emulation=False,
                       includes=['PySide',
                                 'PySide.QtCore',
                                 'PySide.QtGui',
                                 'pyqtgraph',
                                 'scipy.interpolate',
                                 'single_process',
                                 'serial'],
                       excludes=['PySide.QtNetwork',
                                 'wxpython',
                                 'matplotlib',
                                 'zmq',
                                 'lib-dynload',
                                 'numpy.linalg',
                                 ],
                       plist=plist,
                       iconfile='src/simplepl/resources/icon.icns',
                       )
    extra_options = dict(
                         setup_requires=['py2app'],
                         app=['src/simplepl/main.py'],
                         options=dict(
                                      py2app=py2app_opts
                                      )
                         )
elif sys.platform == 'win32':
    extra_options = dict(
                         setup_requires=['py2exe'],
                         windows = [
                dict(script='with_gui.py',
                     icon_resources=[(1, 'src/simplepl/resources/icon.ico')])
                                    ]
                         )
else:
    extra_options = dict(
         # Normally unix-like platforms will use "setup.py install"
         # and install the main script as such
         scripts=['src/simplepl/main.py'],
     )

setup(name='simplepl',
      version=__version__,  # read from version.py
      description='a simple python gui for taking ' \
                  'photoluminescence (PL) spectra',
      long_description=open('README.rst').read(),
      url='http://scott-maddox.github.io/simplepl',
      author='Scott J. Maddox',
      author_email='smaddox@utexas.edu',
      license='AGPLv3',
      packages=['simplepl',
                'simplepl.dialogs',
                'simplepl.instruments',
                'simplepl.instruments.drivers',
                ],
      package_dir={'simplepl': 'src/simplepl'},
      zip_safe=True,
      **extra_options)
