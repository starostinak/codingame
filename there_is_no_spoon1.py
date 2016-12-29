import sys
import math

# Don't let the machines win. You are humanity's last hope...

width = int(input())  # the number of cells on the X axis
height = int(input())  # the number of cells on the Y axis
array = [input() for i in range(height)]

for i in range(height):
    for j in range(width):
        if array[i][j] == '0':
            left, bottom = None, None
            try:
                left_j = next(k for k in range(j + 1, width) if array[i][k] == '0')
                left = (left_j, i)
            except StopIteration:
                left = (-1, -1)
            try:
                bottom_i = next(k for k in range(i + 1, height) if array[k][j] == '0')
                bottom = (j, bottom_i)
            except StopIteration:
                bottom = (-1, -1)
            print("%i %i %i %i %i %i" % (j, i, left[0], left[1], bottom[0], bottom[1]))
