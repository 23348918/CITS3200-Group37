from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import cv2

def darkness_filter(image: Image.Image, strength: float) -> Image.Image:
    """
    @brief Applies a darkness filter to the image.
    @params image (Image.Image): The image to be processed.
    @params strength (float): Strength of the darkness effect, between 0.0 and 1.0.
    @return Image.Image: The processed image with the darkness filter applied.
    """
    enhancer: ImageEnhance.Brightness = ImageEnhance.Brightness(image)
    return enhancer.enhance(1.0 - strength)

def brightness_filter(image: Image.Image, strength: float) -> Image.Image:
    """
    @brief Applies a brightness filter to the image.
    @params image (Image.Image): The image to be processed.
    @params strength (float): Strength of the brightness effect, between 0.0 and 1.0.
    @return Image.Image: The processed image with the brightness filter applied.
    """
    enhancer: ImageEnhance.Brightness = ImageEnhance.Brightness(image)
    return enhancer.enhance(strength * 2 + 1.0)

def gaussian_blur_filter(image: Image.Image, strength: float) -> Image.Image:
    """
    @brief Applies a Gaussian blur filter to the image.
    @params image (Image.Image): The image to be processed.
    @params strength (float): Strength of the blur effect, affects the radius of the blur.
    @return Image.Image: The processed image with the Gaussian blur filter applied.
    """
    return image.filter(ImageFilter.GaussianBlur(radius=strength * 5))

def intensity_filter(image: Image.Image, strength: float) -> Image.Image:
    """
    @brief Applies an intensity (contrast) filter to the image.
    @params image (Image.Image): The image to be processed.
    @params strength (float): Strength of the contrast effect, between 0.0 and 1.0.
    @return Image.Image: The processed image with the contrast filter applied.
    """
    enhancer: ImageEnhance.Contrast = ImageEnhance.Contrast(image)
    return enhancer.enhance(strength * 2 + 1)

def motion_blur_filter(image: Image.Image, strength: float) -> Image.Image:
    """
    @brief Applies a motion blur filter to the image.
    @params image (Image.Image): The image to be processed.
    @params strength (float): Strength of the motion blur effect, affects the kernel size.
    @return Image.Image: The processed image with the motion blur filter applied.
    """
    kernel_size: int = int(strength * image.size[0] / 20)
    
    if kernel_size < 1:
        return image  # No blur if intensity is too low
    
    # Create a horizontal motion blur kernel
    kernel: np.ndarray = np.zeros((kernel_size, kernel_size))
    kernel[int((kernel_size - 1) / 2), :] = np.ones(kernel_size)
    kernel = kernel / kernel_size
    
    # Convert the PIL image to a numpy array
    image_array: np.ndarray = np.array(image)
    
    # Apply the motion blur using the kernel with cv2's filter2D function
    blurred_array: np.ndarray = cv2.filter2D(image_array, -1, kernel)
    
    # Convert the numpy array back to a PIL image
    blurred_image: Image.Image = Image.fromarray(blurred_array)
    
    return blurred_image
