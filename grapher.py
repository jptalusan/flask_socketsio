import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime


list = ["0 nodes.txt", "1 nodes.txt", "2 nodes.txt", "3 nodes.txt", "4 nodes.txt", "5 nodes.txt"]
title_list = ["local", "1 node", "2 nodes", "3 nodes", "4 nodes", "5 nodes"]
frame_array = []
data_array = []

for f in list:
    _f = open(f, 'r')
    x = _f.readlines()
    frame_array.append(x)

for i, array in enumerate(frame_array):
    start_stamp = datetime.strptime(array[0].strip(), '%Y-%m-%d %H:%M:%S.%f')
    end_stamp = datetime.strptime(array[len(array) - 2].strip(), '%Y-%m-%d %H:%M:%S.%f')
    print(list[i])
    elapsed = (end_stamp - start_stamp).total_seconds()
    frames = len(array)
    fps = round((frames/elapsed), 2)
    print(fps)
    data_array.append(fps)

fig = plt.figure()
plt.grid(True)
fig.suptitle('Effect of number of nodes on frames per second', fontsize=16)
width = .35
ind = np.arange(len(data_array))
plt.bar(ind, data_array, width=width)
plt.xticks(ind + width / 2, title_list)
plt.xlabel('number of nodes', fontsize=14)
plt.ylabel('frames per second', fontsize=14)
fig.autofmt_xdate()

plt.savefig("figure.png")