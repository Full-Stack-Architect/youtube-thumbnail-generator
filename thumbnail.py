import os
import threading
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageFilter

SUPPORTED = (".jpg", ".jpeg", ".png", ".webp")

files = []

# ---------------- IMAGE PROCESS ---------------- #

def create_thumbnail(path, size, suffix, progress):
    try:
        img = Image.open(path)
        img.verify()

        img = Image.open(path).convert("RGB")

        bg = img.copy()
        bg.thumbnail(size)
        bg = bg.resize(size)
        bg = bg.filter(ImageFilter.GaussianBlur(25))

        fg = img.copy()
        fg.thumbnail(size)

        bg.paste(
            fg,
            ((size[0] - fg.width) // 2, (size[1] - fg.height) // 2)
        )

        new_path = os.path.splitext(path)[0] + suffix + ".jpg"

        counter = 1
        while os.path.exists(new_path):
            new_path = os.path.splitext(path)[0] + f"{suffix}_{counter}.jpg"
            counter += 1

        bg.save(new_path, "JPEG", quality=95, subsampling=0)

        progress()

    except Exception as e:
        log_message(f"Skipped: {os.path.basename(path)}")


# ---------------- CORE PROCESS ---------------- #

def start_generate():
    if not files:
        messagebox.showwarning("Warning", "Select images or folder first")
        return

    generate_btn.config(state=DISABLED)
    progress_bar["value"] = 0
    progress_bar["maximum"] = len(files)

    mode = mode_var.get()
    size = (1280, 720) if mode == "yt" else (1080, 1920)
    suffix = "_yt" if mode == "yt" else "_shorts"

    def update_progress():
        progress_bar["value"] += 1

    def task():
        for path in files:
            create_thumbnail(path, size, suffix, update_progress)

        generate_btn.config(state=NORMAL)
        messagebox.showinfo("Done", "Thumbnails generated successfully!")

    threading.Thread(target=task, daemon=True).start()


# ---------------- FILE SELECT ---------------- #

def select_images():
    global files
    files = filedialog.askopenfilenames(
        filetypes=[("Images", "*.jpg *.jpeg *.png *.webp")]
    )
    update_info()


def select_folder():
    global files
    folder = filedialog.askdirectory()
    if not folder:
        return

    files = [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.lower().endswith(SUPPORTED)
    ]

    update_info()


def update_info():
    info_label.config(text=f"Images Found: {len(files)}")


# ---------------- LOG ---------------- #

def log_message(msg):
    log_box.insert(END, msg + "\n")
    log_box.see(END)


# ---------------- UI ---------------- #

root = Tk()
root.title("Thumbnail Generator — YT + Shorts")
root.geometry("600x520")
root.resizable(False, False)

title = ttk.Label(root, text="Thumbnail Generator", font=("Segoe UI", 18, "bold"))
title.pack(pady=10)

btn_frame = Frame(root)
btn_frame.pack()

ttk.Button(btn_frame, text="Select Images", command=select_images).grid(row=0, column=0, padx=5)
ttk.Button(btn_frame, text="Select Folder", command=select_folder).grid(row=0, column=1, padx=5)

info_label = ttk.Label(root, text="Images Found: 0")
info_label.pack(pady=5)

mode_var = StringVar(value="yt")

mode_frame = Frame(root)
mode_frame.pack()

ttk.Radiobutton(mode_frame, text="YouTube 1280×720", variable=mode_var, value="yt").grid(row=0, column=0, padx=10)
ttk.Radiobutton(mode_frame, text="Shorts 1080×1920", variable=mode_var, value="shorts").grid(row=0, column=1, padx=10)

generate_btn = ttk.Button(root, text="Generate Thumbnails", command=start_generate)
generate_btn.pack(pady=15)

progress_bar = ttk.Progressbar(root, length=400, mode="determinate")
progress_bar.pack(pady=10)

log_box = Text(root, height=10, width=70)
log_box.pack(pady=10)

ttk.Label(root, text="Batch mode supported • Secure processing").pack()

root.mainloop()

