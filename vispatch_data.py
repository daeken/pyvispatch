"""vispatch_data.py

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

import sys
import struct
import os

VISPATCH_BSPNAME_LEN = 32
VISPATCH_ENTRY_SIZE_LEN = 4
VISPATCH_VISDATA_SIZE_LEN = 4
VISPATCH_LEAFDATA_SIZE_LEN = 4


class VisPatchEntry:
	def __init__(self, bspname, visdata, leafdata, number=None):
		self.number = number
		self.bspname = os.path.basename(bspname)
		self.visdata = visdata
		self.leafdata = leafdata
		
	def get_packed(self):
		data = self.bspname
		
		bspnamelen = len(self.bspname)
		if (bspnamelen < VISPATCH_BSPNAME_LEN):
			''.join([data, 
				struct.pack('x' * (VISPATCH_BSPNAME_LEN - bspnamelen))])
		
		visdatasize = len(self.visdata)
		leafdatasize = len(self.leafdata)
		
		''.join([data, struct.pack('i', 8 + visdatasize + leafdatasize),
			struct.pack('i', visdatasize), self.visdata,
			struct.pack('i', leafdatasize, self.leafdata)])
		
		return data
		
		
class VisPatch:
	def __init__(self, filename=None):
		self.entries = []
		
		if filename:
			count = 0
	
			with open(filename, 'rb') as visfile:
				bspname = visfile.read(VISPATCH_BSPNAME_LEN)

				while len(bspname) == VISPATCH_BSPNAME_LEN:
					bspname = bspname.split('\0')[0]
					bspname = bspname.strip()

					entrysize = visfile.read(VISPATCH_ENTRY_SIZE_LEN)
					if len(entrysize) < VISPATCH_ENTRY_SIZE_LEN:
						sys.stderr.write('Unexpected end of file reached ' +\
							'while trying to read Vis file entry size\n')
						return 1
					else:
						entrysize = struct.unpack('i', entrysize)[0]

					visdatasize = visfile.read(VISPATCH_VISDATA_SIZE_LEN)
					if len(visdatasize) < VISPATCH_VISDATA_SIZE_LEN:
						sys.stderr.write('Unexpected end of file reached ' +\
							'while trying to read Vis data size\n')
						return 1
					else:
						visdatasize = struct.unpack('i', visdatasize)[0]

					visdata = visfile.read(visdatasize)
					if len(visdata) < visdatasize:
						sys.stderr.write('Unexpected end of file reached ' +\
							'while trying to read Vis data\n')
						return 1

					leafdatasize = visfile.read(VISPATCH_LEAFDATA_SIZE_LEN)
					if len(leafdatasize) < VISPATCH_LEAFDATA_SIZE_LEN:
						sys.stderr.write('Unexpected end of file reached ' +\
							'while trying to read leaf data size\n')
						return 1
					else:
						leafdatasize = struct.unpack('i', leafdatasize)[0]

					leafdata = visfile.read(leafdatasize)
					if len(leafdata) < leafdatasize:
						sys.stderr.write('Unexpected end of file reached ' +\
							'while trying to read leaf data\n')
						return 1

					self.entries.append(VisPatchEntry(bspname, visdata, 
						leafdata, count))

					count = count + 1
					bspname = visfile.read(VISPATCH_BSPNAME_LEN)
	
	def num_entries(self):
		return len(self.entries)
		
	def get_entry_for_filename(self, filename):
		basename = os.path.basename(filename)
		
		for entry in self.entries:
			if basename.lower() == entry.bspname.lower():
				return entry
		
		return None
		
	def append_entry(self, entry):
		entry.number = len(self.entries)
		self.entries.append(entry)
		
	def get_packed(self):
		data = ''
		
		for entry in self.entries:
			''.join([data, entry.get_packed()])
			
		return data
		