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
import sys
import os.path
from itertools import izip

# third party imports
from PySide import QtGui, QtCore

# local imports
if __name__ == '__main__':
    sys.path.insert(0,
        os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    import simplepl
from simplepl.simple_pl_parser import SimplePLParser


class GenerateVeuszFileDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(GenerateVeuszFileDialog, self).__init__(parent)
        self.setWindowTitle('Generate Veusz File')
        self.setModal(True)

        # Get a settings object
        self.settings = QtCore.QSettings()

        # Generate and Cancel buttons
        generateButton = QtGui.QPushButton('Generate Veusz File')
        cancelButton = QtGui.QPushButton('Cancel')

        # Scroll area for the SpectrumWidgets
        self.tableWidget = QtGui.QTableWidget(1, 2)
        self.tableWidget.setHorizontalScrollMode(
                                    QtGui.QAbstractItemView.ScrollPerPixel)
        self.tableWidget.setHorizontalHeaderLabels(['Data Prefix',
                                                    'File Path'])
        self.tableWidget.setVerticalHeaderLabels(['+'])

        # Connect signals and slots
        self.tableWidget.cellDoubleClicked.connect(
                                              self._handleCellDoubleClicked)
        self.tableWidget.cellChanged.connect(self._handleCellChanged)
        generateButton.clicked.connect(self._generateVeuszFile)
        cancelButton.clicked.connect(self.close)

        # Layout
        buttonsLayout = QtGui.QHBoxLayout()
        buttonsLayout.addStretch(1)
        if sys.platform == 'darwin':
            buttonsLayout.addWidget(cancelButton)
            buttonsLayout.addWidget(generateButton)
        else:
            buttonsLayout.addWidget(generateButton)
            buttonsLayout.addWidget(cancelButton)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(QtGui.QLabel('Double-click on a cell to add PL '
                                      'files:'))
        layout.addWidget(self.tableWidget, stretch=1)
        layout.addLayout(buttonsLayout)
        self.setLayout(layout)

    def _handleCellDoubleClicked(self, row, column):
        if column != 1:
            return

        if row == (self.tableWidget.rowCount() - 1):
            self._appendFilePathItems()
        else:
            self._setFilePathItem(row)

    def _handleCellChanged(self, row, column):
        if column == 0 and row == (self.tableWidget.rowCount() - 1):
            # If the last prefix is changed, add a row to the end, and
            # prompt the user to select a file
            item = self.tableWidget.takeItem(row, column)
            self.tableWidget.insertRow(row)
            self.tableWidget.setItem(row, 0, item)
            self._setFilePathItem(row)

    def _getPLFilePath(self):
        '''Prompts the user to select one PL file to add'''
        dirpath = self.settings.value('last_open_directory', '')
        caption = 'Select a PL file to add...'
        pl_filepath, _filter = QtGui.QFileDialog.getOpenFileName(
                                                            parent=self,
                                                            caption=caption,
                                                            dir=dirpath,
                                                            filter='',
                                                            selectedFilter='',
                                                            options=0)
        if not pl_filepath or not self._validatePLFilePath(pl_filepath):
            self.raise_()
            self.activateWindow()
            return
        dirpath, _filename = os.path.split(pl_filepath)
        self.settings.setValue('last_open_directory', dirpath)

        return pl_filepath

    def _getPLFilePaths(self):
        '''Prompts the user to select one or more PL files to add'''
        dirpath = self.settings.value('last_open_directory', '')
        caption = 'Select PL files to add...'
        pl_filepaths, _filter = QtGui.QFileDialog.getOpenFileNames(
                                                            parent=self,
                                                            caption=caption,
                                                            dir=dirpath,
                                                            filter='',
                                                            selectedFilter='',
                                                            options=0)
        if not pl_filepaths:
            self.raise_()
            self.activateWindow()
            return []
        dirpath, _filename = os.path.split(pl_filepaths[0])
        self.settings.setValue('last_open_directory', dirpath)

        return [fp for fp in pl_filepaths if self._validatePLFilePath(fp)]

    def _validatePLFilePath(self, filepath):
        # Test for uniqueness
        if filepath in self.getFilePaths():
            QtGui.QMessageBox.warning(self, 'Duplicate File',
                                      'Ignoring duplicate file.')
            return False  # skip filespaths already in the table
        # Test for parsability
        try:
            parser = SimplePLParser(filepath)
            parser.parse()
        except:
            QtGui.QMessageBox.warning(self, 'Unparsable File',
                                      'Ignoring unparsable file: {}'
                                      ''.format(filepath))
            return False  # skip filepaths that cannot be parsed
        return True

    def _appendFilePathItems(self):
        for pl_filepath in self._getPLFilePaths():
            self._appendFilePath(pl_filepath)
        self.raise_()
        self.activateWindow()

    def _getUniquePrefix(self, filepath):
        filepaths = self.getFilePaths()
        filepaths.append(filepath)
        # tokenize the filenames
        l_tokens = []
        for fp in filepaths:
            _dirpath, filename = os.path.split(fp)
            root, _ext = os.path.splitext(filename)
            l_tokens.append(root.split())
        if len(l_tokens) == 1:
            return l_tokens[0][0]
        for i in xrange(1, len(l_tokens)):
            for j in xrange(len(l_tokens[i])):
                if l_tokens[i - 1][j] != l_tokens[i][j]:
                    _dirpath, filename = os.path.split(filepath)
                    root, _ext = os.path.splitext(filename)
                    return root.split()[j]
            else:
                return ''  # couldn't find a good, unique prefix

    def _appendFilePath(self, filepath):
        row = self.tableWidget.rowCount()
        prefixItem = QtGui.QTableWidgetItem(self._getUniquePrefix(filepath))
        filepathItem = QtGui.QTableWidgetItem(filepath)
        self.tableWidget.insertRow(row - 1)
        self.tableWidget.setItem(row - 1, 0, prefixItem)
        self.tableWidget.setItem(row - 1, 1, filepathItem)
        self.tableWidget.resizeColumnToContents(0)
        self.tableWidget.resizeColumnToContents(1)

    def _setFilePathItem(self, row):
        pl_filepath = self._getPLFilePath()
        item = QtGui.QTableWidgetItem(pl_filepath)
        self.tableWidget.setItem(row, 1, item)
        self.tableWidget.resizeColumnToContents(1)
        self.raise_()
        self.activateWindow()

    def getPrefixes(self):
        prefixes = []
        for row in xrange(self.tableWidget.rowCount() - 1):
            prefixItem = self.tableWidget.item(row, 0)
            if prefixItem:
                prefixes.append(prefixItem.text())
            else:
                prefixes.append('')
        return prefixes

    def getFilePaths(self):
        filepaths = []
        for row in xrange(self.tableWidget.rowCount() - 1):
            filepathItem = self.tableWidget.item(row, 1)
            if filepathItem:
                filepaths.append(filepathItem.text())
            else:
                filepaths.append('')
        return filepaths

    def _generateVeuszFile(self):
        # Make sure there are enough unique prefixes
        prefixes = self.getPrefixes()
        pl_filepaths = self.getFilePaths()

        # Prune rows with empty filepath
        pruned_prefixes = []
        pruned_pl_filepaths = []
        for prefix, filepath in izip(prefixes, pl_filepaths):
            if filepath:
                pruned_prefixes.append(prefix)
                pruned_pl_filepaths.append(filepath)
        prefixes = pruned_prefixes
        pl_filepaths = pruned_pl_filepaths

        # Check for duplicates
        if any(prefixes.count(x) > 1 for x in prefixes):
            # there are duplicates
            QtGui.QMessageBox.warning(self, 'Duplicate Date Prefixes',
                                      'Please provide a unique data prefix '
                                      'for each file.')
            self.raise_()
            self.activateWindow()
            return  # cancel

        # Ask where to save the file
        dirpath = self.settings.value('last_save_directory', '')
        caption = 'Select where to save the Veusz file...'
        save_filepath, _filter = QtGui.QFileDialog.getSaveFileName(
                                                        parent=None,
                                                        caption=caption,
                                                        dir=dirpath,
                                                        filter='*.vsz',
                                                        selectedFilter='',
                                                        options=0)
        if not save_filepath:
            self.raise_()
            self.activateWindow()
            return  # cancel

        dirpath, _filename = os.path.split(save_filepath)
        self.settings.setValue('last_save_directory', dirpath)
        if not save_filepath.endswith('.vsz'):
            save_filepath += '.vsz'

        # Fenerate and output the file
        vertical_spacing = 1. / 2
        with open(save_filepath, 'w') as f:
            for pl_filepath, prefix in zip(pl_filepaths, prefixes):

                parser = SimplePLParser(pl_filepath)
                parser.parse()

                # Output the wavelength array
                f.write("ImportString(u'`%s Wavelength`(numeric)','''\n" %
                        prefix)
                for w in parser.wavelength:
                    f.write("%.1f\n" % w)
                f.write("''')\n")

                # Output the energy array
                f.write("ImportString(u'`%s Energy`(numeric)','''\n" % prefix)
                for w in parser.energy:
                    f.write("%E\n" % w)
                f.write("''')\n")

                # Output the system response removed array
                f.write("ImportString(u'`%s SysResRem`(numeric)','''\n" %
                        prefix)
                for w in parser.signal:
                    f.write("%E\n" % w)
                f.write("''')\n")

                # Output the normalized array
                normalized = parser.signal / parser.signal.max()
                f.write("ImportString(u'`%s Normalized`(numeric)','''\n" %
                        prefix)
                for w in normalized:
                    f.write("%E\n" % w)
                f.write("''')\n")

            # Output the Normalized page
            f.write('''Add('page', name=u'Normalized', autoadd=False)
To(u'Normalized')
Add('graph', name=u'Normalized', autoadd=False)
To(u'Normalized')
Add('axis', name='x', autoadd=False)
To('x')
Set('label', u'Wavelength (nm)')
To('..')
''')
            min = -vertical_spacing
            max = len(prefixes) * vertical_spacing + 1
            for prefix in prefixes:
                f.write('''Add('axis', name=u'y {prefix}', autoadd=False)
To(u'y {prefix}')
Set('hide', True)
Set('label', u'PL Intensity (arb. u.)')
Set('min', {min})
Set('max', {max})
Set('direction', 'vertical')
To('..')
Add('xy', name=u'{prefix}', autoadd=False)
To(u'{prefix}')
Set('xData', u'{prefix} Wavelength')
Set('yData', u'{prefix} Normalized')
Set('key', u'{prefix}')
Set('yAxis', u'y {prefix}')
To('..')
'''.format(prefix=prefix, min=min, max=max))
                min -= vertical_spacing
                max -= vertical_spacing
            f.write('''To('..')\nTo('..')\n''')

            # Output the Normalized vs Energy page
            f.write('''Add('page', name=u'Normalized vs Energy', autoadd=False)
To(u'Normalized vs Energy')
Add('graph', name=u'Normalized vs Energy', autoadd=False)
To(u'Normalized vs Energy')
Add('axis', name='x', autoadd=False)
To('x')
Set('label', u'Energy (eV)')
To('..')
''')
            min = -vertical_spacing
            max = len(prefixes) * vertical_spacing + 1
            for prefix in prefixes:
                f.write('''Add('axis', name=u'y {prefix}', autoadd=False)
To(u'y {prefix}')
Set('hide', True)
Set('label', u'PL Intensity (arb. u.)')
Set('min', {min})
Set('max', {max})
Set('direction', 'vertical')
To('..')
Add('xy', name=u'{prefix}', autoadd=False)
To(u'{prefix}')
Set('xData', u'{prefix} Energy')
Set('yData', u'{prefix} Normalized')
Set('key', u'{prefix}')
Set('yAxis', u'y {prefix}')
To('..')
'''.format(prefix=prefix, min=min, max=max))
                min -= vertical_spacing
                max -= vertical_spacing
            f.write('''To('..')\nTo('..')\n''')

            # Output the SysResRem page
            f.write('''Add('page', name=u'SysResRem', autoadd=False)
To(u'SysResRem')
Add('graph', name=u'SysResRem', autoadd=False)
To(u'SysResRem')
Add('axis', name='x', autoadd=False)
To('x')
Set('label', u'Wavelength (nm)')
To('..')
Add('axis', name=u'y', autoadd=False)
To(u'y')
Set('label', u'PL Intensity (arb. u.)')
Set('direction', 'vertical')
To('..')
''')
            for prefix in prefixes:
                f.write('''Add('xy', name=u'{prefix}', autoadd=False)
To(u'{prefix}')
Set('xData', u'{prefix} Wavelength')
Set('yData', u'{prefix} SysResRem')
Set('key', u'{prefix}')
Set('hide', False)
To('..')
'''.format(prefix=prefix))
            f.write('''To('..')\nTo('..')\n''')

            # Output the SysResRem vs Energy page
            f.write('''Add('page', name=u'SysResRem vs Energy', autoadd=False)
To(u'SysResRem vs Energy')
Add('graph', name=u'SysResRem vs Energy', autoadd=False)
To(u'SysResRem vs Energy')
Add('axis', name='x', autoadd=False)
To('x')
Set('label', u'Energy (eV)')
To('..')
Add('axis', name=u'y', autoadd=False)
To(u'y')
Set('label', u'PL Intensity (arb. u.)')
Set('direction', 'vertical')
To('..')
''')
            for prefix in prefixes:
                f.write('''Add('xy', name=u'{prefix}', autoadd=False)
To(u'{prefix}')
Set('xData', u'{prefix} Energy')
Set('yData', u'{prefix} SysResRem')
Set('key', u'{prefix}')
Set('hide', False)
To('..')
'''.format(prefix=prefix))
            f.write('''To('..')\nTo('..')\n''')

        # Close the dialog
        self.close()

if __name__ == '__main__':
    app = QtGui.QApplication([])
    d = GenerateVeuszFileDialog().exec_()
