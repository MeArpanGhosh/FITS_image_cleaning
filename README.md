

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


Usage

Run the script directly:
python fits_processing.py

You will be prompted to:

Enter the path to your data directory.

Provide the object name (used for science images).

Expected file naming conventions:

Bias frames: bias_001.fits, bias_002.fits, ...

Flat frames: flat_v_2s_001.fits (lowercase filter name)

Science frames: m31_v_10s_001.fits

Processed files will be saved in a processed/ directory.


Citation

If you use this code in a scientific publication, please cite AstroScrappy, which provides the cosmic ray rejection algorithm:

M. T. Craig, A. M. Crawford, A. W. Mann, K. M. Pichon, J. M. Sick, and J. J. van Santen (2023). astroscrappy: Speedy Cosmic Ray Cleaning. Astrophysics Source Code Library, record ascl:1602.008.
DOI: 10.5281/zenodo.1482019


License

This project is released under the MIT License.
See LICENSE
