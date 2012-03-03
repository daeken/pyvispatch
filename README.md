# pyvispatch

## Introduction

pyvispatch is a tool which patches levels for the original
[Quake](https://en.wikipedia.org/wiki/Quake_(video_game)) to give them
transparent water in GLQuake and [many](http://ezquake.sourceforge.net/)
[modern](http://quakeone.com/proquake/) [clients](http://icculus.org/twilight/darkplaces/). This is accomplished by
reading in new visibility data from small patch files and replacing the older
information within the original levels. pyvispatch can patch both standalone BSP files as well as levels stored in Quake PAKs.

This tool is a full re-implementation of the original
[VisPatch](http://vispatch.sourceforge.net/) utility, authored by Andy Bay and
enhanced by O.Sezer, in Python. pyvispatch was created to:
* Reduce some limitations of the original VisPatch such as relative directory handling
* Address bugs in the output of PAK files
* Make it easier to extend the tool or include it with other applications
* Provide a basis for other Quake tools that I would like to write and enhance

## Usage

`vispatch.py [-h] [--version] [-D DIRECTORY] [-d VIS_FILE] [-n | -e] file`

positional arguments:

*	file
	> level filename pattern, .bsp or .pak type, wildcards
	> are allowed, relative paths are not allowed

optional arguments:

*	-h, --help
	> show this help message and exit
	
*	--version
	> show program's version number and exit
	
*	-D DIRECTORY, --dir DIRECTORY
	> the directory that the level files are in (default: current directory)
	
*	-d VIS_FILE, --data VIS_FILE
	> the vis data file (default: vispatch.dat)
	
*	-n, --new
	> instead of overwriting the original level files, if files are inside a
	> .pak create a new .pak with the modified files, else if they are
	> individual .bsp files copy a backup of each old file to name.bak before
	> patching
	
*	-e, --extract
	> retrieve all the vis data from the given file

## License

Copyright &copy; 1996-1997 [Id Software, Inc.](http://www.idsoftware.com/)  
Copyright &copy; 1997-2006 Andy Bay <IMarvinTPA@bigfoot.com>  
Copyright &copy; 2007-2011 O.Sezer <sezero@users.sourceforge.net>  
Copyright &copy; 2012 John Trainer <n@nightmiles.org>

pyvispatch comes with ABSOLUTELY NO WARRANTY. This is free software, and you
are welcome to redistribute it under certain conditions; see COPYING for
details.