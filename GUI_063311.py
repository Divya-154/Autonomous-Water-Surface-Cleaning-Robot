import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import numpy as np

from modules import vision, heatmap, planner, motion, obstacle, multiview, simulation

# ---------------- GLOBALS ----------------
image = None
mask = None
density = None
path = None

battery = 100
trash_collected = 0
bin_fill = 0
status_text = "Idle"

#Redirect messages
import sys

class PrintRedirector:
    def write(self, message):
        if message.strip():
            try:
                log_box.after(0, lambda: log_box.insert(tk.END, message))
                log_box.after(0, log_box.see, tk.END)
            except:
                pass

    def flush(self):
        pass
#----Log Messages For App----
def log(message):
    log_box.insert(tk.END, message + "\n")
    log_box.see(tk.END)
    log_box.pack(pady=5)
    sys.stdout = PrintRedirector()

# ---------------- SHOW IMAGE ----------------
def show_image(img):
    if img is None:
        log("Empty image ")
        return

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    img = img.resize((500, 350))

    img_tk = ImageTk.PhotoImage(img)
    panel.config(image=img_tk)
    panel.image = img_tk


# ---------------- DASHBOARD UPDATE ----------------
def update_dashboard():
    battery_label.config(text=f"Battery: {battery}%")
    trash_label.config(text=f"Trash: {trash_collected}")
    bin_bar['value'] = bin_fill
    status_label.config(text=f"Status: {status_text}")

    log_box.insert(tk.END, f"{status_text}\n")
    log_box.see(tk.END)


# ---------------- TIME UPDATE ----------------
def update_time(elapsed, eta):
    time_label.config(text=f"Time: {elapsed:.1f}s")
    eta_label.config(text=f"ETA: {eta:.1f}s")
    root.update_idletasks()


# ---------------- LOAD IMAGE ----------------
def load_image():
    global image, mask, density, path

    import os
    import sys
    import cv2

    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    image_path = os.path.join(base_path, "data", "water.jpg")

    print("BASE PATH:", base_path)
    print("FULL IMAGE PATH:", image_path)
    print("FILE EXISTS:", os.path.exists(image_path))

    #  LOAD IMAGE (THIS WAS MISSING)
    image_loaded = cv2.imread(image_path)

    if image_loaded is None:
        log("Image not found")
        return

    image = image_loaded

    # RESET OLD DATA
    mask = None
    density = None
    path = None

    show_image(image)  


# ---------------- DETECT TRASH ----------------
def detect_trash():
    global mask

    if image is None:
        log("No image loaded")
        return

    boxed = vision.detect_trash_boxes(image.copy())

    if boxed is None:
        log("Detection failed ")
        return

    show_image(boxed)

    # optional (for heatmap)
    mask = vision.detect_trash_mask(image)

# ---------------- HEATMAP ----------------
def generate_heatmap():
    global density

    if mask is None:
        return

    density = heatmap.generate(mask)
    show_heatmap()


# ---------------- SHOW HEATMAP ----------------
def show_heatmap():
    global density

    heat = cv2.normalize(density, None, 0, 255, cv2.NORM_MINMAX)
    heat = np.uint8(heat)

    grid_size = density.shape[0]
    cell_w = 400 // grid_size
    cell_h = 300 // grid_size

    heat = cv2.resize(heat, (400, 300), interpolation=cv2.INTER_NEAREST)
    heat = cv2.applyColorMap(heat, cv2.COLORMAP_JET)

    for i in range(grid_size):
        for j in range(grid_size):
            value = int(density[i][j])
            x = j * cell_w + 10
            y = i * cell_h + 30

            cv2.putText(heat, str(value),
                        (x, y),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255,255,255), 1)

    legend = np.zeros((300, 200, 3), dtype=np.uint8)

    cv2.rectangle(legend, (10, 20), (40, 50), (0, 0, 255), -1)
    cv2.putText(legend, "High", (50, 45),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1)

    cv2.rectangle(legend, (10, 90), (40, 120), (0, 255, 255), -1)
    cv2.putText(legend, "Medium", (50, 115),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1)

    cv2.rectangle(legend, (10, 160), (40, 190), (255, 0, 0), -1)
    cv2.putText(legend, "Low", (50, 185),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1)

    combined = np.hstack((heat, legend))
    show_image(combined)


# ---------------- PLAN PATH ----------------
# ---------------- PLAN PATH ----------------
def plan_path():
    global path

    if density is None:
        log("No heatmap available")
        return

    try:
        # Get path from planner
        path = planner.plan(density)
        log("PLAN FUNCTION CALLED")

        # Debugging: show path in GUI
        if path is not None and len(path) > 0:
            log("Path planned successfully")
            log("Cleaning Order:")
            for i, step in enumerate(path):
                try:
                    # Handles ((0,2), value)
                    if isinstance(step, tuple) and isinstance(step[0], tuple):
                        coord = step[0]
                    else:
                        coord = step
                except:
                    coord = step

                log(f"{i+1}. {coord}")
        else:
            log("Path planning failed")

    except Exception as e:
        log(f"Error in path planning: {e}")
# ---------------- ROBOT ----------------
def start_robot():
    global battery, trash_collected, bin_fill, status_text

    if image is None or path is None or density is None:
        return

    status_text = "Running"
    update_dashboard()

    #  GUI animation (BLUE DOT + ETA)
    motion.move_robot_visual(
        image.copy(),
        path,
        update_time_callback=update_time
    )

    # Pygame simulation (separate window)
    simulation.run_simulation(path, density)

    battery -= 10
    trash_collected += len(path)
    bin_fill += 30

    status_text = "Completed"
    update_dashboard()

# ---------------- MULTIVIEW ----------------
def multi_view():
    global density

    image_paths = [
        "data/water1.jpeg",
        "data/water2.jpeg",
        "data/water3.jpeg",
        "data/water4.jpeg"
    ]

    density = multiview.generate_multiview_heatmap(image_paths)
    show_heatmap()


# ---------------- RUN ALL ----------------
def run_all():
    load_image()
    detect_trash()
    generate_heatmap()
    plan_path()
    start_robot()


# ================= GUI =================
root = tk.Tk()
root.title("AquaClean AI System")
root.geometry("1200x600")

main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True)

# LEFT SIDE
left_frame = tk.Frame(main_frame)
left_frame.pack(side="left", fill="both", expand=True)

panel = tk.Label(left_frame)
panel.pack(pady=10)

btn_frame = tk.Frame(left_frame)
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="Load Image", width=15, command=load_image).grid(row=0, column=0)
tk.Button(btn_frame, text="Detect Trash", width=15, command=detect_trash).grid(row=0, column=1)

tk.Button(btn_frame, text="Heatmap", width=15, command=generate_heatmap).grid(row=1, column=0)
tk.Button(btn_frame, text="Multi View", width=15, command=multi_view).grid(row=1, column=1)

tk.Button(btn_frame, text="Plan Path", width=15, command=plan_path).grid(row=2, column=0)
tk.Button(btn_frame, text="Start Robot", width=15, command=start_robot).grid(row=2, column=1)

tk.Button(btn_frame, text="Run Full System", width=32, command=run_all).grid(row=3, column=0, columnspan=2, pady=5)

# RIGHT SIDE DASHBOARD
dashboard = tk.Frame(main_frame, bg="#111827", width=400)
dashboard.pack(side="right", fill="both")

tk.Label(dashboard, text="AquaClean AI",
         fg="white", bg="#111827",
         font=("Arial", 20, "bold")).pack(pady=10)

tk.Label(dashboard, text="Autonomous Water Cleaning System",
         fg="lightgray", bg="#111827",
         font=("Arial", 10)).pack(pady=5)

tk.Label(dashboard, text="────────────────────────",
         fg="gray", bg="#111827").pack(pady=5)

tk.Label(dashboard, text="System Metrics",
         fg="white", bg="#111827",
         font=("Arial", 14, "bold")).pack(pady=10)

battery_label = tk.Label(dashboard, text="Battery: 100%",
                         fg="lime", bg="#111827", font=("Arial", 13))
battery_label.pack(pady=5)

trash_label = tk.Label(dashboard, text="Trash: 0",
                       fg="white", bg="#111827", font=("Arial", 13))
trash_label.pack(pady=5)

tk.Label(dashboard, text="Bin Fill",
         fg="white", bg="#111827").pack()

bin_bar = ttk.Progressbar(dashboard, length=250, maximum=100)
bin_bar.pack(pady=8)

status_label = tk.Label(dashboard, text="Status: Idle",
                        fg="cyan", bg="#111827", font=("Arial", 13))
status_label.pack(pady=10)

time_label = tk.Label(dashboard, text="Time: 0s",
                      fg="white", bg="#111827", font=("Arial", 12))
time_label.pack(pady=3)

eta_label = tk.Label(dashboard, text="ETA: 0s",
                     fg="white", bg="#111827", font=("Arial", 12))
eta_label.pack(pady=3)

tk.Label(dashboard, text="────────────────────────",
         fg="gray", bg="#111827").pack(pady=5)

tk.Label(dashboard, text="System Logs",
         fg="white", bg="#111827",
         font=("Arial", 13, "bold")).pack(pady=5)

log_box = tk.Text(dashboard, height=10, width=35,
                  bg="black", fg="lime")
log_box.pack(pady=5)

log_box.insert(tk.END, "System Ready...\n")

tk.Label(dashboard, text="────────────────────────",
         fg="gray", bg="#111827").pack(pady=5)

tk.Label(dashboard, text="Future Enhancements",
         fg="white", bg="#111827",
         font=("Arial", 13, "bold")).pack(pady=5)

future_label = tk.Label(
    dashboard,
    text="• Mobile App Integration\n"
         "• Predictive Cleaning\n"
         "• Waste Classification\n"
         "• Swarm Robots\n"
         "• Dynamic Replanning",
    fg="lightgray",
    bg="#111827",
    justify="left",
    font=("Arial", 11)
)
future_label.pack(pady=10)

tk.Label(dashboard, text=" ",
         bg="#111827").pack(expand=True)

root.mainloop()