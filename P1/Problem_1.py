import hashlib
import time
unique= set()
def dedup(inputFile, outputFile): ## inputfile: file pointer, outputfile: file pointer
    for line in inputFile:
        h = hashlib.new('sha256')
        h.update(line.encode())
        hash = h.hexdigest()
        if not (hash in unique):
            outputFile.write(line)
            unique.add(hash)
    return len(unique)
if __name__ == "__main__":
    inputFile = open('input.txt', 'r',encoding="ascii") 
    outputFile = open('output.txt', 'w', encoding="ascii")
    initial = time.time()
    print(dedup(inputFile, outputFile))
    print(f"Total time taken =", time.time()-initial)
    # all_characters = set(chr(i) for i in range(128))
    # with open("input.txt", "w",encoding="ascii") as f:
    #     for i in range(10000):
    #         for char in all_characters:
    #             f.write(char)
    #             f.write("\n")