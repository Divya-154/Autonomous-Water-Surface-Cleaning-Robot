import numpy as np

def plan(density):
    rows, cols = density.shape

    zones = []

    for i in range(rows):
        for j in range(cols):
            zones.append(((i, j), density[i][j]))

    zones.sort(key=lambda x: x[1], reverse=True)

    print("\nCleaning Order:")
    for zone, value in zones:
        print(f"{zone} -> {value}")

    return zones