"""quake_data.py

Copyright (C) 1996-1997  Id Software, Inc.
Copyright (C) 1997-2006  Andy Bay <IMarvinTPA@bigfoot.com>
Copyright (C) 2007-2011  O.Sezer <sezero@users.sourceforge.net>
Copyright (C) 2012       John Trainer <n@nightmiles.org>

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, 
USA.
"""

import os
import struct

DIRECTORYENTRY_OFFSET_LEN = 4
DIRECTORYENTRY_SIZE_LEN = 4


class DirectoryEntry:
	def __init__(self, dirfile=None, fileoffset=None, offset=None, size=None):
		if dirfile: 
			if offset:
				dirfile.seek(offset, os.SEEK_SET)
		
			self.offset = dirfile.read(DIRECTORYENTRY_OFFSET_LEN)
			if len(self.offset) < DIRECTORYENTRY_OFFSET_LEN:
				raise Exception('Unexpected end of file reached while ' +\
					'trying to read directory entry offset')
			else:
				self.offset = struct.unpack('i', self.offset)[0]
		
			self.size = dirfile.read(DIRECTORYENTRY_SIZE_LEN)
			if len(self.size) < DIRECTORYENTRY_SIZE_LEN:
				raise Exception('Unexpected end of file reached while ' +\
					'trying to read directory entry size')
			else:
				self.size = struct.unpack('i', self.size)[0]
		else:
			self.offset = offset
			self.size = size
		 
			
	def get_packed(self):
		return struct.pack('ii', self.offset, self.size)