import itertools
import math
import time

# simulate for "items" at the row level
row_data = [1, 2, 3, 4]
item_count = len(row_data)


# just count the combinations and permutations
for i in range(1, item_count + 1):
    ncomb = math.comb(item_count, i)
    nperm = math.perm(item_count, i)
    print(f"For {i} items:")
    print(f">>>Combinations: {ncomb}")
    print(f">>>Permuations: {nperm}")


# now actually assemble them...


# combinations first
start = time.perf_counter()
for i in range(1, item_count + 1):
    combos = list(itertools.combinations(row_data, i))
    print(f"For {i} items:")
    print(f">>>Combinations: {len(combos)}")
end = time.perf_counter()
print(f"Finished {item_count} items in {end - start}.")
    
# permutations next 
start = time.perf_counter()
for i in range(1, item_count + 1):
    perms = list(itertools.permutations(row_data, i))
    print(f"For {i} items:")
    print(f">>>Permuations: {len(perms)}")
end = time.perf_counter()
print(f"Finished {item_count} items in {end - start}.")
    
