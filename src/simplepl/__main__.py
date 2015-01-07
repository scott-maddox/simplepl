#
#   Copyright (c) 2013-2014, Scott J Maddox
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
#   License along with SimplePL.  If not, see
#   <http://www.gnu.org/licenses/>.
#
#######################################################################

# std lib imports
import logging
import argparse
import sys

# third party imports
from PySide import QtGui, QtCore

# local imports
if __name__ == '__main__':
    # Make sure we're importing the local simplepl package
    import os
    sys.path.insert(0,
        os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    import simplepl
    # This doesn't work with py2app:
    # assert os.path.dirname(simplepl.__file__) == os.path.dirname(__file__)
from simplepl.exception_handling import install_excepthook


def run(debug, simulate):
    # This is needed for pyqtgraph to function smoothly:
    QtGui.QApplication.setGraphicsSystem("raster")

    # Start the app
    app = QtGui.QApplication([])

    # Set up QSettings
    app.setOrganizationName("Scott J Maddox")
    app.setApplicationName("SimplePL")

    # Set up logging
    settings = QtCore.QSettings()
    settings.setValue('debug', int(debug))
    settings.setValue('simulate', int(simulate))
    settings.sync()
    if debug:
        logging.basicConfig(level=logging.DEBUG)
        log = logging.getLogger(__name__)
        log.debug('Logging enabled.')
        if simulate:
            log.debug('Simulating instruments.')
    install_excepthook()

    runner = AppRunner(debug, simulate)
    QtCore.QTimer.singleShot(0, runner.run)
    app.exec_()


def makeSplashLogo():
    '''Make a splash screen logo.'''
    border = 16
    xw, yw = 512 + 16, 512 + 16
    pix = QtGui.QPixmap(xw, yw)
    pix.fill()
    p = QtGui.QPainter(pix)

    # draw logo on pixmap
    logo = QtGui.QPixmap(QtGui.QImage('resources/icon_256.png'))
    p.drawPixmap(xw / 2 - logo.width() / 2, yw / 2 - logo.height() / 2, logo)
    p.end()
    return pix


class AppRunner(QtCore.QObject):
    '''
    QObject to run application. This provides an event loop, so we can
    have a splash screen while importing, etc.
    '''
    def __init__(self, debug, simulate):
        super(AppRunner, self).__init__()

        self.splash = QtGui.QSplashScreen(makeSplashLogo())
        self.splash.show()
        self.splash.raise_()
        self.splash.activateWindow()

    def run(self):
        from simplepl.main_window import MainWindow
        # Create main window
        self.w = MainWindow()
        self.splash.finish(self.w)
        self.w.show()
        self.w.raise_()
        self.w.activateWindow()

if sys.platform != 'win32':
    from single_process import single_process
    run = single_process(run)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--simulate', action='store_true')
    args = parser.parse_args()
    run(args.debug, args.simulate)
