from PIL import Image, ImageEnhance, ImageFilter

def darkness_filter(image: Image.Image, strength: float) -> Image.Image:
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(1.0 - strength)

def brightness_filter(image: Image.Image, strength: float) -> Image.Image:
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(strength*2 + 1.0)

def gaussian_blur_filter(image: Image.Image, strength: float) -> Image.Image:
    return image.filter(ImageFilter.GaussianBlur(radius=strength*5))

def colour_shift_filter(image: Image.Image, strength: float) -> Image.Image:
    print("colour shift")
    return image

def motion_blur_filter(image: Image.Image, strength: float) -> Image.Image:
    print("motion blur")
    return image