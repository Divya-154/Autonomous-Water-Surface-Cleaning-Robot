import pygame
import time
import numpy as np

ROWS = 5
COLS = 5
CELL_SIZE = 100

WIDTH = COLS * CELL_SIZE + 200
HEIGHT = ROWS * CELL_SIZE


#  HEATMAP → TRASH
def get_trash_from_density(density):
    trash = []
    threshold = np.mean(density)

    for i in range(density.shape[0]):
        for j in range(density.shape[1]):
            if density[i][j] > threshold:
                trash.append((i, j))

    return trash


#  LEGEND FUNCTION 
def draw_legend(screen, robot_img):
    font = pygame.font.SysFont(None, 24)

    x = COLS * CELL_SIZE + 20

    items = [
        ("Robot", (0,255,0)),
        ("Trash", (255,0,0)),
        ("Path", (0,255,255)),
        ("Water", (30,144,255))
    ]

    for i, (text, color) in enumerate(items):
        y = 40 + i*60

        #  Replace green box with robot image
        if text == "Robot":
            robot_icon = pygame.transform.scale(robot_img, (30, 30))
            screen.blit(robot_icon, (x, y))
        else:
            pygame.draw.rect(screen, color, (x, y, 30, 30))

        label = font.render(text, True, (255,255,255))
        screen.blit(label, (x+40, y+5))


def run_simulation(path, density):
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Simulation")

    clock = pygame.time.Clock()

    #LOAD IMAGE
    import os
    import sys

    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    image_path = os.path.join(base_path, "assets", "robot.jpg")

    robot_img = pygame.image.load(image_path)
    robot_img = pygame.transform.scale(robot_img, (70, 70))
    robot_img.set_colorkey((255, 255, 255))

    robot_pos = [0, 0]
    visited = []

    trash = get_trash_from_density(density)

    step = 0

    running = True

    while running:
        screen.fill((30,144,255))  #  water

        # GRID
        for i in range(ROWS):
            for j in range(COLS):
                pygame.draw.rect(screen, (255,255,255),
                                 (j*CELL_SIZE, i*CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

        # PATH
        for (i,j) in visited:
            pygame.draw.rect(screen, (0,255,255),
                             (j*CELL_SIZE+30, i*CELL_SIZE+30, 40, 40))

        # TRASH
        for (i,j) in trash:
            pygame.draw.rect(screen, (255,0,0),
                             (j*CELL_SIZE+20, i*CELL_SIZE+20, 60, 60))

        #  ROBOT
        x = robot_pos[1]*CELL_SIZE + 15
        y = robot_pos[0]*CELL_SIZE + 15
        screen.blit(robot_img, (x, y))

        # CLEAN
        if tuple(robot_pos) in trash:
            trash.remove(tuple(robot_pos))

        #  LEGEND (FIXED)
        draw_legend(screen, robot_img)

        pygame.display.flip()

        # MOVE
        if step < len(path):
            (i,j), _ = path[step]
            robot_pos = [i,j]
            visited.append((i,j))
            step += 1
            time.sleep(0.4)

        # EXIT
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # ESC CLOSE 
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running = False

        clock.tick(30)

    pygame.quit()