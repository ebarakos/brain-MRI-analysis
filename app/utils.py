import shutil
import tarfile
from cStringIO import StringIO
import os
from django.conf import settings
import nibabel as nib
import numpy as np
import scipy
import dipy.reconst.dti as dti
from dipy.core.gradients import gradient_table
from dipy.segment.mask import median_otsu


class Paths(object):
    def __init__(self, nii, bvecs, bvals):
        self.nii = nii
        self.bvecs = bvecs
        self.bvals = bvals


def untar(response):
    try:
        tar = tarfile.open(fileobj=StringIO(response.content))
    except:
        raise RuntimeError('Error on opening tar file')
    extractionFolder = 'tarFiles'
    for tarinfo in tar:
        if tarinfo.isfile():
            filename, file_extension = os.path.splitext(tarinfo.name)
            if file_extension == '.nii':
                niiPath = extractionFolder + '/' + tarinfo.name
            elif file_extension == '.bvec':
                bvecsPath = extractionFolder + '/' + tarinfo.name
            elif file_extension == '.bval':
                bvalsPath = extractionFolder + '/' + tarinfo.name
            else:
                raise RuntimeError('Non-compatible tar file content')
    try:
        niiPath, bvecsPath, bvalsPath
    except NameError:
        raise RuntimeError('Non-compatible tar file content')
    clearFolder(extractionFolder)
    tar.extractall(path=extractionFolder)
    tar.close()
    return Paths(niiPath, bvecsPath, bvalsPath)


def analyze(Paths):
    data = nib.load(Paths.nii).get_data()
    bvals, bvecs = loadBvalsBvecs(Paths.bvals, Paths.bvecs)

    # clear old images so we do not present them by mistake
    clearFolder('images')

    # get the first zero element's index
    b0Index = np.where(bvals == 0)[0][0]
    # b0 map calculation
    b0map = data[:, :, :, b0Index]
    createSliceViews(b0map, '-b0')

    # get the list of all non-zero element's indices
    dwiIndices = np.where(bvals != 0)[0].tolist()
    # dwi map calculation. get the mean value of the 4th axis
    DWImap = data[:, :, :, dwiIndices].mean(axis=3)
    createSliceViews(DWImap, '-dwi')

    # FA map calculation.heavy computation,needs caching and/or optimization.
    # maskdata used according to dipy examples.
    # also problems occured for zero-filled, one-dimensional bvecs
    if len(bvecs.shape) != 1:
        gtab = gradient_table(bvals, bvecs)
        maskdata, mask = median_otsu(data)
        tenmodel = dti.TensorModel(gtab)
        tenfit = tenmodel.fit(maskdata)
        FAmap = dti.fractional_anisotropy(tenfit.evals)
        createSliceViews(FAmap, '-fa')


def createSliceViews(inputMap, suffix):
    indexes = np.shape(inputMap)
    sagittal = inputMap[indexes[0]/2, :, :]
    coronal = inputMap[:, indexes[1]/2, :]
    axial = inputMap[:, :, indexes[2]/2]
    scipy.misc.imsave('images/axial' + suffix + '.jpg', axial)
    scipy.misc.imsave('images/coronal' + suffix + '.jpg', coronal)
    scipy.misc.imsave('images/sagittal' + suffix + '.jpg', sagittal)


def clearFolder(name):
    imagesPath = os.path.join(settings.BASE_DIR, name)
    shutil.rmtree(imagesPath)
    if not os.path.exists(imagesPath):
        os.makedirs(imagesPath)


def loadBvalsBvecs(bvalsPath, bvecsPath):
    bvecs = np.loadtxt(bvecsPath)
    bvals = np.loadtxt(bvalsPath)
    return bvals, bvecs
