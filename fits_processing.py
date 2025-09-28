import os
import numpy as np
from astropy.io import fits
import glob
from natsort import natsorted

#Trying to  import astroscrappy for cosmic ray removal

try:
    import astroscrappy
    HAS_ASTROSCRAPPY = True
except ImportError:
    HAS_ASTROSCRAPPY = False


def median_combine(file_list, scale_mode=False):
    """Median combine a list of FITS files. Optionally scale by mode."""
    data_stack = []
    for filename in file_list:
        data = fits.getdata(filename).astype(np.float64)
        if scale_mode:
            # Scale by mode using (3*median - 2*mean)
            mean = np.mean(data)
            median = np.median(data)
            mode = 3 * median - 2 * mean
            if mode != 0:
                data = data / mode
        data_stack.append(data)
    return np.median(np.array(data_stack), axis=0)

def fits_stats(data):
    """Compute statistics on a FITS image array."""
    mean = np.mean(data)
    median = np.median(data)
    mode = 3*median - 2*mean
    minvalue = np.min(data)
    maxvalue = np.max(data)
    npix = data.size
    return {
        'mean': mean,
        'median': median,
        'mode': mode,
        'min': minvalue,
        'max': maxvalue,
        'npix': npix
    }

def save_fits(data, outname, header=None):
    """Save a numpy array to a FITS file."""
    hdu = fits.PrimaryHDU(data, header=header)
    hdu.writeto(outname, overwrite=True)

def generate_master_bias(bias_pattern, outname='master_bias.fits'):
    bias_files = glob.glob(bias_pattern)
    master_bias = median_combine(bias_files)
    save_fits(master_bias, outname)
    print(f"Master bias saved as {outname}")
    return master_bias

def generate_normalised_flats(flat_pattern, filters, outdir='.'):
    norm_flats = {}
    for filt in filters:
        flat_files = glob.glob(flat_pattern.format(f=filt))
        if not flat_files:
            print(f"No flat files found for filter {filt}")
            continue
        master_flat = median_combine(flat_files, scale_mode=True)
        stats = fits_stats(master_flat)
        normalised_flat = master_flat / stats['median']
        outname = os.path.join(outdir, f"normalised_flat_{filt}.fits")
        save_fits(normalised_flat, outname)
        print(f"Normalised flat for filter {filt} saved as {outname}")
        print(f"Stats for {filt}: {stats}")
        norm_flats[filt] = normalised_flat
    return norm_flats

def bias_correct_images(raw_pattern, master_bias, outdir='.'):
    raw_files = glob.glob(raw_pattern)
    bias_corrected_files = []
    for fname in raw_files:
        data, header = fits.getdata(fname, header=True)
        bias_corr = data - master_bias
        outname = os.path.join(outdir, f"biascorr_{os.path.basename(fname)}")
        save_fits(bias_corr, outname, header=header)
        bias_corrected_files.append(outname)
    return bias_corrected_files

def flat_correct_images(bias_corrected_pattern, filter_name, norm_flat, outdir='.'):
    files = glob.glob(bias_corrected_pattern.format(f=filter_name))
    for fname in files:
        data, header = fits.getdata(fname, header=True)
        flat_corr = data / norm_flat
        outname = os.path.join(outdir, f"flatcorr_{os.path.basename(fname)}")
        save_fits(flat_corr, outname, header=header)
        print(f"Flat and bias corrected image saved as {outname}")


def cosmic_ray_correct_image(image_path, outdir='.', suffix='crcorr'):
    if not HAS_ASTROSCRAPPY:
        print("astroscrappy not installed; skipping cosmic ray correction.")
        return image_path
    data, header = fits.getdata(image_path, header=True)
    #You have to adjust the gain and readnoise parameters according to telescope CCD you are using
    crmask, clean_data = astroscrappy.detect_cosmics(data, gain=1.0, readnoise=5.0, sigclip=4.5, sigfrac=0.3)  
    outname = os.path.join(outdir, f"{suffix}_{os.path.basename(image_path)}")
    save_fits(clean_data, outname, header=header)
    print(f"Cosmic ray corrected image saved as {outname}")
    return outname

def cosmic_ray_correct_images(cosmic_corrected_pattern, outdir='.'):
    corr_files = []
    for fname in cosmic_corrected_pattern:
        corr_file = cosmic_ray_correct_image(fname, outdir=outdir)
        corr_files.append(corr_file)
    return corr_files



if __name__ == "__main__":
    # User must set these patterns to match their directory/file structure

    print('#' * 135)
    print('This image processing code will execute succesfully only if the input files are named using the following convention : ')    
    print('1. All the filenames should be in lower case.') 
    print('2. raw object files should be named as "objname_filtername_exptime_framenumber.fits" . For e.g., m31_v_10s_001.fits') 
    print('3. flat files should be named as "flat_filtername_exptime_framenumber.fits" . For e.g., flat_v_2s_001.fits') 
    print('4. bias files should be named as "bias_framenumber.fits" . For e.g., bias_001.fits ' )
    print('#' * 135)
    
    counter = input('\n\n\n Press p to proceed further:\t')

    if (counter == 'p'):       
        
        #data_path = "/home/arpan/knowledge/ccd_image_reduction_data/20171210/"  # Enter the path to data 
        data_path = input('\nEnter the path to data:\t')
        if os.path.exists(data_path):
            
           os.chdir(data_path)
           filters = ['v', 'r', 'i']  # List your filters here. Please list the filter names in lowercase
          
           outdir = "processed"
          
           os.makedirs(outdir, exist_ok=True)
         
           # 1. Master Bias
           bias_pattern = os.path.join(data_path, 'bias*.fits')  # Selecting the bias frames
           master_bias = generate_master_bias(bias_pattern, outname=os.path.join(outdir, 'master_bias.fits'))
           
           # 2. Normalised Flats
           for filt in filters :
               flat_objname = 'flat*'+filt+'*'
               flat_pattern = os.path.join(data_path,flat_objname)  # Selecting the flats by filter (e.g., ../flat*{filt}*.fits)
          
               norm_flats = generate_normalised_flats(flat_pattern, filters, outdir=outdir)
            
           # 3. Bias Correction
           
           objname = input('\nEnter the name of your source:\t')
           objname_pattern = objname+'*.fits'
           raw_pattern = os.path.join(data_path,objname_pattern)  # Path to raw science images
           bias_corrected_files = bias_correct_images(raw_pattern, master_bias, outdir=outdir)
         
           # 4. Flat Correction (grouped by filter)
           for filt in filters:
               flat_corr_objname = 'biascorr*'+objname+'*'+filt+'*.fits'
               flat_pattern = os.path.join(outdir, flat_corr_objname)#"biascorr*{filt}*.fits")
               
               if filt in norm_flats:
                   flat_correct_images(flat_pattern, filt, norm_flats[filt], outdir=outdir)
           # 5. Reshaping the FITS images
           cosmic_corr_objname = 'flatcorr_biascorr*' + objname + '*.fits'
           cosmic_pattern = natsorted(glob.glob("processed/" + cosmic_corr_objname))
 
           reshaped_files = []
 
           for i in range(len(cosmic_pattern)):
               print(cosmic_pattern[i])
               with fits.open(cosmic_pattern[i]) as hdul:
                   flatcorr_biascorr_image_data = hdul[0].data
                   data_reshaped = flatcorr_biascorr_image_data.reshape(2048, 2048) #Reshaping the data
 
                   hdul[0].data = data_reshaped  
           
                   # Write reshaped file into processed directory
                   reshaped_name = cosmic_pattern[i].replace("processed/", "processed/reshaped_")
                   hdul.writeto(reshaped_name, overwrite=True)
                   reshaped_files.append(reshaped_name)
 
           # 6. Cosmic ray correction
           cosmic_ray_correct_images(reshaped_files, outdir=outdir)
  
 
           print("Processing complete.")
          
        else: 
           print(f"The directory '{data_path}' does not exist.")
          
