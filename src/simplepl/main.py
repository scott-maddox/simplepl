#
#   Copyright (c) 2013, Scott J Maddox
#
#   This file is part of SimplePL.
#
#   SimplePL is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   SimplePL is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public
#   License along with semicontrol.  If not, see
#   <http://www.gnu.org/licenses/>.
#
#######################################################################

# std lib imports
import logging
import argparse
import sys

# third party imports
from PySide import QtGui, QtCore
from single_process import single_process
# local imports
if __name__ == '__main__':
    # Make sure we're importing the local simplepl package
    import os
    sys.path.insert(0,
        os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    import simplepl
    assert os.path.dirname(simplepl.__file__) == os.path.dirname(__file__)
from simplepl.exception_handling import install_excepthook
from simplepl.main_window import MainWindow


@single_process
def run(debug, simulate):
    app = QtGui.QApplication([])

    # Set up QSettings
    app.setOrganizationName("Scott J Maddox")
    app.setApplicationName("SimplePL")

    # Set up logging
    settings = QtCore.QSettings()
    settings.setValue('debug', debug)
    settings.setValue('simulate', simulate)
    settings.sync()
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    install_excepthook()

    # Create main window
    w = MainWindow()
    w.show()
    w.activateWindow()
    w.raise_()

    app.exec_()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--simulate', action='store_true')
    args = parser.parse_args()
    run(args.debug, args.simulate)
