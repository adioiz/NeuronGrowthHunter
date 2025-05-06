import math
import os
from PIL import Image, ImageDraw
import imageio.v2 as imageio

# Configurations
textname = "1-PKCd-3d-trace.txt"
textname = "temp.txt"
output_dir = "neuron_growth_frames_t"
gif_path = os.path.join(output_dir, "neuron_growth.gif")
total_duration_sec = 5
os.makedirs(output_dir, exist_ok=True) # Ensure output directory exists

# Define constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
IMG_SIZE = 800  # size of output image (square)
LINE_WIDTH = 1  # line thickness

# Load and parse the neuron data
with open(textname, "r") as f:
    lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]

neuron_dict = {} # stores all neurons data
children_map = {} # maps parent to its list of children (for growing branches)
for line in lines:
    row_elements = list(map(float, line.split())) # each line is parsed as: ID TYPE X Y Z RADIUS PARENT_ID
    idx = int(row_elements[0])
    x, y, z = row_elements[2:5]
    radius = row_elements[5]
    parent = int(row_elements[6])
    neuron_dict[idx] = {"idx": idx,"pos": (x, y), "parent": parent}
    if parent != -1:
        children_map.setdefault(parent, []).append(idx)

# Scale coordinates to fit canvas
all_coords = [neuron_dict[i]["pos"] for i in neuron_dict]
xs, ys = zip(*all_coords)
min_x, max_x = min(xs), max(xs)
min_y, max_y = min(ys), max(ys)

def scale(coord):
    """
    for x and y - Normalize to [0,1] range and stretch to image size minus padding
    inverts y to match image coordinates and increase upwards.
    """
    x, y = coord
    scaled_x = int(((x - min_x) / (max_x - min_x)) * (IMG_SIZE - 20) + 10)
    scaled_y = int(((y - min_y) / (max_y - min_y)) * (IMG_SIZE - 20) + 10)
    return scaled_x, IMG_SIZE - scaled_y

# BFS traversal from soma to simulate realistic growth
soma_id = min(neuron_dict.keys())  # assuming lowest ID is soma
visited = []
queue = [soma_id]
while queue:
    curr = queue.pop(0)
    visited.append(curr)
    queue.extend(children_map.get(curr, []))

# Generate images
images = []
frames = []
for i in range(1, len(visited)):
    image = Image.new("L", (IMG_SIZE, IMG_SIZE), color=255)  # grayscale
    draw = ImageDraw.Draw(image)
    for j in range(1, i + 1):
        node_id = visited[j]
        parent_id = neuron_dict[node_id]["parent"]
        if parent_id == -1:
            continue
        x1, y1 = scale(neuron_dict[parent_id]["pos"])
        x2, y2 = scale(neuron_dict[node_id]["pos"])
        draw.line((x1, y1, x2, y2), fill=0, width=LINE_WIDTH)
    frame_path = os.path.join(output_dir, f"frame_{i:04d}.png")
    image.save(frame_path)
    frames.append(imageio.imread(frame_path))

# Save GIF
duration_per_frame = total_duration_sec / len(frames)
imageio.mimsave(gif_path, frames, duration=duration_per_frame)
