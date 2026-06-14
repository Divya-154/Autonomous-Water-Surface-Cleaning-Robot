import numpy as np
import matplotlib.pyplot as plt


def generate(image, grid_size=5):
    import cv2
    h, w = image.shape[:2]
    cell_h = h // grid_size
    cell_w = w // grid_size

    density = []

    for i in range(grid_size):
        row = []
        for j in range(grid_size):
            cell = image[i*cell_h:(i+1)*cell_h, j*cell_w:(j+1)*cell_w]

            # BLACK = trash
            trash_pixels = np.sum(cell < 128)

            row.append(trash_pixels)
        density.append(row)

    return np.array(density)


def show_heatmap(density):
    plt.imshow(density, cmap='hot', interpolation='nearest')
    plt.title("Trash Density Heatmap")
    plt.colorbar(label="Density")
    plt.show()