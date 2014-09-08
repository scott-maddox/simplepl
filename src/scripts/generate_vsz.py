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
vertical_spacing = 1./2

# std lib imports
import os.path

# third party imports
from PySide import QtCore, QtGui

# local imports
from simplepl.simple_pl_parser import SimplePLParser


app = QtGui.QApplication([])
app.setOrganizationName("Scott J Maddox")
app.setApplicationName("SimplePL")
settings = QtCore.QSettings()
dirpath = settings.value('last_directory', '')
caption = 'Select the PL files to import...'
pl_filepaths, _filter = QtGui.QFileDialog.getOpenFileNames(parent=None,
                                                           caption=caption,
                                                           dir=dirpath,
                                                           filter='',
                                                           selectedFilter='',
                                                           options=0)
if not pl_filepaths:
    raise ValueError('no PL files selected')
dirpath, _filename = os.path.split(pl_filepaths[0])
settings.setValue('last_directory', dirpath)
print pl_filepaths
# print 'Select the system response file to use (if any)...'
# sysres_filepath = open_dialog('*.*')
# print sysres_filepath
sysres_filepath = None
caption = 'Select where to save the vsz file...'
save_filepath, _filter = QtGui.QFileDialog.getSaveFileName(parent=None,
                                                           caption=caption,
                                                           dir=dirpath,
                                                           filter='*.vsz',
                                                           selectedFilter='',
                                                           options=0)
if not save_filepath:
    raise ValueError('no save path selected')
if not save_filepath.endswith('.vsz'):
    save_filepath += '.vsz'
print save_filepath

# tokenize the filenames
l_tokens = []
for pl_filepath in pl_filepaths:
    dirpath, filename = os.path.split(pl_filepath)
    root, ext = os.path.splitext(filename)
    l_tokens.append(root.split())


# figure out what the difference between filename tokens is
def get_token_diff_index(l_tokens):
    '''
    Finds the first difference between the filename tokens and returns
    the index of the token.
    '''
    skip = 0
    for i in xrange(skip, len(l_tokens)):
        # ignore the first token, since it's either the dattime or a scan number
        for j in xrange(skip, len(l_tokens[i])):
            if l_tokens[i-1][j] != l_tokens[i][j]:
                return j
        else:
            raise Exception("Couldn't find the difference between filename tokens")

token_diff_index = get_token_diff_index(l_tokens)
# extract the actual differences
token_diffs = [tokens[token_diff_index] for tokens in l_tokens]

# write import statements to the vsz file
with open(save_filepath, 'w') as f:
    for pl_filepath, token_diff in zip(pl_filepaths, token_diffs):
        parser = SimplePLParser(pl_filepath, sysres_filepath)
        parser.parse()

        # Output the wavelength array
        f.write("ImportString(u'`%s Wavelength`(numeric)','''\n"%token_diff)
        for w in parser.wavelength:
            f.write("%.1f\n"%w)
        f.write("''')\n")

        # Output the energy array
        f.write("ImportString(u'`%s Energy`(numeric)','''\n"%token_diff)
        for w in parser.energy:
            f.write("%E\n"%w)
        f.write("''')\n")

        # Output the system response removed array
        f.write("ImportString(u'`%s SysResRem`(numeric)','''\n"%token_diff)
        for w in parser.signal:
            f.write("%E\n"%w)
        f.write("''')\n")

        # Output the normalized array
        normalized = parser.signal / parser.signal.max()
        f.write("ImportString(u'`%s Normalized`(numeric)','''\n"%token_diff)
        for w in normalized:
            f.write("%E\n"%w)
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
    max = len(token_diffs)*vertical_spacing+1
    for token_diff in reversed(token_diffs):
        f.write('''Add('axis', name=u'y {token_diff}', autoadd=False)
To(u'y {token_diff}')
Set('hide', True)
Set('label', u'PL Intensity (arb. u.)')
Set('min', {min})
Set('max', {max})
Set('direction', 'vertical')
To('..')
Add('xy', name=u'{token_diff}', autoadd=False)
To(u'{token_diff}')
Set('xData', u'{token_diff} Wavelength')
Set('yData', u'{token_diff} Normalized')
Set('yAxis', u'y {token_diff}')
To('..')
'''.format(token_diff=token_diff, min=min, max=max))
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
    max = len(token_diffs)*vertical_spacing+1
    for token_diff in reversed(token_diffs):
        f.write('''Add('axis', name=u'y {token_diff}', autoadd=False)
To(u'y {token_diff}')
Set('hide', True)
Set('label', u'PL Intensity (arb. u.)')
Set('min', {min})
Set('max', {max})
Set('direction', 'vertical')
To('..')
Add('xy', name=u'{token_diff}', autoadd=False)
To(u'{token_diff}')
Set('xData', u'{token_diff} Energy')
Set('yData', u'{token_diff} Normalized')
Set('yAxis', u'y {token_diff}')
To('..')
'''.format(token_diff=token_diff, min=min, max=max))
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
    for token_diff in reversed(token_diffs):
        f.write('''Add('xy', name=u'{token_diff}', autoadd=False)
To(u'{token_diff}')
Set('xData', u'{token_diff} Wavelength')
Set('yData', u'{token_diff} SysResRem')
Set('hide', False)
To('..')
'''.format(token_diff=token_diff))
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
    for token_diff in reversed(token_diffs):
        f.write('''Add('xy', name=u'{token_diff}', autoadd=False)
To(u'{token_diff}')
Set('xData', u'{token_diff} Energy')
Set('yData', u'{token_diff} SysResRem')
Set('hide', False)
To('..')
'''.format(token_diff=token_diff))
    f.write('''To('..')\nTo('..')\n''')