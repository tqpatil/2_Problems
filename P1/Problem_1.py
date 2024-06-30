import hashlib
import time
import sys
import os
import subprocess
unique= set()
def dedup(inputFile, outputFile): ## inputfile: file pointer, outputfile: file pointer
    for item in inputFile:
        h = hashlib.new('sha256') ## sha256 encoded hash (may lead to memory problems but reduces collisions)
        h.update(item.encode())
        hash = h.hexdigest()
        if not (hash in unique):
            outputFile.write(item)
            unique.add(hash)
    return len(unique)
if __name__ == "__main__":
    if(len(sys.argv)< 3):
        print("Please pass in input file path and output file path as arguments")
        sys.exit()
    inFilePath =sys.argv[1]
    outFilePath = sys.argv[2] 
    if not (os.path.exists(inFilePath)):
        print("Error: input file doesn't exist")
        sys.exit()
    inputFile = open(inFilePath, 'r',encoding="ascii") 
    outputFile = open(outFilePath, 'w', encoding="ascii")
    initial = time.time()
    print("Total unique items:", dedup(inputFile, outputFile))
    print(f"Total time taken =", time.time()-initial)



    # all_characters = set(chr(i) for i in range(128))
    # with open("input.txt", "w",encoding="ascii") as f:
    #     for i in range(10000):
    #         for char in all_characters:
    #             f.write(char)
    #             f.write("\n")