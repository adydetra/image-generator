import os
import sys
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

try:
    from gen_images import DEFAULT_OUTDIR, PATTERNS
except Exception as exc:  # pragma: no cover
    raise RuntimeError("Gagal mengimpor gen_images. Pastikan file berada di direktori yang sama.") from exc

PATTERN_CHOICES = ["random"] + sorted(PATTERNS.keys()) + ["digits"]


def run_generation(params, log_callback, done_callback):
    args = [
        sys.executable,
        os.path.join(os.path.dirname(__file__), "gen_images.py"),
        "--count",
        str(params["count"]),
        "--delay",
        str(params["delay"]),
        "--pattern",
        params["pattern"],
        "--output",
        params["output"],
    ]

    if params["width"]:
        args.extend(["--width", str(params["width"])])
    if params["height"]:
        args.extend(["--height", str(params["height"])])
    if params["seed"]:
        args.extend(["--seed", str(params["seed"])])

    log_callback(f"Menjalankan: {' '.join(args)}\n")

    try:
        process = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
    except FileNotFoundError:
        log_callback("Python tidak ditemukan. Pastikan Python ter-install dan tersedia di PATH.\n")
        done_callback(False)
        return

    with process.stdout:
        for line in process.stdout:
            log_callback(line)
    returncode = process.wait()
    if returncode == 0:
        log_callback("\nSelesai tanpa error.\n")
        done_callback(True)
    else:
        log_callback(f"\nProses berakhir dengan kode {returncode}.\n")
        done_callback(False)


def main():
    root = tk.Tk()
    root.title("Image Generator GUI")
    root.geometry("1280x720")

    input_frame = ttk.Frame(root, padding=16)
    input_frame.pack(fill=tk.X)

    # Pattern selection
    ttk.Label(input_frame, text="Pola gambar (pattern)").grid(row=0, column=0, sticky=tk.W)
    pattern_var = tk.StringVar(value=PATTERN_CHOICES[0])
    pattern_combo = ttk.Combobox(input_frame, textvariable=pattern_var, values=PATTERN_CHOICES, state="readonly")
    pattern_combo.grid(row=0, column=1, sticky=tk.EW, padx=(8, 0))

    # Count
    ttk.Label(input_frame, text="Jumlah gambar").grid(row=1, column=0, sticky=tk.W, pady=(8, 0))
    count_var = tk.StringVar(value="10")
    count_entry = ttk.Entry(input_frame, textvariable=count_var)
    count_entry.grid(row=1, column=1, sticky=tk.EW, padx=(8, 0), pady=(8, 0))

    # Delay
    ttk.Label(input_frame, text="Delay antar gambar (detik)").grid(row=2, column=0, sticky=tk.W, pady=(8, 0))
    delay_var = tk.StringVar(value="5")
    delay_entry = ttk.Entry(input_frame, textvariable=delay_var)
    delay_entry.grid(row=2, column=1, sticky=tk.EW, padx=(8, 0), pady=(8, 0))

    # Width & Height
    ttk.Label(input_frame, text="Lebar (px)").grid(row=3, column=0, sticky=tk.W, pady=(8, 0))
    width_var = tk.StringVar(value="1920")
    width_entry = ttk.Entry(input_frame, textvariable=width_var)
    width_entry.grid(row=3, column=1, sticky=tk.EW, padx=(8, 0), pady=(8, 0))

    ttk.Label(input_frame, text="Tinggi (px)").grid(row=4, column=0, sticky=tk.W, pady=(8, 0))
    height_var = tk.StringVar(value="1080")
    height_entry = ttk.Entry(input_frame, textvariable=height_var)
    height_entry.grid(row=4, column=1, sticky=tk.EW, padx=(8, 0), pady=(8, 0))

    # Seed (optional)
    ttk.Label(input_frame, text="Seed (opsional)").grid(row=5, column=0, sticky=tk.W, pady=(8, 0))
    seed_var = tk.StringVar()
    seed_entry = ttk.Entry(input_frame, textvariable=seed_var)
    seed_entry.grid(row=5, column=1, sticky=tk.EW, padx=(8, 0), pady=(8, 0))

    # Output directory
    ttk.Label(input_frame, text="Folder output").grid(row=6, column=0, sticky=tk.W, pady=(8, 0))
    output_var = tk.StringVar(value=DEFAULT_OUTDIR)
    output_entry = ttk.Entry(input_frame, textvariable=output_var)
    output_entry.grid(row=6, column=1, sticky=tk.EW, padx=(8, 0), pady=(8, 0))

    def browse_output():
        directory = filedialog.askdirectory(initialdir=output_var.get() or os.getcwd())
        if directory:
            output_var.set(directory)

    browse_btn = ttk.Button(input_frame, text="Browse...", command=browse_output)
    browse_btn.grid(row=6, column=2, padx=(8, 0), pady=(8, 0))

    input_frame.columnconfigure(1, weight=1)

    # Log area
    log_frame = ttk.LabelFrame(root, text="Log", padding=8)
    log_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 16))
    log_text = tk.Text(log_frame, height=12, wrap=tk.NONE, state=tk.DISABLED)
    log_text.pack(fill=tk.BOTH, expand=True)

    log_scroll_y = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=log_text.yview)
    log_text.configure(yscrollcommand=log_scroll_y.set)
    log_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

    status_var = tk.StringVar(value="Ready")
    status_label = ttk.Label(root, textvariable=status_var, relief=tk.SUNKEN, anchor=tk.W, padding=(12, 4))
    status_label.pack(fill=tk.X, side=tk.BOTTOM)

    running = {"thread": None}

    def append_log(message: str):
        log_text.configure(state=tk.NORMAL)
        log_text.insert(tk.END, message)
        log_text.see(tk.END)
        log_text.configure(state=tk.DISABLED)

    def on_done(success: bool):
        run_button.config(state=tk.NORMAL)
        status_var.set("Selesai" if success else "Gagal / selesai dengan error")

    def start_run():
        if running["thread"] and running["thread"].is_alive():
            messagebox.showinfo("Sedang berjalan", "Proses sedang berjalan. Tunggu hingga selesai.")
            return

        try:
            count = int(count_var.get())
            if count <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input tidak valid", "Jumlah harus berupa bilangan bulat positif.")
            return

        try:
            delay = float(delay_var.get())
            if delay < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input tidak valid", "Delay harus berupa angka >= 0.")
            return

        width = width_var.get().strip()
        height = height_var.get().strip()
        seed = seed_var.get().strip()

        try:
            width_val = int(width) if width else None
            if width_val is not None and width_val <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input tidak valid", "Lebar harus berupa bilangan bulat positif atau kosong.")
            return

        try:
            height_val = int(height) if height else None
            if height_val is not None and height_val <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input tidak valid", "Tinggi harus berupa bilangan bulat positif atau kosong.")
            return

        try:
            seed_val = int(seed) if seed else None
        except ValueError:
            messagebox.showerror("Input tidak valid", "Seed harus berupa bilangan bulat atau kosong.")
            return

        output_dir = output_var.get().strip()
        if not output_dir:
            messagebox.showerror("Input tidak valid", "Folder output wajib diisi.")
            return

        params = {
            "pattern": pattern_var.get(),
            "count": count,
            "delay": delay,
            "width": width_val,
            "height": height_val,
            "seed": seed_val,
            "output": output_dir,
        }

        run_button.config(state=tk.DISABLED)
        status_var.set("Sedang menghasilkan gambar...")
        append_log("============================\n")
        append_log("Memulai proses generate...\n")

        thread = threading.Thread(
            target=run_generation,
            args=(params, append_log, on_done),
            daemon=True,
        )
        running["thread"] = thread
        thread.start()

    run_button = ttk.Button(root, text="Generate", command=start_run)
    run_button.pack(pady=(0, 12))

    root.mainloop()


if __name__ == "__main__":
    main()
