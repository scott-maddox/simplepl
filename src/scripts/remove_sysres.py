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
import os.path

# third party imports

# local imports
from simplepl.simple_pl_parser import SimplePLParser
from simplepl.utils import open_dialog, open_multiple_dialog, dir_dialog
print 'Select files from which to remove the system response...'
filenames = open_multiple_dialog('*.*')
print filenames
print 'Select the system response file to open...'
sysres_filename = open_dialog('*.*')
print sysres_filename
print 'Select the directory in which to save the system response removed files...'
sysresrem_dir = dir_dialog()
print sysresrem_dir

for filename in filenames:
    parser = SimplePLParser(filename, sysres_filename)
    parser.parse()
    path, pathless_filename = os.path.split(filename)
    sysresrem_filename = os.path.join(sysresrem_dir, pathless_filename)
    with open(sysresrem_filename, 'w') as f:
        f.write('Wavelength\tSysResRem\n')
        for i in xrange(len(parser.wavelength)):
            f.write('%.1f\t%E\n'%(parser.wavelength[i], parser.sysresrem[i]))