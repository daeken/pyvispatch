"""quake_bsp.py

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

BSP_VERSION_LEN = 4
BSP_HEADER_LEN = 4 + (8 * 15)

class QuakeBsp:
	def __init__(self, filename, bspfile, offset=None):
		if offset:
			bspfile.seek(offset, os.SEEK_SET)
		
		self.version = bspfile.read(BSP_VERSION_LEN)
		if len(self.version) < BSP_VERSION_LEN:
			raise Exception('Unexpected end of file reached while trying to read BSP version')
		else:
			self.version = struct.unpack('i', self.version)[0]
			
		self.entities_metadata = quake_data.DirectoryEntry(dirfile=bspfile);
		self.planes_metadata = quake_data.DirectoryEntry(dirfile=bspfile);
		self.miptex_metadata = quake_data.DirectoryEntry(dirfile=bspfile);
		self.vertices_metadata = quake_data.DirectoryEntry(dirfile=bspfile);
		self.visilist_metadata = quake_data.DirectoryEntry(dirfile=bspfile);
		self.nodes_metadata = quake_data.DirectoryEntry(dirfile=bspfile);
		self.texinfo_metadata = quake_data.DirectoryEntry(dirfile=bspfile);
		self.faces_metadata = quake_data.DirectoryEntry(dirfile=bspfile);
		self.lightmaps_metadata = quake_data.DirectoryEntry(dirfile=bspfile);
		self.clipnodes_metadata = quake_data.DirectoryEntry(dirfile=bspfile);
		self.leaves_metadata = quake_data.DirectoryEntry(dirfile=bspfile);
		self.lface_metadata = quake_data.DirectoryEntry(dirfile=bspfile);
		self.edges_metadata = quake_data.DirectoryEntry(dirfile=bspfile);
		self.ledges_metadata = quake_data.DirectoryEntry(dirfile=bspfile);
		self.models_metadata = quake_data.DirectoryEntry(dirfile=bspfile);
		
		self.filename = filename
		self.bspfile = bspfile
		self.offset = offset
	
	def get_size(self):
		return self.models_metadata.offset + self.models_metadata.size
		
	def get_header(self):
		data = struct.pack('i', self.version) + \
			self.entities_metadata.get_packed() + \
			self.planes_metadata.get_packed() + \
			self.miptex_metadata.get_packed() + \
			self.vertices_metadata.get_packed() + \
			self.visilist_metadata.get_packed() + \
			self.nodes_metadata.get_packed() + \
			self.texinfo_metadata.get_packed() + \
			self.faces_metadata.get_packed() + \
			self.lightmaps_metadata.get_packed() + \
			self.clipnodes_metadata.get_packed() + \
			self.leaves_metadata.get_packed() + \
			self.lface_metadata.get_packed() + \
			self.edges_metadata.get_packed() + \
			self.ledges_metadata.get_packed() + \
			self.models_metadata.get_packed()
		return data