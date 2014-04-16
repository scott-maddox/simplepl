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
import logging; log = logging.getLogger(__name__)
import random

# third party imports
import numpy as np
import pyqtgraph as pg
from PySide import QtCore, QtGui

# local imports
from expanding_buffer import ExpandingBuffer
from spectra_pro_2500i import SpectraPro2500i
from srs_sr830 import SR830


#QtGui.QApplication.setGraphicsSystem('raster')
app = QtGui.QApplication([])
#mw = QtGui.QMainWindow()
#mw.resize(800,800)

# Use black text on white background
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

# Create the graphics window
win = pg.GraphicsWindow(title='SimplePL')
win.setWindowTitle('SimplePL')
win.resize(1000,600)
#win.center()
win.show()
win.activateWindow()
win.raise_() # just to be sure it's on top


plt = win.addPlot()
plt.setLabel('left', "Intensity", units='V')
plt.setLabel('bottom', "Wavelength (nm)")
curve = plt.plot(pen='b')
i = 2600
x = ExpandingBuffer(initial_size=10, dtype=np.int)
y = ExpandingBuffer(initial_size=10, dtype=np.float32)
def update():
    global i
    i += 10
    x.append(i)
    y.append(random.random()*1e-6)
    curve.setData(x.get(), y.get())
timer = QtCore.QTimer()
timer.timeout.connect(update)
update_rate = 100 # Hz
timer.start(1000./update_rate)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()