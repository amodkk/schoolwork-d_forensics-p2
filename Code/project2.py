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

#"CONSTANTS" ----------------------------------------------------------
#Signatures
PDF_SIG = "25-50-44-46"

#Paths
CURRENTDIR = Path(__file__).parent #dunder/special variable __file__ 
DISKIMG_FILENAME = "Project2Updated.dd"
OUTPUT_FILENAME = "AnalysisOutput.txt"
DISKIMG_PATH = CURRENTDIR.joinpath(DISKIMG_FILENAME)
OUTPUT_PATH = CURRENTDIR.joinpath(OUTPUT_FILENAME)
DISKIMG_SIZE = Path(DISKIMG_PATH).stat().st_size #size of the disk image, in bytes 
#Files 
DISKIMG = open(DISKIMG_PATH, "rb")
OUTPUT_FILE = open(OUTPUT_PATH, "w") #for manual debugging


offset = 0 #current byte offset location in disk
progress = 0 #progress made through disk analysis (in percent)
bufsize = 4096 #to load larger amount of bytes at once into t he program vs constsantly having to read from OS. speeds up program


#update disk analysis every progress every 5%
def updateProgress(offset):
        global progress
        new_prog = offset/DISKIMG_SIZE * 100
        if(new_prog >= progress + 5): 
                progress = int(new_prog)
                print("Progress: " + str(progress) + " %") 

#match signatures-- very premature version
def matchSignatures(offset, data): 
        match = str(data).find(PDF_SIG)
        if(match != -1): 
                print("Potential PDF found at offset " + str(match + offset))

#this loop reads the diskimage and prints it in hex format to output file
buf = DISKIMG.read(bufsize)
while buf: #continues looping as long as 'buf' variable is populated
        sliceStart = 0
        SLICE_SIZE = 16
        #debug
        buffLength = buf.__len__() 
        while (sliceStart < buffLength): 
                line = buf[sliceStart:sliceStart + SLICE_SIZE].hex('-') #16-byte line of the diskimage data in hex format
                matchSignatures(offset, line)
                #match signatures here
                OUTPUT_FILE.write("Offset " + str(offset) + " | " + line  + "\n")
                offset += SLICE_SIZE
                sliceStart += SLICE_SIZE
                updateProgress(offset)
        buf = DISKIMG.read(bufsize)
OUTPUT_FILE.close()