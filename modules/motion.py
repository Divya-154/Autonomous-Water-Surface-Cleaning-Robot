import cv2
import time
import random

def move_robot_visual(image, path, update_time_callback=None):
    #Base image
    base = cv2.resize(image, (500, 350))
    h, w, _ = base.shape
    cell_h = h // 5
    cell_w = w // 5

    # Living objects → 2 random cells
    all_cells = [(i, j) for i in range(5) for j in range(5)]
    living_objects = random.sample(all_cells, 2)
    print("Living objects at:", living_objects)

    #  Hidden failure flag
    failure_flag = False

    start_time = time.time()
    total_time = len(path) * 0.4  # example total time

    for step, ((i, j), value) in enumerate(path):
        display = base.copy()

        # Draw visited cells
        for k in range(step + 1):
            ii, ij = path[k][0]
            xk = ij * cell_w
            yk = ii * cell_h
            cv2.rectangle(display, (xk, yk), (xk + cell_w, yk + cell_h), (0, 255, 0), 2)

        # Draw robot
        cx = j * cell_w + cell_w // 2
        cy = i * cell_h + cell_h // 2
        cv2.circle(display, (cx, cy), 8, (255, 0, 0), -1)

        #  Living object detection print
        if (i, j) in living_objects:
            print(f"Living object detected at ({i},{j})")

        # Hidden failure
        if not failure_flag and random.random() < 0.1:
            print("Failure internally detected (handled safely)")
            failure_flag = True

        #  Real-time ETA
        if update_time_callback:
            elapsed = time.time() - start_time
            remaining = total_time - elapsed
            update_time_callback(elapsed, max(0, remaining))

        cv2.imshow("Robot", display)
        cv2.waitKey(300)

    cv2.destroyAllWindows()