#COMP 5350-001 
#Project #2 
#Group members: Amod Karki, Marwa Farag 
#REQUIRES Python 3.8 

#Code description
#This code recovers files from a binary disk image. 
#This is done by first locating unique file signatures throughout the disk, recording their offsets, 
# and carving out the file using those offsets.
#Note: This code's signature searching functionality is tailored to this project, 
# meaning that the code will not be testing against ALL existing variations of each file's signature(s). 
#---------------------------------------------------------------------------------------------------------------------------------

#main sources: garykessler.net for file signatures, active disk editor for signature documentation, 
# python documentation, lectures for recovery methods & software
#---------------------------------------------------------------------------------------------------------------------------------
from pathlib import Path
from array import *
import re 
from enum import Enum


#Paths
CURRENTDIR = Path(__file__).parent #dunder/special variable __file__ 
DISKIMG_FILENAME = "Project2Updated.dd"
OUTPUT_FILENAME = "AnalysisOutput.txt"
MATCHES_FILENAME = "MatchResults.txt"
DISKIMG_PATH = CURRENTDIR.joinpath(DISKIMG_FILENAME)
DISKIMG_SIZE = Path(DISKIMG_PATH).stat().st_size #size of the disk image, in bytes 
OUTPUT_PATH = CURRENTDIR.joinpath(OUTPUT_FILENAME) #for manual debugging 
MATCHES_PATH = CURRENTDIR.joinpath(MATCHES_FILENAME) #for manual debugging


#File Streams
DISKIMG = open(DISKIMG_PATH, "rb")
OUTPUT_FILE = open(OUTPUT_PATH, "w") #for manual debugging


#2D-Array of files' unique header & footer sigs 
#Each element is a set of 3 strings following the format: [<file type>, <Unique header sig>, <uniq footer sig>]
HDR_FTR_ARR = [["AVI", "^52-49-46-46", "null"], 
        ["BMP", "^42-4D(?:-[0-9A-F]{2}){4}-00-00", "null"], 
        ["DOCX", "^50-4B-03-04-14-00-06-00", "50-4B-05-06"], 
        ["GIF", "^47-49-46-38-39-61", "00-00-3B"], 
        ["JPG", "^FF-D8-FF-E0", "FF-D9"], 
        ["MPG", "^00-00-01-B(?:3|A)", "00-00-01-B(?:7|9)(?:-00)*$"], 
        ["PDF", "^25-50-44-46", "25-25-45-4F-46"], 
        ["PNG", "^89-50-4E-47-0D-0A-1A-0A", "49-45-4E-44-AE-42-60-82"]]

#Dirty solution for MPG Trailing Zeroes
TRAILING_ZEROES_RE = "(?:-00)*$"

#Identifies indices of the files in HDR_FTR_ARR
class fileIndx(Enum): #enum values correspond to the file type's location in "SIGS_ARR"
        AVI = 0
        BMP = 1
        DOCX = 2
        GIF = 3
        JPG = 4
        MPG = 5
        PDF = 6
        PNG = 7


offset = 0 #current byte offset location in disk
progress = 0 #progress made through disk analysis (in percent)
bufsize = 4096 #to load larger amount of bytes at once into the program vs constsantly having to read from OS. speeds up program
matchResults = "" 
seekFootSig = -1


#Summary: takes in a hex string, slices it from 'start' to 'end', slice is interpreted as little-endian order. 
# The slice is then converted to decimal format and returned. 
def littleEndianHexToDec(hexStr, start, end):
        headerLine = hexStr.replace("-", " ") 
        hex_bArr = bytearray.fromhex(headerLine)[start:end] 
        hex_bArr.reverse() #change to big endian, needed bytearray for this operation
        decSize = int(hex_bArr.hex(), 16) #byte size of file in decimal format
        return decSize


#match signatures-- very premature version
def matchHeaderSigs(offset, data): 
        global matchResults #indicating the global var will be changed in this scope
        global seekFootSig  
        i = 0
        regexMatch = []
        while (i < len(HDR_FTR_ARR)): #check for match against all signatures in SIGS_ARR
                fileType = fileIndx(i).name
                fileSig = HDR_FTR_ARR[i][1] 
                regexMatch = re.findall(fileSig, data) #param 1 contains the regex expression, checks against param2
                if(regexMatch): #if any potential signature found
                        result = fileType + " signature offset: " + str(offset) #str(match + offset)
                        print(result)
                        matchResults += result + "\n"
                        seekFootSig = i
                        return 
                i += 1


#match trailer for the associated signature
#result is a string that will be printed to terminal for debugging
def matchFooterSigs(offset, data): 
        global matchResults #indicating the global var will be changed in this scope
        global seekFootSig
        endSeek = False
        offsetAdjust = 0
        fileType = fileIndx(seekFootSig).name
        footerSig = HDR_FTR_ARR[seekFootSig][2]
        if(seekFootSig == -1): 
                return
        #AVI, BMP
        if(seekFootSig in (fileIndx.AVI.value, fileIndx.BMP.value)):  
                if(seekFootSig == fileIndx.AVI.value): 
                        decSize = littleEndianHexToDec(data, 4, 8)
                        offsetAdjust = decSize + 7 #for AVI, data size indicates bytes AFTER the first 7 bytes of header
                else: #BMP  
                        decSize = littleEndianHexToDec(data, 2, 6)
                        offsetAdjust = decSize - 1
                result = fileType + " ending offset: " + str(offset + offsetAdjust) + " (inclusive)"
                endSeek = True

        #Everything else: DOCX, GIF, JPG, MPG, PDF, PNG, MPG
        else:
                regexMatch = re.findall(footerSig, data)
                if(regexMatch):
                        if(seekFootSig == fileIndx.MPG.value): #brain fart theres probably a much simpler way to do this
                                footerSig = regexMatch[0] 
                                trailingZerosRE = re.findall(TRAILING_ZEROES_RE, footerSig)
                                if(trailingZerosRE):
                                        trailingZeroesBytes = bytes.fromhex(trailingZerosRE[0].replace("-", " "))
                                        offsetAdjust -= len(trailingZeroesBytes) #subtract these number of trailing zeroes' bytes from file ending offset
                        #adjusting offset
                        footerLineBytes = bytes.fromhex(data.replace("-", " "))
                        footerSigBytes = bytes.fromhex(footerSig.replace("-", " "))
                        preFSigBytes = footerLineBytes.find(footerSigBytes) #number of bytes before footer sig
                        fSigBytes = len(footerSigBytes) #number of bytes of footer sig
                        offsetAdjust += preFSigBytes + fSigBytes - 1
                        if(seekFootSig == fileIndx.DOCX.value): 
                                offsetAdjust += 18 #DOCX files have an additional 18 bytes after the trailer sequence
                        result = fileType + " ending offset: " + str(offset + offsetAdjust) + " (inclusive)"
                        endSeek = True
        if(endSeek): 
                print(result)
                matchResults += result + "\n\n"
                seekFootSig = -1


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


#DEBUG LINES
#ISKIMG.seek(49859296) #debugging BMP regex quicker by starting from that offset
#offset = 49859296


#this loop reads the diskimage and prints it in hex format to output file
buf = DISKIMG.read(bufsize)
while buf: #continues looping as long as 'buf' variable is populated
        sliceStart = 0
        SLICE_SIZE = 16
        #debug
        buffLength = len(buf) 
        #this loop will analyze the buffer in 16-byte segments.
        while (sliceStart < buffLength): 
                line = buf[sliceStart:sliceStart + SLICE_SIZE].hex('-').upper() #16-byte line of the diskimage data in hex format
                matchHeaderSigs(offset, line)
                if(seekFootSig != -1): 
                        matchFooterSigs(offset, line)
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
print("-- See output file 'MatchResults' for manual debugging --")