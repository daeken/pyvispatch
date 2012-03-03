"""quake_pak.py

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
import quake_data

MAX_FILES_IN_PAK = 2048

PAK_HEADER_OFFSET = 0

PAK_MAGIC_LEN = 4
PAK_DIR_OFFSET_LEN = 4
PAK_DIR_SIZE_LEN = 4

PAK_HEADER_LEN = PAK_MAGIC_LEN + PAK_DIR_OFFSET_LEN + PAK_DIR_SIZE_LEN

PAK_MAGIC = 'PACK'

PAKENTRY_FILENAME_LEN = 56
PAKENTRY_OFFSET_LEN = 4
PAKENTRY_SIZE_LEN = 4
PAKENTRY_LEN = PAKENTRY_FILENAME_LEN + PAKENTRY_OFFSET_LEN + PAKENTRY_SIZE_LEN


class QuakePakEntry(quake_data.DirectoryEntry):
	def __init__(self, pakfile=None, pakoffset=None, filename=None, 
			offset=None, size=None):
		if pakfile:
			if offset:
				pakfile.seek(offset, os.SEEK_SET)
		
			self.filename = pakfile.read(PAKENTRY_FILENAME_LEN)
			if len(self.filename) < PAKENTRY_FILENAME_LEN:
				raise Exception('Unexpected end of file reached while ' +\
					'trying to read PAK entry filename')
			else:
				self.filename_fixed = self.filename
				self.filename = self.filename.split('\0')[0]
				self.filename = self.filename.strip()
		
			quake_data.DirectoryEntry.__init__(self, dirfile=pakfile)
		else:
			self.filename_fixed = filename
			self.filename = filename.split('\0')[0]
			self.filename = self.filename.strip()
			
			quake_data.DirectoryEntry.__init__(self, offset=offset, size=size)
			
	def get_packed(self):
		data = self.filename_fixed
		
		filenamelen = len(self.filename_fixed)
		if (filenamelen < PAKENTRY_FILENAME_LEN):
			''.join([data, 
				struct.pack('x' * (PAKENTRY_FILENAME_LEN - filenamelen))])
		
		''.join([data, quake_data.DirectoryEntry.get_packed(self)])
		
		return data
		

class QuakePak:
	def __init__(self, pakfile=None):
		self.entries = []
		
		if pakfile:
			returnto = pakfile.tell()
			pakfile.seek(PAK_HEADER_OFFSET, os.SEEK_SET)
		
			magic = pakfile.read(PAK_MAGIC_LEN)
			if len(magic) < PAK_MAGIC_LEN:
				raise Exception('Unexpected end of file reached while ' +\
					'trying to read PAK format')
			elif magic != PAK_MAGIC:
				raise Exception('Attempted to load a file which does not ' +\
					'appear to be a valid PAK')
			
			directory_metadata = quake_data.DirectoryEntry(dirfile=pakfile)
			entrycount = directory_metadata.size / PAKENTRY_LEN
			
			if entrycount > MAX_FILES_IN_PAK:
				raise Exception('This PAK appears to have %i files but ' +\
					'PAKs only support up to %i.' % \
					(entrycount, MAX_FILES_IN_PAK))
		
			pakfile.seek(directory_metadata.offset, os.SEEK_SET)
		
			for i in range(0,entrycount):
				self.entries.append(QuakePakEntry(pakfile=pakfile))
			
			pakfile.seek(returnto, os.SEEK_SET)
	
	def append_entry(self, entry):
		self.entries.append(entry)
		
	def get_data_size(self):
		size = 0
		
		for entry in self.entries:
			size = size + entry.size
			
		return size
		
	def get_directory_size(self):
		return len(self.entries) * PAKENTRY_LEN
		
	def get_header(self):
		diroffset = PAK_HEADER_OFFSET + PAK_HEADER_LEN + self.get_data_size()
		
		directory_metadata = quake_data.DirectoryEntry(offset=diroffset, 
			size=self.get_directory_size())
		data = PAK_MAGIC + directory_metadata.get_packed()
		
		return data
		
	def get_directory(self):
		data = ''
		
		for entry in self.entries:
			''.join([data, entry.get_packed()])
			
		return data
			