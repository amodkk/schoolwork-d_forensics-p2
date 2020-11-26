#COMP 5350-001 
#Project #2 
#Group members: Amod Karki, Marwa Farag 

#Code description
#This code recovers files from a binary disk image. 
#This is done by first locating unique file signatures throughout the disk, recording their offsets, and carving out the file using those offsets.
#---------------------------------------------------------------------------------------------------------------------------------

#Sources: garykessler.net for file signatures, lectures for recovery methods & software
#---------------------------------------------------------------------------------------------------------------------------------

f = open("Project2Updated.dd", "rb")

#offset represents the exact current byte offset location in the disk. updates as we progress through the disk image
offset = 0
#bufsize represents the number of bytes that will be loaded into buf at a time. makes the program faster this way, vs constantly having to read from the OS.
#readlines() will then interate through that data/bytes. when the end of that is reached, <bufsize> number of bytes will be read in again. 
bufsize = 4096
buf = f.readlines(bufsize)
print(type(buf))


#this loop was able to reach all the way to the end of the file!! =D, somewhat neatly displaying current offset and byte length. 
#was able to compare with active disk editor to confirm. 
#now to incorporate regex
while buf: 
        for line in buf: #line is of type 'bytes'
                print("Current offset: " + str(offset))
                offset += line.__len__()
                print("Bytes (line length): " + str(line.__len__()))
                print(line)
                print("\n")
        buf = f.readlines(bufsize)

#while buf:
#    for line in buf:
        #do search stuff
        #totalBytes += line.__len__()
        #print(line.__len__())
#        print(line)
        #buf = f.readlines(bufsize)

