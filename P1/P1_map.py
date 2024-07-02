import subprocess
import ray
import sys
import os
# zen_of_python = subprocess.check_output(["python", "-c", "import this"])
# corpus = zen_of_python.split()
# num_partitions = 3
# chunk = len(corpus) // num_partitions

def map_function(document):
    dic = set()
    for word in document:
        if word in dic:
            yield word,0
        else:
            dic.add(word)
            yield word,1
@ray.remote
def apply_map(corpus, num_partitions=3):
    map_results = [list() for _ in range(num_partitions)]
    for document in corpus:
        for result in map_function(document):
            first_letter = result[0][0]
            word_index = ord(first_letter) % num_partitions
            map_results[word_index].append(result)
    return map_results
@ray.remote
def apply_reduce(*results):
    output = set()
    for res in results:
        for key, value in res:
            if key not in output:
                output.add(key)

    return output
if __name__ == "__main__":
    if(len(sys.argv)< 3):
        print("Please pass in input file path and output file path as arguments")
        sys.exit()
    inFilePath =sys.argv[1]
    outFilePath = sys.argv[2] 
    if not (os.path.exists(inFilePath)):
        print("Error: input file doesn't exist")
        sys.exit()
    num_cpus = 4
    ray.init(num_cpus=num_cpus)
    inputFile = open(inFilePath, 'r',encoding="ascii") 
    outputFile = open(outFilePath, 'w', encoding="ascii")
    data = inputFile.read().split('\n')
    num_partitions = 3
    chunk = len(data) // num_partitions
    partitions = [
    data[i * chunk: (i + 1) * chunk] for i in range(num_partitions)
    ]
    map_results = [
    apply_map.options(num_returns=num_partitions)
    .remote(data, num_partitions)
    for data in partitions
    ]

    outputs = []
    for i in range(num_partitions):
        outputs.append(
            apply_reduce.remote(*[partition[i] for partition in map_results])
        ) 

    counts = set([item for output in ray.get(outputs) for item in output])
    for count in counts:
        outputFile.write(count + "\n")
    ray.shutdown()
    