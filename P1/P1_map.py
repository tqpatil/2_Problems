import subprocess
import ray
zen_of_python = subprocess.check_output(["python", "-c", "import this"])
corpus = zen_of_python.split()
num_partitions = 3
chunk = len(corpus) // num_partitions
partitions = [
    corpus[i * chunk: (i + 1) * chunk] for i in range(num_partitions)
]
def map_function(document):
    dic = set()
    for word in document.lower().split():
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
            first_letter = result[0].decode("utf-8")[0]
            word_index = ord(first_letter) % num_partitions
            map_results[word_index].append(result)
    return map_results
map_results = [
    apply_map.options(num_returns=num_partitions)
    .remote(data, num_partitions)
    for data in partitions
]

@ray.remote
def apply_reduce(*results):
    output = set()
    for res in results:
        for key, value in res:
            if key not in output:
                set.add(key)

    return output
outputs = []
for i in range(num_partitions):
    outputs.append(
        apply_reduce.remote(*[partition[i] for partition in map_results])
    )

counts = {k: v for output in ray.get(outputs) for k, v in output.items()}
for count in counts.keys():
    print(f"{count.decode('utf-8')}")