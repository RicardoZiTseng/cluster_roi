#### group_binfile_parcellation.py
# Copyright (C) 2010 R. Cameron Craddock (cameron.craddock@gmail.com)
#
# This script is a part of the pyClusterROI python toolbox for the spatially
# constrained clustering of fMRI data. It performs group level normalized
# clustering of connectivity matrices. This is one of two methods proposed in
# Craddock (2011) for group level clustering. Results of subject level
# clusterings are combined and then clustered. This is referred to as 2-level
# clustering in the paper. 
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

# this scripts requires NumPy (numpy.scipy.org), SciPy (www.scipy.org), and
# python_ncut_lib distributed with this script to be installed in a directory
# that is accessible through PythonPath (the current directory will do for
# python_ncut_lib.py).
from numpy import array
from scipy import *
from scipy.sparse import *
from python_ncut_lib import *

# group_img=group_binfile_parcellate( infiles, outfile, K,n_voxels ):
#
# This function performs group level clustering of individual level clustering
# results. Each single subject clustering is converted into a coincidence matrix
# W, where w_ij = 1 if voxels i and j are in the same cluster, and zero
# otherwise. Coincidence matrices are averaged across subjects and then
# submitted to normalized cut clustering to obtain K clusters.
#    infiles:   list of .NPY or .bin file containing single subject clustering
#               results. Each of these files is a 1D vector where the ith value
#               corresponds to the cluster assignment of voxel i. This assumes
#               that the vectors are in the same order. These files are
#               generated by binfile_parcellation.py
#    outfile:   the name of the output file, a n_voxels x 1 vector is written to
#               this file, where the ith value corresponds to the cluster to
#               which voxel i is assigned 
#    K:         The number of clusters that will be generated. This is a single
#               number. This assumes that each of the input files were clustered
#               to K
#    n_voxels:  Number of voxels in the _mask_ used to generate the subject
#               specific connectivity matrices
#    group_img: (output) n_voxels x 1 vector indicating cluster assignments 
def group_binfile_parcellate( infiles, outfile, K, n_voxels ):

    # read in all of the files, construct coincidence matrices, and average
    # them 
    for i in range(0,len(infiles)):

        # read in the files
        if infiles[i].endswith(".npy"):
            print "Reading",infiles[i],"as a npy filetype"
            imdat=load(infiles[i])
        else:
            print "Reading %s as a binary file of doubles"%(\
                infiles[i])
            fid=open(infiles[i], 'rb')
            imdat=fromfile(fid)
            fid.close()

        # construct the coincidences between the voxels    
        sparse_i=[]
        sparse_j=[]
        for j in range(1,K+1):
            grp_ndx=nonzero(imdat==j)[0]
            ff=tile(grp_ndx,(len(grp_ndx),1))
            sparse_i=append(sparse_i,reshape(ff,prod(shape(ff))))
            sparse_j=append(sparse_j,reshape(ff.transpose(),prod(shape(ff))))

        # sum the coincidence matrices across input files    
        if i==0:
            W=csc_matrix((ones(len(sparse_i)),(sparse_i,sparse_j)),\
               (n_voxels,n_voxels),dtype=double)
        else:
            print 'adding ',i
            W=W+csc_matrix((ones(len(sparse_i)),(sparse_i,sparse_j)),\
                (n_voxels,n_voxels),dtype=double)

    # set the diagonal to zeros as is customary with affinity matrices
    W=W-spdiags(W.diagonal(),[0],n_voxels,n_voxels,"csc")
    print "diag is ",sum(W.diagonal()),"\n"

    # divide by the number of input files, to calculate the average     
    W=W/len(infiles)
    print "finished reading in data and calculating connectivity\n"

    # perform clustering
    eigenval,eigenvec = ncut(W,K)
    eigenvec_discrete = discretisation(eigenvec)

    ## write out the results
    group_img=eigenvec_discrete[:,0]

    for i in range(1,K):
        group_img=group_img+(i+1)*eigenvec_discrete[:,i]

    save(outfile,group_img.todense())
    print "finished group parcellation\n"

    return array(group_img.todense())
