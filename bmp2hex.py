#!/usr/bin/env python

##@file bmp2hex.py
#  @ingroup util
#	This is a fork from Robert Gallup
#
#	A script for converting a 1-bit bitmap to HEX for use in an Arduino sketch.
#
#	The BMP format is well publicized. The byte order of the actual bitmap is a
#	little unusual. The image is stored bottom to top, left to right. In addition,
#	The pixel rows are rounded to DWORDS which are 4 bytes long. SO, to convert this
#   to left to right, top to bottom, no byte padding. We have to do some calculations
#	as we loop through the rows and bytes of the image. See below for more
#
#	Usage: 
#	>>>bmp2hex.py [-i] [-w <bytes>] [-b <size-bytes>] <infile> <tablename>
#	
#	@param infile		The file to convert.
#	@param tablename	The name of the table to create
#   @param inverse		"-i", if invert image [optional] 
#	@param tablewidth	"-w <bytes>, The number of characters for each row of the output table [optional]
#	@param sizebytes	"-b <bytes>, Bytes = 0, 1, or 2. 0 = auto. 1 = 1-byte for sizes. 2 = 2-byte sizes (big endian) [optional]
#	
#	@author Robert Gallup 2016-02
#
#	Author:    Robert Gallup (bg@robertgallup.com)
#	License:   MIT Opensource License
#
#	Copyright 2016 Robert Gallup 
#

import sys, array, os, textwrap, math, random, argparse

# Todo:
# Manage the file object to this convert function
# Rename the main function
# Pass the file object as the parameter of the main function
def main ():

	# Default parameters
	infile = ""
	tablename = ""
	tablewidth = 16
	sizebytes = 0
	invert = True

	# Set up parser and handle arguments
	parser = argparse.ArgumentParser()
	parser.add_argument ("infile", help="The 1-bit BMP file to convert")
	parser.add_argument ("tablename", help="The name of the output table")
	parser.add_argument ("-i", "--invert", help="Inverts bitmap pixels", action="store_true")
	parser.add_argument ("-w", "--width", help="Output table width in hex bytes [default: 16]", type=int)
	#parser.add_argument ("-b", "--bytes", help="Byte width of BMP sizes: 0=auto, 1, or 2 (big endian) [default: 0]", type=int)
	args = parser.parse_args()

	# Required arguments
	infile = args.infile
	tablename = args.tablename

	# Options
	if args.invert:
		invert = args.invert
	if args.width:
		tablewidth = args.width
	#if args.bytes:
	#	sizebytes = args.bytes % 3

	# Do the work
	bmp2hex(infile, tablename, tablewidth, invert)

# Utility function. Return a long int from array (little endian)
def getLONG(a, n):
	return (a[n+3] * (2**24)) + (a[n+2] * (2**16)) + (a[n+1] * (2**8)) + (a[n])

# Main conversion function
def bmp2hex(infile, tablename, tablewidth, invert = True):

	invertbyte = 0x00 if invert else 0xFF

	# Convert tablewidth to characters from hex bytes
	tablewidth = int(tablewidth) * 6

	# Initilize output buffer
	outstring =  ''

	# Open File
	fin = open(os.path.expanduser(infile), "rb")
	uint8_tstoread = os.path.getsize(os.path.expanduser(infile))
	valuesfromfile = array.array('B')
	try:
		valuesfromfile.fromfile(fin, uint8_tstoread)
	finally:
		fin.close()

	# Get bytes from file
	values=valuesfromfile.tolist()

	# Calculate and print pixel size
	pixelWidth  = getLONG(values, 18)
	pixelHeight = getLONG(values, 22)

	# Calculate width in words and padded word width (each row is padded to 4-bytes)
	wordWidth   = int(math.ceil(float(pixelWidth)/8.0))
	paddedWidth = int(math.ceil(float(pixelWidth)/32.0) * 4)

	# For auto (sizebytes = 0), set sizebytes to 1 or 2, depending on size of the bitmap
	if (sizebytes==0):
		if (pixelWidth>255) or (pixelHeight>255):
			sizebytes = 2
		else:
			sizebytes = 1

	# Print the include library for Arduino ESP8266

	print ('#include \"imagedata.h\"')
	print ('#include <pgmspace.h>')
	print ('const unsigned char ' + tablename + '[] PROGMEM = {')

	
	# Get offset to BMP data (Byte 10 of the bmp data)
	BMPOffset = getLONG(values, 10)

	# Generate HEX bytes in output buffer
	try:
		for i in range(pixelHeight):
			for j in range (wordWidth):
				ndx = BMPOffset + ((pixelHeight-1-i) * paddedWidth) + j
				outstring += "{0:#04X}".format(values[ndx] ^ invertbyte) + ", "

	# Wrap the output buffer. Print. Then, finish.
	finally:
		outstring = textwrap.fill(outstring[:-2], tablewidth)
		print (outstring)
		print ("};")


# Only run if launched from commandline
if __name__ == '__main__': main()