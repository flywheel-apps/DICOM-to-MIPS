#!/usr/bin/env python

import os
import json
import nibabel as nib
import numpy as np
import PIL
from PIL import ImageOps


def process_mips(image_data, threshold_percentile):
    '''
    This function processes MIPs 2D numpy arrays
    It first calculates the value at the threshold_percentile for the array
    and sets any values above this value to this value
    :param image_data: a 2D numpy array representation of an image
    :param threshold_percentile: the percentile cutoff for maximum values
    :return: a PIL object that can be saved as an image file
    '''
    # determine value at threshold_percentile
    threshold_value = np.percentile(image_data, threshold_percentile)
    # replace values greater than threshold_value with threshold_value
    image_data[image_data > threshold_value] = threshold_value
    # scale to 255 for PIL import
    image_data *= (255.0/image_data.max())
    # convert to PIL object for image operations
    img = PIL.Image.fromarray(np.uint8(image_data))
    # invert image (black to white)
    img = ImageOps.invert(img)
    # resize image and rotate 90 degrees counter-clockwise
    img = img.resize((400,400)).rotate(90)
    return img


def create_mips_file_name(filename,string):
    output_string = filename.split(".nii.gz")[0]
    output_string = output_string + '_' + string
    return output_string


# Gear basics
input_folder = '/flywheel/v0/input/file/'
output_folder = '/flywheel/v0/output/'

# Declare the output path
output_filepath = os.path.join(output_folder, '.metadata.json')

# declare config file path
config_file_path = '/flywheel/v0/config.json'

# read in config
with open(config_file_path) as config_data:
    config = json.load(config_data)

# set values from config
# filepath = config['inputs']['nifti']['location']['path']
# filename = config['inputs']['nifti']['location']['name']
threshold_percentile = config['config']['threshold_percentile']
generate_nifti = config['config']['generate_nifti']

# find a nifti file in the output filepath
for file in os.listdir(output_folder):
    if file.endswith(".nii.gz"):
        filepath = os.path.join(output_folder, file)
        filename = file
        break

# import nifti with nibabel
nifti_file = nib.load(filepath)
# get np 3D np array from nifti_file
image_data = nifti_file.get_fdata()

# compute MIPS for each cardinal direction
sagittal = np.amax(image_data, 0)
coronal = np.amax(image_data, 1)
axial = np.amax(image_data, 2)

# threshold MIPS
sagittal = process_mips(sagittal, threshold_percentile)
coronal = process_mips(coronal, threshold_percentile)
axial = process_mips(axial, threshold_percentile)

# save images
sagittal.save(os.path.join(output_folder, create_mips_file_name(filename, 'mips_sag.png')), "PNG")
coronal.save(os.path.join(output_folder, create_mips_file_name(filename, 'mips_cor.png')), "PNG")
axial.save(os.path.join(output_folder, create_mips_file_name(filename, 'mips_ax.png')), "PNG")

# delete NIfTI if specified
if str(generate_nifti) == 'n':
    print('Deleting NIfTI file...')
    os.remove(filepath)

