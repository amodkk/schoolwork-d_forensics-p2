#COMP 5350-001 
#Project #2 
#Group members: Amod Karki, Marwa Farag 

#Code description
#This code recovers files from a binary disk image. 
#This is done by first locating unique file signatures throughout the disk, recording their offsets, and carving out the file using those offsets.
#---------------------------------------------------------------------------------------------------------------------------------

#Sources: garykessler.net for file signatures, lectures for recovery methods & software
#---------------------------------------------------------------------------------------------------------------------------------
from pathlib import Path

#Get paths right  IDE has different working directory for some reason
CURRENTDIR = Path(__file__).parent #dunder/special variable __file__ 
DISKIMG = "Project2Updated.dd"
OUTPUTFILE = "AnalysisOutput.txt"
DISKIMG_PATH = CURRENTDIR.joinpath(DISKIMG)
OUTPUT_PATH = CURRENTDIR.joinpath(OUTPUTFILE)
#debug
#print(DISKIMG_PATH)
f = open(DISKIMG_PATH, "rb")
#output_file is really for manual debugging, as we can't scroll all the way up on this huge output 
output_file = open(OUTPUT_PATH, "w")

#offset represents the exact current byte offset location in the disk. updates as we progress through the disk image
offset = 0
offset_str = "" 
#bufsize represents the number of bytes that will be loaded into buf at a time. makes the program faster this way, vs constantly having to read from the OS.
#readlines() will then interate through that data/bytes. when the end of that is reached, <bufsize> number of bytes will be read in again. 
bufsize = 4096
buf = f.readlines(bufsize)

#this loop was able to reach all the way to the end of the file!! =D, somewhat neatly displaying current offset and byte length. 
#was able to compare with active disk editor to confirm. 
#now to incorporate regex
while buf: 
        for line in buf: #line is of type 'bytes'
                offset_str = "Current offset: " + str(offset)
                bytes_len = "Bytes (line length): " + str(line.__len__())
                output = offset_str + "\n" + bytes_len + "\n" + str(line) + "\n"
                print(output)
                output_file.write(output + "\n")
                offset += line.__len__() #update offset before moving 
        buf = f.readlines(bufsize) #***make sure this line is indented to fall under the while loop, not under the inner for loop!
output_file.close()

#short version for debugging
#for x in range(0, 2): 
#        for line in buf:
#                offset_str = "Current offset: " + str(offset)
#                bytes_len = "Bytes (line length): " + str(line.__len__())
#                output = offset_str + "\n" + bytes_len + "\n" + str(line) + "\n"
#                print(output)
#                output_file.write(output + "\n")
#                offset += line.__len__() #update offset before moving 
#        buf = f.readlines(bufsize)
#output_file.close()