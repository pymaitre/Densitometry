"""
Module for:
- reading and showing CT images;
- reading and showing the RTSTRUCT;
- identifing the requested ROI;
- recreating the ROI mask on the CT image;
- extracting HU values and their corresponding counts.
- performing image resampling
"""

import os
from pathlib import Path
from typing import Tuple
import numpy as np
import SimpleITK as sitk
import matplotlib.pyplot as plt
import resmip as rsm
import matplotlib

matplotlib.use("Agg")


def save_info_nifti(
    save_info_all: bool,
    directory_out: Path,
    CT: rsm.Image,
    rt: rsm.RTStructureSet,
    ROI_name: str,
    ID: str,
) -> None:
    """
    Save CT image and RT Structure Set in NIFTI format.

    :param save_info_all: save the input CT image and RT Structure Set.
    :type save_info_all: bool
    :param directory_out: path where to save the desired information.
    :type directory_out: Path
    :param CT: input CT image.
    :type CT: rsm.Image
    :param rt: input RT Structure Set.
    :type rt: rsm.RTStructureSet
    :param ROI_name: name of the ROI.
    :type ROI_name: str
    :param ID: patient ID.
    :type ID: str

    :return: None
    """

    if ROI_name in rt.keys():
        rt_save = rt[ROI_name]
    else:
        raise ValueError("Not valid ROI name")

    if save_info_all:
        dir_nifti = Path(directory_out) / "dataset" / "imagesTr"
        Path(dir_nifti).mkdir(parents=True, exist_ok=True)

        dir_RTst = Path(directory_out) / "dataset" / "labelsTr"
        Path(dir_RTst).mkdir(parents=True, exist_ok=True)

        CT_nifti_path = dir_nifti / f"test_{ID}_0000.nii.gz"
        RTst_nifti_path = dir_RTst / f"test_{ID}.nii.gz"

        try:
            sitk.WriteImage(CT, str(CT_nifti_path))
            print("CT_saved in:")
            print(CT_nifti_path)
            rt_save.write(RTst_nifti_path, write_metadata=False)

            print("RTst_saved in: ")
            print(RTst_nifti_path)
            print("")
        except Exception as e:
            print("problem: ", e)


def ROI_ok(
    ct_path: Path, rt_path: Path, ROI_founded: str, show_CT_ROI: bool, slice: int
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Define the ROI and extract the distribution of HU values within the ROI.

    :param ct_path: CT image path.
    :type ct_path: Path
    :param rt_path: RT Structure Set path.
    :type rt_path: Path
    :param ROI_founded: name of the ROI.
    :type ROI_founded: str
    :param show_CT_ROI: flag used to show CT slice and ROI.
    :type show_CT_ROI: bool
    :param slice: slice number to display.
    :type slice: int

    :return: array of HU values in the ROI and array of their corresponding counts.
    :rtype: Tuple[np.ndarray,np.ndarray]
    """

    # Read CT and CT_arr
    CT, CT_arr = read_and_show_ct(ct_path, show_CT_ROI, slice)

    # Get RT Structure Set
    rt = rsm.RTStructureSet.read(filename=rt_path, structure_names=ROI_founded, reference_image=CT)

    # Mask
    mask = read_and_show_RTst(rt, ROI_founded)

    # Get HU and counts for each ROI
    HU_ROI, counts_ROI = obtain_ROI(mask, CT_arr, show_CT_ROI, slice)

    return HU_ROI, counts_ROI


def ROI_res(
    ct_path: Path,
    rt_path: Path,
    new_sp: np.ndarray,
    ROI_founded: str,
    show_CT_ROI: bool,
    resampler,
    slice: int,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Define the ROI and extract the distribution of HU values within the ROI after resampling.

    :param ct_path: CT image path.
    :type ct_path: Path
    :param rt_path: RT Structure Set path.
    :type rt_path: Path
    :param new_sp: new voxel spacing.
    :type new_sp: np.ndarray
    :param ROI_founded: name of the ROI.
    :type ROI_founded: str
    :param show_CT_ROI: flag used to show CT slice and ROI.
    :type show_CT_ROI: bool
    :param slice: slice number to display.
    :type slice: int

    :return: arrays containing HU values and their corresponding counts of the resampled image.
    :rtype: Tuple[np.ndarray,np.ndarray]
    """

    # CT and CT_arr
    CT, CT_arr = read_and_show_ct(ct_path, show_CT_ROI, slice)

    # Resampling
    CT_res = resample(CT, new_sp[0], new_sp[1], new_sp[2], resampler)
    CT_res_arr = CT_res.numpy()

    # Get RTStructure Set
    rt_res = rsm.RTStructureSet.read(
        filename=rt_path, structure_names=ROI_founded, reference_image=CT_res
    )

    # Get the mask
    mask_res = read_and_show_RTst(rt_res, ROI_founded)

    # Get HU and counts for ROI
    HU_ROI_res, counts_ROI_res = obtain_ROI(mask_res, CT_res_arr, show_CT_ROI, slice)

    return HU_ROI_res, counts_ROI_res


def read_and_show_ct(ct_path: Path, show_CT_ROI: bool, slice: int) -> Tuple[rsm.Image, np.ndarray]:
    """
    Extract CT image from ct_path and optionally display the input slice.

    :param ct_path: path to the CT directory.
    :type ct_path: Path
    :param show_CT_ROI: flag used to show the CT slice.
    :type show_CT_ROI: bool
    :param slice: slice number to display.
    :type slice: int

    :return: CT image and CT array.
    :rtype: Tuple[rsm.Image,np.ndarray]
    """

    # Read image
    ct = rsm.Image.read(ct_path)

    # Get the CT array
    ct_arr = ct.numpy()
    print("The CT has a shape: ", ct_arr.shape)

    # Remove comments if you want to see the slice
    # if show_CT_ROI:
    #     plt.imshow(ct_arr[slice])
    #     plt.show()

    return ct, ct_arr


def read_and_show_RTst(rt_0: rsm.RTStructureSet, ROI_founded: str) -> np.ndarray:
    """
    Define the ROI mask found for the CT.
    Because the value 0 HU is significant in CT image, the binary mask of the ROI is
    converted to 1 and NaN.

    :param rt_0: input RT Structure Set.
    :type rt_0: rsm.RTStructureSet
    :param ROI_founded: name of the ROI.
    :type ROI_founded: str

    :return: mask associated with the ROI (1 and NaN instead of 1 and 0).
    :rtype: np.ndarray
    """
    # Check the different ROIs
    print(f"ROI: {rt_0.keys()}")

    roi_obj = None

    # Get the desired RTStructures
    for name_ROI in rt_0.keys():
        if ROI_founded == name_ROI:
            print("Consider the ROI: ", name_ROI, ", coinciding with: ", ROI_founded)
            roi_obj = rt_0[name_ROI]

            break
        else:
            print("I'm analyzing the ROI: ", name_ROI)

    rt = roi_obj

    # Convert in array
    rt_arr = rt.numpy()
    print(
        "The RTst has a shape: ",
        rt_arr.shape,
        " and contains: ",
        np.unique(rt_arr, return_counts=True)[1][1],
        " 1",
    )

    # Get the mask
    mask = rt_arr.astype(float)
    mask[mask == 0] = np.nan

    return mask


def obtain_ROI(
    mask: np.ndarray, ct_arr: np.ndarray, show_CT_ROI: bool, slice: int
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Extract the HU distribution for the ROI by multiplying the CT array and the ROI mask.
    Then NaN values are removed.

    :param mask: mask associated with the ROI (1 and NaN instead of 1 and 0).
    :type mask: np.ndarray
    :param ct_arr: CT image converted to an array.
    :type ct_arr: np.ndarray
    :param show_CT_ROI: flag used to show the CT slice and ROI.
    :type show_CT_ROI: bool
    :param slice: slice number to display.
    :type slice: int

    :return: arrays containing HU values and their corresponding counts within the ROI.
    :rtype: Tuple[np.ndarray,np.ndarray]
    """

    # Compute ct, HU, HU not NaN and counts not NaN for the desired ROI
    ct_ROI = mask * ct_arr
    HU_ROI, counts_ROI = np.unique(ct_ROI, return_counts=True)
    HU_ROI_no_nan = HU_ROI[np.where(~np.isnan(HU_ROI))[0]]
    counts_ROI_no_nan = counts_ROI[np.where(~np.isnan(HU_ROI))[0]]

    # Remove comments if you want the following prints
    # if show_CT_ROI:
    # print("The number of HU and counts in the ROI is: ", len(HU_ROI_no_nan), " and ", len(counts_ROI_no_nan))
    # print("starting CT in ROI has type: ", ct_ROI.shape)
    # print(HU_ROI_no_nan)
    # print(counts_ROI_no_nan)
    # plt.imshow(ct_ROI[slice])
    # plt.colorbar()
    # plt.show()

    return HU_ROI_no_nan, counts_ROI_no_nan


def resample(
    image: rsm.Image, new_x: float, new_y: float, new_z: float, resampler: int
) -> rsm.Image:
    """
    Resample the given image using the new voxel spacing and resampler.

    :param image: image to be resampled.
    :type image: rsm.Image
    :param new_x: new voxel spacing value for the x-axis.
    :type new_x: float
    :param new_y: new voxel spacing value for the y-axis.
    :type new_y: float
    :param new_z: new voxel spacing value for the z-axis.
    :type new_z: float
    :param resampler: resampling interpolation method.
    :type resampler: int


    :return: resampled image.
    :rtype: rsm.Image
    """

    # Fill new_spacing
    new_spacing = np.array([new_x, new_y, new_z])

    # Check if all the dimensions are greater than 0
    orig_size = image.size
    for s in orig_size:
        if s == 0:
            raise ValueError("The image has one dimension equal to zero")

    new_image = rsm.Image.resample(image, new_spacing, resampler, 0)

    return new_image
