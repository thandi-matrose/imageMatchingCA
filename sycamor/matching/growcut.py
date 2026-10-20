from skimage.registration import phase_cross_correlation

# Assume `reference_image` and `moving_image` are 2D NumPy arrays
# (e.g., a SAR feature band and its corresponding optical band)
shift, error, diffphase = phase_cross_correlation(
    reference_image, 
    moving_image, 
    upsample_factor=100  # for subpixel accuracy
)
# `shift` is a tuple: (row_shift, col_shift)
# You can apply it using scipy.ndimage.fourier_shift