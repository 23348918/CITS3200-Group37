from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import cv2

def darkness_filter(image: Image.Image, strength: float) -> Image.Image:
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(1.0 - strength)

def brightness_filter(image: Image.Image, strength: float) -> Image.Image:
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(strength*2 + 1.0) 

def gaussian_blur_filter(image: Image.Image, strength: float) -> Image.Image:
    return image.filter(ImageFilter.GaussianBlur(radius=strength*5))

def intensity_filter(image: Image.Image, strength: float) -> Image.Image:
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(strength*2 + 1)

''' https://www.geeksforgeeks.org/opencv-motion-blur-in-python/ '''
def motion_blur_filter(image: Image.Image, strength: float) -> Image.Image:
    # Define the kernel size based on strength
    kernel_size = int(strength * image.size[0]/20)
    
    if kernel_size < 1:
        return image  # No blur if intensity is too low
    
    # Create a horizontal motion blur kernel
    kernel = np.zeros((kernel_size, kernel_size))
    kernel[int((kernel_size - 1) / 2), :] = np.ones(kernel_size)
    kernel = kernel / kernel_size
    
    # Convert the PIL image to a numpy array
    image_array = np.array(image)
    
    # Apply the motion blur using the kernel with cv2's filter2D function
    blurred_array = cv2.filter2D(image_array, -1, kernel)
    
    # Convert the numpy array back to a PIL image
    blurred_image = Image.fromarray(blurred_array)
    
    return blurred_image