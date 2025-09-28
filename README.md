

# FITS Image Processing Pipeline

This repository provides a Python pipeline for processing astronomical CCD images obtained from 1.3m Devasthal Fast Optical Telescope (DFOT) and 2m Himalayan Chandra Telescope (HCT).  
The script supports **bias correction**, **flat-field correction**, **reshaping**, and **cosmic ray removal** using [AstroScrappy](https://github.com/astropy/astroscrappy).

---

## Features
- Generate **master bias** from multiple bias frames.
- Create **normalized flats** for each filter.
- Apply **bias and flat corrections** to science images.
- Reshape FITS data arrays to 2D (e.g., `2048 x 2048`). The data from 1.3m DFOT & 2m HCT are often in the shape of (2048,2048,1) which is improper format for the input in Astroscrappy module
- Perform **cosmic ray correction** with AstroScrappy.

---

## Requirements

- Python 3.8+
- [Astropy](https://www.astropy.org/)
- [Numpy](https://numpy.org/)
- [natsort](https://pypi.org/project/natsort/)
- [AstroScrappy](https://github.com/astropy/astroscrappy) (for cosmic ray cleaning)

Install all dependencies via:

```bash
pip install astropy numpy natsort astroscrappy
