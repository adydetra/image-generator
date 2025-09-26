# Image Generator 🎨

A simple Python script to generate random PNG images with various patterns without any external dependencies.

![Static Badge](https://img.shields.io/badge/license-MIT-brightgreen?label=LICENSE)

---

## Get Started

`Required` to install:

- [Python 3.x](https://www.python.org/downloads/)

Clone or download the repository.

---

## Commands

Generate 1 random image:

```bash
python gen_images.py
```

Generate 5 noise images:

```bash
python gen_images.py --count 5 --pattern noise
```

Generate 10 images with default pattern and 5 seconds delay:

```bash
python gen_images.py --count 10 --delay 5
```

Generate 10 gradient images with 2 seconds delay:

```bash
python gen_images.py --count 10 --pattern gradient --delay 2
```

---

## License

The code is licensed [MIT](LICENSE)
