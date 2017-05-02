#!/usr/bin/env python
##################################################
##  rmdotfiles.py                               ##
##______________________________________________##
##  Searches for all "dot-files" and "Apple.    ##
##  doubles" from within a subtree path and     ##
##  systematically removes them.                ##
##______________________________________________##
##  Copyright (C) 2017 Walter Arrighetti        ##
##  coding by: Walter Arrighetti, PhD, CISSP    ##
##################################################
_version = "0.7"
import os
import sys
import time
import shutil
import fnmatch

ExcludeFolders = frozenset([
	"System Volume Information","@Recycle","stonefs","sacc_data"
])
ExcludeFiles = frozenset([
])
DotFolders = frozenset([
	".Trashes",".Trash-root",".Trash-0",".Trash-guest",".DS_Store",".hccache",".syncing_db"
	".Spotlight-V100",".fseventsd",".TemporaryItems",
	"$RECYCLE.BIN","$Recycle.Bin","$$PendingFiles"#,"Recycled","RECYCLER"
])
DotFiles = frozenset([
	".DS_Store",".desktop",".Desktop",".Thumbs.db",".dustbust-data","._.Trashes","._.DS_Store",
	"Thumbs.db",
])
DotFileSyntaxes = frozenset([
])
DotFileExts = frozenset([
	"exr","dpx","tif","tiff","ari","mov","mxf","wav","doc","docx","htm","html"
])

def sizeprint(mag, SI=True, decimaldigits=-1, separated=False):
	size, prefix = float(mag), ''
	if SI:
		if size > 1000000000000000L:
			size /= 1000000000000000L
			prefix='P'
		elif size > 1000000000000L:
			size /= 1000000000000L
			prefix='T'
		elif size > 1000000000:
			size /= 1000000000
			prefix='G'
		elif size > 1000000:
			size /= 1000000
			prefix='M'
		elif size > 1024:
			size /= 1000
			prefix='k'
	else:
		if size > 1125899906842624L:
			size /= 1125899906842624L
			prefix='Pi'
		elif size > 1099511627776L:
			size /= 1099511627776L
			prefix='Ti'
		elif size > 1073741824L:
			size /= 1073741824L
			prefix='Gi'
		elif size > 1048576:
			size /= 1048576
			prefix='Mi'
		elif size > 2047:
			size /= 1024
			prefix='ki'
	if decimaldigits<=0:
		if size%1==0 or decimaldigits==0:
			if separated:	return (str(int(size)), prefix)
			else:	return "%d%s"%(int(size),prefix)
		else:
			if prefix in ['M','Mi']:
				if separated:	return ("%.01f"%size, prefix)
				else:	return ("%.01f%s"%(size,prefix))
			elif prefix in ['k','ki']:
				if separated:	return (str(int(math.ceil(size))), prefix)
				else:	return ("%d%s"%(int(math.ceil(size)),prefix))
			else:
				if separated:	return ("%.02f"%size, prefix)
				else:	return ("%.02f%s"%(size,prefix))
	if separated:	return (("%%.%df%"%decimaldigits)%size, prefix)
	else:	return (("%%.%df%%s"%decimaldigits)%(size,prefix))


print "RmDotFiles systematic \"dot-files\" and 'Apple-doubles' removal tool v%s"%_version
print "Copyright (C) 2017 Walter Arrighetti, PhD, CISSP.\n"

if len(sys.argv) not in [2,3] or not os.path.isdir(sys.argv[1]):
	print "\n * SYNTAX:\tRmDotFiles  basepath  [logfile]\n"
	print """            Removes 'dot-files' and macOS 'Apple "doubles"' from a subtree structure.
            Some folders and files are always left in place (like critical filesystem     
            objects like "System Volume Information" or "@Recycle" folders). Some objects 
            are instead *always* removed (like ".Trash-*" folders or ".DS_Store" files),  
            plus all dotfiles starting with '._' and *some* files just starting with ".". 
            The user starting this tool must have permissions to write/delete the objects.
            An optional logfile can be used to record the script actions."""
	print '\n',
	sys.exit(-9)
basepath, log = os.path.abspath(sys.argv[1]), False
if len(sys.argv)==3:
	logfile = os.path.abspath(sys.argv[2])
	try:	log = open(logfile,"a")
	except:
		print " * ERROR: Unable to append to logfile \"%s\"."%logfile
		sys.exit(-2)
print "Analyzing directory structure under \"%s\"....."%basepath,
deletedfiles, deleteddirs, deletedsize = 0,0,0L
errorfiles, errordirs, errorsize = 0,0,0L
dotfilecount, dotdircount = {".*":0}, {}
for key in DotFiles:	dotfilecount[key] = 0
for key in DotFolders:	dotdircount[key] = 0

#from os.path import join, getsize
for root, dirs, files in os.walk(basepath):
	for dir in dirs:
		markforremoval = False
		if dir in ExcludeFolders:	continue
		elif dir in DotFolders:	markforremoval = True
		elif fnmatch.fnmatch(dir,".Trash-[0-9]{3,4}") or fnmatch.fnmatch(dir,"F[oO][uU][nN][dD].[0-9][0-9][0-9]"):	markforremoval = True
		if markforremoval:
			targetdir = os.path.join(root,dir)
			print targetdir+'/'
			try:
				result = shutil.rmtree(targetdir)
				if result==False:	raise IOException
				elif result==True:	deleteddirs += 1
				else:	
					deletedfiles += result[0]
					deleteddirs += result[1]
					deletedsize += result[2]
					if dir in DotFolders:	dotdircount[dir] += 1
			except:
				errordirs += 1
				print "\n Unable to remove folder \"%s\"."%targetdir,
	for file in files:
		markforremoval = False
		if file in ExcludeFiles:	continue
		elif file in DotFiles:	markforremoval = True
		elif fnmatch.fnmatch(file,"._*"):	markforremoval = True
		elif file[0]=='.' and len(file) > 1:
			for syntax in DotFileSyntaxes:
				if fnmatch.fnmatch(file[1:],syntax):
					markforremoval = True;	break
			for dotext in DotFileExts:
				if file.lower().endswith(dotext):
					markforremoval = True;	break
		if markforremoval:
			targetfile = os.path.join(root,file)
			targetsize = os.path.getsize(targetfile)
			if fnmatch.fnmatch(file,"._*") and targetsize>8192:	continue
			try:
				os.remove(targetfile)
				deletedsize += targetsize
				deletedfiles += 1
				if file in DotFiles:	dotfilecount[file] += 1
				elif file[0]=='.':	dotfilecount[".*"] += 1
			except:
				errorsize += targetsize
				errorfiles += 1
				print "\n Unable to remove file \"%s\"."%targetfile,
print '\r'+(' '*78)+"\r"
#time.strftime("%Y%m%d-%H%M")
if (not deletedfiles) and (not deleteddirs) and (not deletedsize):	
	print "No filesystem objects were deleted from \"%s\"."%basepath
	if log: log.write("[RmDotFiles] %s:\tNo filesystem objects were deleted.\r\n"%time.strftime("%Y%m%d-%H%M"))
else:
	outstr = "Purged %d files and %d folders (%0.2f GiB) from \"%s\"."%(deletedfiles,deleteddirs,float(deletedsize)/(1024*1024*1024),basepath)
	print outstr
	if log: log.write("[RmDotFiles] %s:\t%s\r\n"%(time.strftime("%Y%m%d-%H%M"),outstr))
	for key in DotFolders:
		if dotdircount[key]:	print 'Deleted %d "%s" folders.'%(dotdircount[key],key)
	for key in DotFiles:
		if dotfilecount[key]:	print 'Deleted %d "%s" files.'%(dotfilecount[key],key)
	if dotfilecount[".*"]:	print "Deleted %d other 'dot-files'."%dotfilecount[".*"]
if errorfiles or errordirs:
	outstr = "Note: %d files and %d folders (%0.2f GiB) could NOT be deleted.\n"%(errorfiles, errordirs,float(errorsize)/(1024*1024*1024))
	print outstr
	if log: log.write("[RmDotFiles] %s:\t%s\r\n"%(time.strftime("%Y%m%d-%H%M"),outstr))

if log:	log.close()
sys.exit(0)
