import time
from collections import defaultdict
import matplotlib.pyplot as plt
from generate_numbered_states import generate_tile_coordinates_np
from A_star import a_star

# Parameters
board_size = 5
num_geoms = 5
bin_size = 10 #how many puzzles per complexity
min_complexity = 5 #smallest complexity to be considered
max_complexity = 25 #highest complexity to be considered

# Generate board states
initial_states, goal_states = generate_tile_coordinates_np(board_size, num_geoms)
print(f"Total solutions: {len(initial_states) ** 2}")

# Initialize bins (defaultdict of lists)
bins = defaultdict(list)

# Start timer
start_time = time.time()
counter = 0
breaking = False

# Loop through board states
for i in initial_states:
    for j in goal_states:
        solution = a_star(board_size, i, j)
        if solution is not None:  # Check if a solution was found
            bins[len(solution)].append(solution)  # Bin by solution length

        counter += 1  # Increment the counter

        if counter % 1000 == 0: #10**4 == 0:
            print(f"{counter} iterations completed, Time taken: {time.time() - start_time:.4f} seconds")
            breaking = True
            break
    if breaking:
        break


# End timer
end_time = time.time()
elapsed_time = end_time - start_time
print(f"Time taken: {elapsed_time:.4f} seconds")

# Plot bin sizes
bin_sizes = {length: len(solutions) for length, solutions in bins.items()}

plt.figure(figsize=(10, 6))
plt.bar(bin_sizes.keys(), bin_sizes.values())
plt.xlabel("Solution Length")
plt.ylabel("Number of Solutions")
plt.title("Distribution of Solution Lengths")
plt.show()

#make directory for puzzles
#sample problems from each bin
#add color shape combination
#generate a json save it to dir