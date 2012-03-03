#!/usr/bin/python -tt
"""pyvispatch: Quake level patcher for water visibility.

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
import sys
import fnmatch
import traceback
import struct
import argparse
import quake_bsp
import quake_pak
import vispatch_data

APP_NAME = 'pyvispatch'
APP_VERSION = '0.0.1'
COPYRIGHT_NOTICE = 	\
'Copyright (C) 1996-1997  Id Software, Inc.\n' +\
'Copyright (C) 1997-2006  Andy Bay <IMarvinTPA@bigfoot.com>\n' +\
'Copyright (C) 2007-2011  O.Sezer <sezero@users.sourceforge.net>\n' +\
'Copyright (C) 2012       John Trainer <n@nightmiles.org>\n\n' +\
'pyvispatch comes with ABSOLUTELY NO WARRANTY. This is free software, and ' +\
'you\nare welcome to redistribute it under certain conditions; see COPYING' +\
' for\ndetails.'

TEMP_FILE_NAME = '~vistmp.tmp'
TEMP_PAK_NAME = '~vispak.tmp'

MIN_BSP_SIZE = 50001

MODE_PATCH = 0
MODE_EXTRACT = 1
MODE_NEW = 2
	
	
def main(filemask, mapsdir, visfilename, new=False, extract=False):
	print '%s v%s\n\n%s\n' % (APP_NAME, APP_VERSION, COPYRIGHT_NOTICE) 
	
	
	if not filemask or len(filemask) < 1:
		sys.stderr.write('You must specify a file or wildcard to patch\n')
		return 1
	
	currentdir = os.getcwd()
	if not currentdir or len(currentdir) < 1:
		sys.stderr.write('Unable to determine current working directory\n')
		return 1
		
	print 'Current directory:', currentdir
	
	if not mapsdir or len(mapsdir) < 1:
		mapsdir = currentdir
	else:
		print 'Will look into %s as the pak/bsp directory..' % (mapsdir)
	
	# This is only done to approximate the output of the original VisPatch.
	mode = MODE_PATCH
	if extract and new:
		sys.stderr.write('"extract" and "new" cannot be used together\n')
		return 1
	elif extract:
		mode = MODE_EXTRACT
	elif new:
		mode = MODE_NEW
		
	print 'VisPatch is in mode %i' % (mode)
	
	if not visfilename or len(visfilename) < 1:
		sys.stderr.write('Vis data filename is blank\n')
		return 1
		
	print 'Will use %s as the Vis-data source' % (visfilename)
		
	
	outpaknum = -1
	outpakname = None
	
	if extract:
		print 'Will extract Vis data to %s, auto-append.' % (visfilename)
	elif new:
		if '*' in filemask:
			for filename in os.listdir(mapsdir):
				if fnmatch.fnmatch(filename.lower(), 'pak*.pak'):
					outpaknum = outpaknum + 1
			if outpaknum > -1:
				outpaknum = outpaknum + 1
				outpakname = os.path.join(mapsdir, 'pak%i.pak' % (outpaknum))
				print 'The new pak file will be called %s.' % (outpakname)
				
	tempfilename = os.path.join(mapsdir, TEMP_FILE_NAME)
	temppakname = os.path.join(mapsdir, TEMP_PAK_NAME)
	
	if not extract:
		chk = 0
		
		try:
			vispatch = vispatch_data.VisPatch(visfilename)
		except Exception as e:
			sys.stderr.write("couldn't load the vis source file.\n")
			return 1
			
		if vispatch.num_entries() < 1:
			sys.stderr.write('No Vis entries found in the Vis source file\n')
			return 1
		
		
		# Start by creating/truncating temporary PAK file.
		#
		# This won't actually be used unless in new mode, but it's easier to
		# put this here to avoid issues.
		with open(temppakname, 'wb') as temppakfile:
			temppakfile.seek(quake_pak.PAK_HEADER_LEN)
			
			if new:
				newpak = quake_pak.QuakePak()
			else:
				newpak = None
				
			if '*' in filemask:
				for filename in os.listdir(mapsdir):
					if fnmatch.fnmatch(filename.lower(), filemask) 
							and filename.lower().endswith(('.pak', '.bsp')):
						patch_file(filename, vispatch, tempfilename, 
							temppakfile, newpak, mapsdir)	
			elif filemask.lower().endswith(('.pak', '.bsp')):
				patch_file(filemask, vispatch, tempfilename, temppakfile, 
					newpak, mapsdir)
			# VisPatch displays no error/warning when filename/mask is 
			# provided but is not/does not match a BSP or PAK or if file was 
			# not found.
			
			# After processing BSPs, if a new PAK was made write out its 
			# header and directory.
			if new and len(newpak.entries) > 0:
				temppakfile.write(newpak.get_directory())
				temppakfile.seek(quake_pak.PAK_HEADER_OFFSET, os.SEEK_SET)
				temppakfile.write(newpak.get_header())
		
		# If a new PAK was created, rename it to outpakname
		if new and len(newpak.entries) > 0:
			os.rename(temppakname, outpakname)
		else:
			# Otherwise, just delete the temp file
			os.delete(temppakname)
	else:
		# Extract mode
		vispatch = vispatch_data.VisPatch()
		
		if '*' in filemask:
			for filename in os.listdir(mapsdir):
				if fnmatch.fnmatch(filename.lower(), filemask) 
						and filename.lower().endswith(('.pak', '.bsp')):
					extract_file(filename, vispatch, mapsdir)
		elif filemask.lower().endswith(('.pak', '.bsp')):
			extract_file(filemask, vispatch, mapsdir)
		# VisPatch displays no error/warning when filename/mask is provided 
		# but is not/does not match a BSP or PAK or if file was not found.
					
		if len(vispatch.entries) > 0:
			with open(visfilename, 'ab') as visfile:
				visfile.write(vispatch.get_packed())
		else:
			print 'No vis info was found to extract. Vis data file will ' +\
				'not be created/changed.'
			
	return 0


def read_bsp_data(bspfile, inoffset, direntry):
	bspfile.seek(inoffset + direntry.offset, os.SEEK_SET)
	data = bspfile.read(direntry.size)
	return data


def copy_and_align(bspfile, inoffset, direntry, outfile):
	data = read_bsp_data(bspfile, inoffset, direntry)
	write_and_align(outfile, direntry.size, data)


def write_and_align(outfile, size, data):
	outfile.write(data)

	if size % 4 != 0:
		outfile.write(struct.pack('x' * (4 - (size % 4))))


def patch_bsp(bsp, vispatch, tempfile, new=False):
	print 'BSP Version %i, Vis info at %i (%i bytes)' % (bsp.version, 
		bsp.visilist_metadata.offset, bsp.visilist_metadata.size)
	
	# If bsp.offset isn't None, the BSP is in a PAK file at offset bsp.offset
	if bsp.offset:
		inoffset = bsp.offset
	else:
		inoffset = 0
		
	outoffset = tempfile.tell()
	
	visentry = vispatch.get_entry_for_filename(bsp.filename)
	
	if not visentry:
		# No VisPatch was found for this BSP's filename
		if bsp.offset:
			bsp.bspfile.seek(inoffset, os.SEEK_SET)
			
			if not new:
				# If the BSP is in a PAK and the tempfile will eventually 
				# replace that PAK (i.e. the user hasn't chosen "new" mode) 
				# then take a straight copy of this BSP and shove it into the
				# new PAK.
				# 
				# This isn't done if a new PAK is being created. Only modified
				# BSP files get put there.
				unmodified = bsp.bspfile.read(bsp.get_size())
				
				tempfile.write(unmodified)
		
		# No patching occurred, just a stright copy if not doing an overwrite
		return False
	else:
		visdatasize = len(visentry.visdata)
		leafdatasize = len(visentry.leafdata)
		print 'Name: %s Size: %i (# %i)' % (visentry.bspname, visdatasize, 
			visentry.number)
		
		# Replace the size of VisData and leaves data with those of the data 
		# they will be replaced with from the VisPatch.
		bsp.visilist_metadata.size = visdatasize
		bsp.leaves_metadata.size = leafdatasize
		
		# Seek past the header of the BSP
		tempfile.seek(quake_bsp.BSP_HEADER_LEN, os.SEEK_CUR)
		
		# Existing planes data
		newoffset = tempfile.tell() - outoffset
		copy_and_align(bsp.bspfile, inoffset, bsp.planes_metadata, tempfile)
		bsp.planes_metadata.offset = newoffset
		
		# New leaf data from VisPatch
		newoffset = tempfile.tell() - outoffset
		write_and_align(tempfile, leafdatasize, visentry.leafdata)
		bsp.leaves_metadata.offset = newoffset
		
		# Existing vertices data
		newoffset = tempfile.tell() - outoffset
		copy_and_align(bsp.bspfile, inoffset, bsp.vertices_metadata, tempfile)
		bsp.vertices_metadata.offset = newoffset
		
		# Existing nodes data
		newoffset = tempfile.tell() - outoffset
		copy_and_align(bsp.bspfile, inoffset, bsp.nodes_metadata, tempfile)
		bsp.nodes_metadata.offset = newoffset
		
		# Existing texinfo data
		newoffset = tempfile.tell() - outoffset
		copy_and_align(bsp.bspfile, inoffset, bsp.texinfo_metadata, tempfile)
		bsp.texinfo_metadata.offset = newoffset
		
		# Existing faces data
		newoffset = tempfile.tell() - outoffset
		copy_and_align(bsp.bspfile, inoffset, bsp.faces_metadata, tempfile)
		bsp.faces_metadata.offset = newoffset
		
		# Existing clipnodes data
		newoffset = tempfile.tell() - outoffset
		copy_and_align(bsp.bspfile, inoffset, bsp.clipnodes_metadata, 
			tempfile)
		bsp.clipnodes_metadata.offset = newoffset
		
		# Existing lface data
		newoffset = tempfile.tell() - outoffset
		copy_and_align(bsp.bspfile, inoffset, bsp.lface_metadata, tempfile)
		bsp.lface_metadata.offset = newoffset
		
		# Existing ledges data
		newoffset = tempfile.tell() - outoffset
		copy_and_align(bsp.bspfile, inoffset, bsp.ledges_metadata, tempfile)
		bsp.ledges_metadata.offset = newoffset
		
		# Existing edges data
		newoffset = tempfile.tell() - outoffset
		copy_and_align(bsp.bspfile, inoffset, bsp.edges_metadata, tempfile)
		bsp.edges_metadata.offset = newoffset
		
		# Existing models data
		newoffset = tempfile.tell() - outoffset
		copy_and_align(bsp.bspfile, inoffset, bsp.models_metadata, tempfile)
		bsp.models_metadata.offset = newoffset
		
		# Existing lightmaps data
		newoffset = tempfile.tell() - outoffset
		copy_and_align(bsp.bspfile, inoffset, bsp.lightmaps_metadata, 
			tempfile)
		bsp.lightmaps_metadata.offset = newoffset
		
		# New visilist data from VisPatch
		newoffset = tempfile.tell() - outoffset
		write_and_align(tempfile, visdatasize, visentry.visdata)
		bsp.visilist_metadata.offset = newoffset
		
		# Existing entities data
		newoffset = tempfile.tell() - outoffset
		copy_and_align(bsp.bspfile, inoffset, bsp.entities_metadata, tempfile)
		bsp.entities_metadata.offset = newoffset
		
		# Existing miptex data
		newoffset = tempfile.tell() - outoffset
		copy_and_align(bsp.bspfile, inoffset, bsp.miptex_metadata, tempfile)
		bsp.miptex_metadata.offset = newoffset
		
		# Write header
		afterbsp = tempfile.tell()
		tempfile.seek(outoffset, os.SEEK_SET)
		tempfile.write(bsp.get_header())
		tempfile.seek(afterbsp)
		
		# Patching occurred
		return True
	
		
def patch_bsp_file(filepath, vispatch, tempfilename, new, mapsdir):
	didpatch = False

	# Only operate on the file if it is at at least MIN_BSP_SIZE
	if os.path.getsize(filepath) >= MIN_BSP_SIZE:
		with open(filepath, 'rb') as bspfile:
			print 'Looking at file %s.' % (filepath)
			bsp = quake_bsp.QuakeBsp(filepath, bspfile)
			with open(tempfilename, 'wb') as tempfile:
				didpatch = patch_bsp(bsp, vispatch, tempfile, new)
		if didpatch:
			if new:
				bakpath = os.path.join(mapsdir, 
					os.path.basename(filepath)[0:-4] + '.bak')
				os.rename(filepath, bakpath)
			os.rename(tempfilename, filepath)
		else:
			# No patching happened, so get rid of the temp file
			os.delete(tempfilename)

		
def extract_bsp(bsp, vispatch):
	print 'Version of bsp file is:  %i' % (bsp.version)
	print 'Vis info is at %i and is %i long' % (bsp.visilist_metadata.offset, 
		bsp.visilist_metadata.size)
	print 'Leaf info is at %i and is %i long' % (bsp.leaves_metadata.offset, 
		bsp.leaves_metadata.size)
	
	if bsp.visilist_metadata.size < 1:
		print 'Vis info size = %i.  Skipping...' % \
			(bsp.visilist_metadata.size)
	else:
		# If bsp.offset isn't None, the BSP is in a PAK file at offset 
		# bsp.offset
		if bsp.offset:
			inoffset = bsp.offset
		else:
			inoffset = 0
		
		visdata = read_bsp_data(bsp.bspfile, inoffset, bsp.visilist_metadata)
		leafdata = read_bsp_data(bsp.bspfile, inoffset, bsp.leaves_metadata)
		
		visentry = vispatch_data.VisPatchEntry(bsp.filename, visdata, 
			leafdata)
		vispatch.append_entry(visentry)
	
		
def extract_bsp_file(filepath, vispatch):
	with open(filepath, 'rb') as bspfile:
		print 'Looking at file %s.' % (os.path.basename(filepath))
		bsp = quake_bsp.QuakeBsp(filepath, bspfile)
		extract_bsp(bsp, vispatch)


def patch_pak_into_file(path, vispatch, tempfile, newpak=None):
	patchcount = 0
	
	if newpak:
		new = True
	else:
		new = False
	
	print 'Looking at file %s.' % (os.path.basename(path))
	with open(path, 'rb') as pakfile:
		pak = quake_pak.QuakePak(pakfile)

		pakfile.seek(quake_pak.PAK_HEADER_OFFSET + quake_pak.PAK_HEADER_LEN, 
			os.SEEK_SET)
		
		for entry in pak.entries:
			# New offset for this entry will be where we left off
			newoffset = tempfile.tell()
			
			# Only operate on the file if it's a .bsp of at least MIN_BSP_SIZE
			if entry.size >= MIN_BSP_SIZE 
					and entry.filename.lower().endswith('.bsp'):
				print 'Looking at file %s.' % (entry.filename)
				bsp = quake_bsp.QuakeBsp(entry.filename, pakfile, 
					entry.offset)
				
				if patch_bsp(bsp, vispatch, tempfile, new):
					patchcount = patchcount + 1
					# Patching happened - the size may have changed
					entry.size = tempfile.tell() - newoffset
					entry.offset = newoffset
					if newpak:
						newpak.append_entry(entry)
				elif not newpak:
					# No patching happened, but the PAK will be overwritten 
					# and the offset of this BSP may have changed within the
					# PAK.
					entry.offset = newoffset
			elif not newpak:
				# If overwriting the existing PAK, copy over non-BSP files
				entry.offset = newoffset
				unmodified = pakfile.read(entry.size)
				tempfile.write(unmodified)
		
		if not newpak:
			# Overwriting PAK file, so it needs a new directory and header
			tempfile.write(pak.get_directory())
			tempfile.seek(quake_pak.PAK_HEADER_OFFSET, os.SEEK_SET)
			tempfile.write(pak.get_header())
		# If writing a separate PAK file in new mode, the writing of that 
		# PAK's header and directory needs to happen somewhere above here in
		# the call stack.
			
		if patchcount > 0:
			return True
		else:
			return False
	
			
def patch_pak(filepath, vispatch, tempfilename, sharedpakfile, newpak):
	if not newpak:
		didpatch = False
		
		# Overwriting existing PAK. Write out contents of PAK to a new
		# temporary file, then replace the old PAK with the new one.
		with open(tempfilename, 'wb') as tempfile:
			tempfile.seek(quake_pak.PAK_HEADER_LEN)
			didpatch = patch_pak_into_file(filepath, vispatch, tempfile)
		
		if didpatch:
			os.rename(tempfilename, filepath)
		else:
			# No patching happened, so get rid of the temp file
			os.delete(tempfilename)
	else:
		# In new mode, so write into the previously opened temporary PAK file
		# and use the shared newpak object.
		patch_pak_into_file(filepath, vispatch, sharedpakfile, newpak)
		
			
def extract_pak(path, vispatch):
	print 'Looking at file %s.' % (os.path.basename(path))
	with open(path, 'rb') as pakfile:
		pak = quake_pak.QuakePak(pakfile)

		pakfile.seek(quake_pak.PAK_HEADER_OFFSET + quake_pak.PAK_HEADER_LEN, 
			os.SEEK_SET)

		for entry in pak.entries:
			# Only operate on the file if it's a .bsp of at least MIN_BSP_SIZE
			if entry.size >= MIN_BSP_SIZE 
					and entry.filename.lower().endswith('.bsp'):
				print 'Looking at file %s.' % (entry.filename)
				bsp = quake_bsp.QuakeBsp(entry.filename, pakfile, 
					entry.offset)

				extract_bsp(bsp, vispatch)
		
				
def patch_file(filename, vispatch, tempfilename, temppakfile, newpak, 
		mapsdir):
	filepath = os.path.join(mapsdir, filename)
				
	if filepath.lower().endswith('.pak'):
		# This is a PAK file
		patch_pak(filepath, vispatch, tempfilename, temppakfile, newpak)
	elif filepath.lower().endswith('.bsp'):
		# This is a BSP file
		patch_bsp_file(filepath, vispatch, tempfilename, newpak, mapsdir)
	
		
def extract_file(filename, vispatch, mapsdir):
	filepath = os.path.join(mapsdir, filename)	
			
	if filepath.lower().endswith('.pak'):
		# This is a PAK file
		extract_pak(filepath, vispatch)
	elif filepath.lower().endswith('.bsp'):
		# This is a BSP file
		extract_bsp_file(filepath, vispatch)
	
			
if __name__ == "__main__":
	try:
		parser = argparse.ArgumentParser(
			formatter_class=argparse.RawDescriptionHelpFormatter,
			description='Quake level patcher for water visibility.\n\n' +\
				COPYRIGHT_NOTICE)
		
		newextractgroup = parser.add_mutually_exclusive_group(required=False);
	
		parser.add_argument('--version', action='version', 
			version='%(prog)s ' + APP_VERSION)
			
		parser.add_argument('-D', '--dir', metavar='DIRECTORY',
			help='''the directory that the level files are in (default: 
				current directory)''')
			
		parser.add_argument('-d', '--data', metavar='VIS_FILE', 
			type=str, default='vispatch.dat',
			help='the vis data file (default: %(default)s)')
		
		newextractgroup.add_argument('-n', '--new', action='store_true',
			help='''instead of overwriting the original level files, if files 
				are inside a .pak create a new .pak with the modified files, 
				else if they are individual .bsp files copy a backup of each 
				old file to name.bak before patching''')
		
		newextractgroup.add_argument('-e', '--extract', action='store_true',
			help='retrieve all the vis data from the given file')
		
		parser.add_argument('file', type=str,
			help='''level filename pattern, .bsp or .pak type, wildcards are
				allowed, relative paths are not allowed''')
				
		args = parser.parse_args()
				
		sys.exit(main(args.file, args.dir, args.data, args.new, args.extract))
	except Exception, err:
		sys.stderr.write('Caught unhandled exception: %s\n' % (str(err)))
		traceback.print_exc(file=sys.stderr)
		sys.exit(1)
		