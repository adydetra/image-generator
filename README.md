# Image Generator 🖼️

Simple PNG image generator written in pure Python with no external dependencies. Supports multiple visual patterns, configurable delays, and custom output folders.

![Static Badge](https://img.shields.io/badge/license-MIT-brightgreen?label=LICENSE)

---

## Requirements

- [Python 3.x](https://www.python.org/downloads/) installed and available on `PATH`.

After cloning or downloading the repository, open a terminal inside this project folder.

---

## Quick Start (Windows)

- **CLI menu**: run `run.bat`. Choose options 1–5 to trigger the available presets.
- **Desktop GUI**:
  - `launch_gui.bat` → direct shortcut.
  - or `python gui_launcher.py` → launch the GUI from a terminal.

The GUI lets you fill all parameters interactively (pattern, count, delay, dimensions, seed, output folder).

---

## Run the Python Script Directly

```bash
python gen_images.py [options]
```

### Key Options

| Option | Default | Description |
| ------ | ------- | ----------- |
| `--count`, `-n` | `1` | Number of images to generate. |
| `--pattern` | `random` | Pattern type. Choices: `random`, `noise`, `stripes`, `checker`, `circle`, `gradient`, `digits`. |
| `--delay` | `5` | Delay (seconds) between images. Use `0` for no delay. |
| `--width` | `1920` | Image width in pixels. |
| `--height` | `1080` | Image height in pixels. |
| `--seed` | random | RNG seed. Provide an integer to reproduce exact output. |
| `--output`, `-o` | `DEFAULT_OUTDIR` in `gen_images.py` | Output folder. Created automatically if it doesn't exist. |

### Examples

- 10 gradient images with 2-second delay:
  ```bash
  python gen_images.py --count 10 --pattern gradient --delay 2
  ```
- 100 digit images with fixed seed and custom folder:
  ```bash
  python gen_images.py --count 100 --pattern digits --seed 42 --output D:\OutputGambar
  ```

---

## Key Notes

- **Seed**: integer that fixes the random sequence. Provide one when you need reproducible results (documentation, testing). Leave empty to get unique images every run.
- **Output folder**: change it via `--output` or the "Folder output" field in the GUI. The default value lives in `DEFAULT_OUTDIR` inside `gen_images.py`.
- **Digits pattern**: generates numbered images (`001.png`, `002.png`, etc.), ideal for sequential frames.

---

## License

This project is licensed under the [MIT](LICENSE) license.
