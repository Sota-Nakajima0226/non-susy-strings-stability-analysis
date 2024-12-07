import numpy as np
from itertools import combinations, product

def generate_e8_root_vectors():
    root_vectors = []

    # Generate form 1 roots: (±1, ±1, 0, 0, 0, 0, 0, 0)
    indices = combinations(range(8), 2)
    for idx in indices:
        for signs in product([1, -1], repeat=2):
            vec = np.zeros(8)
            vec[idx[0]], vec[idx[1]] = signs
            root_vectors.append(vec)

    # Generate form 2 roots: (±1/2, ±1/2, ±1/2, ±1/2, ±1/2, ±1/2, ±1/2, ±1/2)
    signs = [-1/2, 1/2]
    for bits in range(256):
        vec = np.array([(bits >> i & 1) * signs[1] + (~bits >> i & 1) * signs[0] for i in range(8)])
        if np.sum(vec) % 2 == 0:
            root_vectors.append(vec)
    return root_vectors

# add generate_d16_root_vectors()
