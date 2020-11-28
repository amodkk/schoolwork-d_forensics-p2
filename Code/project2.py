#COMP 5350-001 
#Project #2 
#Group members: Amod Karki, Marwa Farag 
#REQUIRES Python 3.8 

#Code description
#This code recovers files from a binary disk image. 
#This is done by first locating unique file signatures throughout the disk, recording their offsets, and carving out the file using those offsets.
#---------------------------------------------------------------------------------------------------------------------------------

#Sources: garykessler.net for file signatures, lectures for recovery methods & software
#---------------------------------------------------------------------------------------------------------------------------------
from pathlib import Path

#CONSTANTS ----------------------------------------------------------
#Get paths right  IDE has different working directory for some reason
CURRENTDIR = Path(__file__).parent #dunder/special variable __file__ 
DISKIMG = "Project2Updated.dd"
OUTPUTFILE = "AnalysisOutput_Hex.txt"
DISKIMG_PATH = CURRENTDIR.joinpath(DISKIMG)
OUTPUT_PATH = CURRENTDIR.joinpath(OUTPUTFILE)
DISKIMG_SIZE = Path(DISKIMG_PATH).stat().st_size #size of the disk image, in bytes 

#SIGNATURES
PDF_SIG = "25-50-44-46"

#debug
#print(DISKIMG_PATH)
diskImg = open(DISKIMG_PATH, "rb")
#output_file is really for manual debugging, as we can't scroll all the way up on this huge output 
outputFile = open(OUTPUT_PATH, "w")

offset = 0 #current byte offset location in disk
progress = 0 #progress made through disk analysis (in percent)
bufsize = 4096 #to load larger amount of bytes at once into t he program vs constsantly having to read from OS. speeds up program
buf = diskImg.readlines(bufsize)

#update disk analysis every progress every 5%
def updateProgress(offset):
        global progress
        new_prog = offset/DISKIMG_SIZE * 100
        if(new_prog >= progress + 5): 
                progress = new_prog
                print("Progress: " + str(progress) + " %")

#writes diskImg information to file in hex format
def writeToFile(offset, bytes_len, outputFile): 
        offset_str = "Current offset: " + str(offset)
        bytes_len = "Bytes (line length): " + str(line.__len__())
        output = offset_str + "\n" + bytes_len + "\n" + line.hex("-") + "\n" #now its all as hex, as in active desk editor
        #print(output) #debugging purposes
        outputFile.write(output + "\n")

#goes through the lines of the diskimage and prints it in hex format to output file
while buf: 
        for line in buf: #line is of type 'bytes'
                writeToFile(offset, line.__len__(), outputFile)
                updateProgress(offset)
                offset += line.__len__() #update offset before moving 
        buf = diskImg.readlines(bufsize) #***make sure this line is indented to fall under the while loop, not under the inner for loop!
outputFile.close()

"""
#debugging version
for x in range(0, 8000): 
        for line in buf:
                offset_str = "Current offset: " + str(offset)
                bytes_len = "Bytes (line length): " + str(line.__len__())
                #output_1 = offset_str + "\n" + bytes_len + "\n" + str(line) + "\n" #raw interpretation is a mixture of bytes and ascii
                output_2 = offset_str + "\n" + bytes_len + "\n" + line.hex("-") + "\n" #now its all as hex, as in active desk editor
                #print(output_1)
                #print(output_2)
                updateProgress(offset)
                #output_file.write(output + "\n")
                offset += line.__len__() #update offset before moving 
        buf = f.readlines(bufsize)
output_file.close()
"""