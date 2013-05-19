#### make_image_from_bin_renum.py
# Copyright (C) 2010 R. Cameron Craddock (cameron.craddock@gmail.com)
#
# This script is a part of the pyClusterROI python toolbox for the spatially
# constrained clustering of fMRI data. It converts a NPY file generated by
# binfile_parcellation.py, group_binfile_parcellation.py, or
# group_mean_binfile_parcellation.npy into a nifti file where each voxels
# intensity corresponds to the number of the cluster to which it belongs. The
# clusters are renumbered to be contiguous.
#
# For more information refer to:
#
# Craddock, R. C.; James, G. A.; Holtzheimer, P. E.; Hu, X. P. & Mayberg, H. S.
# A whole brain fMRI atlas generated via spatially constrained spectral
# clustering Human Brain Mapping, 2012, 33, 1914-1928 doi: 10.1002/hbm.21333.
#
# ARTICLE{Craddock2012,
#   author = {Craddock, R C and James, G A and Holtzheimer, P E and Hu, X P and
#   Mayberg, H S},
#   title = {{A whole brain fMRI atlas generated via spatially constrained
#   spectral clustering}},
#   journal = {Human Brain Mapping},
#   year = {2012},
#   volume = {33},
#   pages = {1914--1928},
#   number = {8},
#   address = {Department of Neuroscience, Baylor College of Medicine, Houston,
#       TX, United States},
#   pmid = {21769991},
# } 
#
# Documentation, updated source code and other information can be found at the
# NITRC web page: http://www.nitrc.org/projects/cluster_roi/ and on github at
# https://github.com/ccraddock/cluster_roi
#
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
####

# this scripts requires NumPy (numpy.scipy.org), and nibabel 
# (http://niftilib.sourceforge.net/pynifti/) to be installed in a directory that is
# accessible through PythonPath 
import nibabel as nb
from numpy import *

# make_image_from_bin_renum( image, binfile, mask ):
# 
# Converts a NPY file generated by binfile_parcellation.py,
# group_binfile_parcellation.py, or group_mean_binfile_parcellation.npy into a
# nifti file where each voxels intensity corresponds to the number of the
# cluster to which it belongs. Clusters are renumberd to be contiguous.
#     image:   The name of the nifti file to be written.
#     binfile: The binfile to be converted. The file contains a n_voxel x 1
#              vector that is converted to a nifti file.
#     mask:    Mask describing the space of the nifti file. This should
#              correspond to the mask originally used to create the
#              connectivity matrices used for parcellation.
#
def make_image_from_bin_renum( image, binfile, mask ):

    # read in the mask
    nim=nb.load(mask)

    # read in the binary data    
    if( binfile.endswith(".npy") ):
        print "Reading",binfile,"as a npy filetype"
        a=load(binfile)
    else:
        print "Reading",binfile,"as a binary file of doubles"
        a=fromfile(binfile)

    unique_a=list(set(a.flatten()))
    unique_a.sort()

    # renumber clusters to make the contiguous
    b=zeros((len(a),1))
    for i in range(0,len(unique_a)):
        b[a==unique_a[i]]=i+1

    imdat=nim.get_data()

    # map the binary data to mask
    imdat[imdat>0]=1
    imdat[imdat>0]=short(b[0:sum(imdat)].flatten())

    # write out the image as nifti
    nim_out = nb.Nifti1Image(imdat, nim.get_affine())
    nim_out.set_data_dtype('int16')
    nim_out.to_filename(image)
