#COMP 5350-001 
#Project #2 
#Group members: Amod Karki, Marwa Farag 
#REQUIRES Python 3.8 

#Code description
#This code recovers files from a binary disk image. 
#This is done by first locating unique file signatures throughout the disk, recording their offsets, 
# and carving out the file using those offsets.
#---------------------------------------------------------------------------------------------------------------------------------

#main sources: garykessler.net for file signatures, active disk editor for signature documentation, 
# python documentation, lectures for recovery methods & software
#---------------------------------------------------------------------------------------------------------------------------------
from pathlib import Path
from array import *
import re 
from enum import Enum

#"CONSTANTS" ----------------------------------------------------------
#Paths
CURRENTDIR = Path(__file__).parent #dunder/special variable __file__ 
DISKIMG_FILENAME = "Project2Updated.dd"
OUTPUT_FILENAME = "AnalysisOutput.txt"
MATCHES_FILENAME = "MatchResults2_JPG-Trail.txt"
DISKIMG_PATH = CURRENTDIR.joinpath(DISKIMG_FILENAME)
OUTPUT_PATH = CURRENTDIR.joinpath(OUTPUT_FILENAME)
MATCHES_PATH = CURRENTDIR.joinpath(MATCHES_FILENAME)
DISKIMG_SIZE = Path(DISKIMG_PATH).stat().st_size #size of the disk image, in bytes 
#Files 
DISKIMG = open(DISKIMG_PATH, "rb")
OUTPUT_FILE = open(OUTPUT_PATH, "w") #for manual debugging
#Signatures: 2D-Array. Each element is a pair of strings of the format: [<Type of signature>, <Unique hexadecimal signature>]
SIGS_ARR = [["AVI", "52-49-46-46"], ["BMP", "42-4D(?:-[0-9A-F]{2}){4}-00-00"], ["DOCX", "50-4B-03-04-14-00-06-00"], 
        ["GIF", "47-49-46-38-39-61"], ["JPG", "FF-D8-FF-E0"], ["PDF", "25-50-44-46"], ["PNG", "89-50-4E-47-0D-0A-1A-0A"]]

TRAIL_ARR = [["AVI", ""], ["BMP", ""], ["DOCX", ""], 
        ["GIF", ""], ["JPG", "FF-D9(?:-00)*$"], ["PDF", ""], ["PNG", ""]]

seekTrailer = -1

class fileIndices(Enum): #enum values correspond to the file type's location in "SIGS_ARR"
        AVI = 0
        BMP = 1
        DOCX = 2
        GIF = 3
        JPG = 4
        PDF = 5
        PNG = 6

offset = 0 #current byte offset location in disk
progress = 0 #progress made through disk analysis (in percent)
bufsize = 4096 #to load larger amount of bytes at once into the program vs constsantly having to read from OS. speeds up program
matchResults = "" 

#match signatures-- very premature version
def matchSignatures(offset, data): 
        global matchResults #indicating the global var will be changed in this scope
        global seekTrailer  
        i = 0
        regexMatch = []
        while (i < len(SIGS_ARR)): #check for match against all signatures in SIGS_ARR
                fileType = SIGS_ARR[i][0]
                fileSig = SIGS_ARR[i][1]
                if(fileType == SIGS_ARR[fileIndices.BMP.value][0]): #BMP requires regex matching
                        regexMatch = re.findall(fileSig, data) #param 1 contains the regex expression, checks against param2
                else:
                        match = data.find(fileSig)
                if(regexMatch or match != -1): #if any potential signature found
                                result = "Potential " + fileType + " signature found at offset " + str(offset) #str(match + offset)
                                print(result)
                                matchResults += result + "\n"

                                if(i == fileIndices.JPG.value): #only debugging for jpg at this point
                                        seekTrailer = i
                                else: 
                                        seekTrailer = -1 #only debugging for jpg at this point
                                return 
                i += 1

#match trailer for the associated signature
def matchTrailer(offset, data): 
        global matchResults #indicating the global var will be changed in this scope
        fileType = TRAIL_ARR[seekTrailer][0]
        fileTrail = TRAIL_ARR[seekTrailer][1]
        regexMatch = re.findall(fileTrail, data) #param 1 contains the regex expression, checks against param2
        if(regexMatch): 
                result = "Potential " + fileType + " trailer found at line " + str(offset)
                print(result)
                matchResults += result + "\n"

#update disk analysis every progress every 5%
#gets current progress percentage by dividing: (current byte offset/disk image byte size)
def updateProgress(offset):
        global progress
        new_prog = offset/DISKIMG_SIZE * 100
        if(new_prog >= progress + 2): 
                progress = int(new_prog)
                print("Progress: " + str(progress) + " %") 
                if(progress == 100): 
                        print("-- Analysis completed --")

#this loop reads the diskimage and prints it in hex format to output file
#DISKIMG.seek(31621120) #debugging BMP regex quicker by starting from that offset
buf = DISKIMG.read(bufsize)
while buf: #continues looping as long as 'buf' variable is populated
        sliceStart = 0
        SLICE_SIZE = 16
        #debug
        buffLength = len(buf) 
        while (sliceStart < buffLength): 
                line = buf[sliceStart:sliceStart + SLICE_SIZE].hex('-').upper() #16-byte line of the diskimage data in hex format
                matchSignatures(offset, line)
                if(seekTrailer != -1): 
                        matchTrailer(offset, line)
                OUTPUT_FILE.write("Offset " + str(offset) + " | " + line  + "\n")
                offset += SLICE_SIZE
                sliceStart += SLICE_SIZE
                updateProgress(offset)
        buf = DISKIMG.read(bufsize)
OUTPUT_FILE.close()
DISKIMG.close()

#create output file showing matches & match locations
MATCHES_FILE = open(MATCHES_PATH, "w")
MATCHES_FILE.write("-- MATCH RESULTS --\n")
MATCHES_FILE.write(matchResults)
MATCHES_FILE.close()