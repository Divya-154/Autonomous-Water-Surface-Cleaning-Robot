import cv2
import numpy as np

def generate_multiview_heatmap(image_paths, grid_size=5):
    combined_grid = np.zeros((grid_size, grid_size))

    for file in image_paths:
        img = cv2.imread(file)
        img = cv2.resize(img, (500, 500))

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        h, w = gray.shape
        cell_h = h // grid_size
        cell_w = w // grid_size

        for i in range(grid_size):
            for j in range(grid_size):
                cell = gray[
                    i*cell_h:(i+1)*cell_h,
                    j*cell_w:(j+1)*cell_w
                ]

                trash_pixels = np.sum(cell < 120)
                combined_grid[i, j] += trash_pixels

    # Normalize
    combined_grid = combined_grid / combined_grid.max()

    return combined_grid