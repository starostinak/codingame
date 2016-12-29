import sys
import math

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

# w: width of the building.
# h: height of the building.
w, h = [int(i) for i in input().split()]
n = int(input())  # maximum number of turns before game over.
x, y = [int(i) for i in input().split()]

x_min, x_max = 0, w
y_min, y_max = 0, h

# game loop
while True:
    bomb_dir = input()  # the direction of the bombs from batman's current location (U, UR, R, DR, D, DL, L or UL)
    print(str((x_min, x_max)) + " " + str((y_min, y_max)), file = sys.stderr)

    if 'U' in bomb_dir:
        y_max = y
    elif 'D' in bomb_dir:
        y_min = y
    else:
        y_min = y
        y_max = y + 1
    if 'R' in bomb_dir:
        x_min = x
    elif 'L' in bomb_dir:
        x_max = x
    else:
        x_min = x
        x_max = x + 1
    
    x = int((x_max + x_min) / 2)
    y = int((y_max + y_min) / 2)
    print(str(x) + " " + str(y))

