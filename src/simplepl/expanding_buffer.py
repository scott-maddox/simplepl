#
#   Copyright (c) 2014, Scott J Maddox
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
'''
Defines the ExpandingBuffer class--a numpy array based expanding buffer
designed for efficient real-time plotting.
'''

import numpy as np


class ExpandingBuffer(object):
    '''
    A numpy array based expanding buffer that allows efficient appending
    and accessing of ordered values. This implementation is designed
    specifically for real-time plotting.
    '''

    # np.float64 needed to hold time.time()
    def __init__(self, initial_size=1024, dtype=np.float64):
        '''
        Creates an ExpandingBuffer with the given initial size and dtype.

        :param integer size: the initial size of the ExpandingBuffer
        :param numpy.dtype dtype: the data type of the contained values
        :returns ExpandingBuffer:
        '''
        assert initial_size > 0
        self._size = initial_size
        self.dtype = dtype
        self._buffer = np.empty(initial_size, dtype=dtype)
        self._index = 0

    @classmethod
    def from_array(cls, array):
        '''
        Creates a ExpandingBuffer from the given numpy array. The dtype will
        be the same as the array, and the initial values are copied in from
        the array.

        :param numpy.array array: the numpy array to create the
                                  ExpandingBuffer from
        :returns ExpandingBuffer:
        '''
        rb = cls(array.size, dtype=array.dtype)
        rb.extend(array)
        return rb

    def append(self, value):
        '''
        Append a value to the end of the ExpandingBuffer.

        :param number value: a value to append to the ExpandingBuffer
        :returns None:
        '''
        if self._index >= self._size:
            # get a new buffer that's 2x longer
            old_buffer = self._buffer
            old_size = self._size
            self._size = self._size * 2
            self._buffer = np.empty(self._size, dtype=self.dtype)
            self._buffer[:old_size] = old_buffer

        i = self._index
        self._buffer[i] = value
        self._index += 1

    def extend(self, iterable):
        '''
        Extend the ExpandingBuffer with the values in iterable.

        :param sequence iterable: a sequency of values to append
        :returns None:
        '''
        for v in iterable:
            self.append(v)

    def get(self):
        '''
        Get the array.

        :param None:
        :returns numpy.array: the array of values
        '''
        return self._buffer[0:self._index]

    def clear(self):
        '''
        Clears the contents of the ExpandingBuffer.

        :param None:
        :returns None:
        '''
        self._index = 0

    def __len__(self):
        return self._index

if __name__ == "__main__":
    x = ExpandingBuffer(10, dtype=np.int32)
    for i in xrange(100):
        x.append(i)
        print x.get()
