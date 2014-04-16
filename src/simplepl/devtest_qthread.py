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
import time
import random

# third party imports
from PySide import QtCore, QtGui

# local imports


class WorkerThread(QtCore.QThread):
    
    _sigRequestData = QtCore.Signal()
    _sigRequestQuit = QtCore.Signal()
    
    sigData = QtCore.Signal(float)
    
    def __init__(self):
        super(WorkerThread, self).__init__()
        print self.currentThread(), 'WorkerThread.__init__', time.time()
        self._sigRequestData.connect(self._getData)
        self._sigRequestQuit.connect(self._Quit)
        self.moveToThread(self)
        self.start()
        
    
    def run(self):
        print self.currentThread(), 'WorkerThread.run', time.time()
        self.exec_()
    
    @QtCore.Slot()
    def _getData(self):
        print self.currentThread(), 'WorkerThread._getData', time.time()
        self.sleep(2)
        self.sigData.emit(random.random())
    
    def requestData(self):
        '''
        Sends a request to the worker thread to generate new data, and
        emit sigData.
        '''
        print self.currentThread(), 'WorkerThread.requestData', time.time()
        self._sigRequestData.emit()
    
    @QtCore.Slot()
    def _Quit(self):
        print self.currentThread(), 'WorkerThread._Quit', time.time()
        self.quit()
    
    def requestQuit(self):
        '''
        Sends a request to the worker thread to quit.
        '''
        print self.currentThread(), 'WorkerThread.requestQuit', time.time()
        self._sigRequestQuit.emit()

class MainWindow(QtGui.QMainWindow):
    
    sigRequestQuit = QtCore.Signal()
    
    def __init__(self):
        print QtCore.QThread.currentThread(), 'MainWindow.__init__', time.time()
        super(MainWindow, self).__init__()
        self.label = QtGui.QLabel('')
        self.setCentralWidget(self.label)
        self.show()
        self.activateWindow()
        self.raise_()
        
        self.worker = WorkerThread()
        self.worker.sigData.connect(self.slotNewData)
        self.sigRequestQuit.connect(self.worker.requestQuit)
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.timerTick)
        self.timer.start(5000)
        #TODO: see if a direct call works also
    
    def closeEvent(self, ev):
        print QtCore.QThread.currentThread(), 'MainWindow.closeEvent', time.time()
        self.worker.requestQuit()
        self.worker.wait()
    
    def timerTick(self):
        print QtCore.QThread.currentThread(), 'MainWindow.timerTick', time.time()
        print 'before', time.time()
        self.worker.requestData()
        print 'after', time.time()
    
    @QtCore.Slot(float)
    def slotNewData(self, data):
        print QtCore.QThread.currentThread(), 'MainWindow.slotNewData', time.time()
        self.label.setText('%.6f'%data)

app = QtGui.QApplication([])
w = MainWindow()
## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()