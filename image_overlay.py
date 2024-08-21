import cv2
import numpy as np
import sys

def enhance_overlay(overlay, effect_type):
    """Enhance the overlay based on the effect type."""
    if effect_type == "graffiti":
        # Increase contrast and brightness slightly for graffiti
        enhanced = cv2.convertScaleAbs(overlay, alpha=1.2, beta=15)
    elif effect_type == "fog":
        # increase contrast
        enhanced = cv2.convertScaleAbs(overlay, alpha=4.0, beta=30)
    else:
        # Default enhancement (for rain)
        enhanced = cv2.convertScaleAbs(overlay, alpha=1.0, beta=20)
    return enhanced

def add_overlay(background_path, output_path, effect_type):
    # Define overlay paths
    overlay_paths = {
        "rain": "C:/Users/cornf/OneDrive - The University of Western Australia/Year 3/Semester 1/CITS3200/Project/Images/rain.png",
        "fog": "C:/Users/cornf/OneDrive - The University of Western Australia/Year 3/Semester 1/CITS3200/Project/Images/fog.png",
        "graffiti": "C:/Users/cornf/OneDrive - The University of Western Australia/Year 3/Semester 1/CITS3200/Project/Images/graffiti.png"
    }
    
    # Validate effect type and get the overlay path
    if effect_type not in overlay_paths:
        print("Invalid effect type. Choose from 'rain', 'graffiti', or 'fog'.")
        sys.exit(1)
    
    overlay_path = overlay_paths[effect_type]

    # Read the background image
    background = cv2.imread(background_path)
    
    # Read the overlay image (supports transparency if the image has 4 channels)
    overlay = cv2.imread(overlay_path, cv2.IMREAD_UNCHANGED)
    
     # Resize overlay: make fog image larger by 20% (adjust as needed)
    if effect_type == "fog":
        # Increase size by 20% for fog
        new_width = int(background.shape[1] * 1.8)
        new_height = int(background.shape[0] * 1.8)
        overlay = cv2.resize(overlay, (new_width, new_height))
        
        # Center the resized fog image on the background
        start_x = (overlay.shape[1] - background.shape[1]) // 2
        start_y = (overlay.shape[0] - background.shape[0]) // 2
        overlay = overlay[start_y:start_y + background.shape[0], start_x:start_x + background.shape[1]]
    else:
        # Resize overlay to match background size
        overlay = cv2.resize(overlay, (background.shape[1], background.shape[0]))


    # Enhance the overlay for better visibility based on effect type
    overlay = enhance_overlay(overlay, effect_type)

    # Check if the overlay has an alpha channel (4 channels)
    if overlay.shape[2] == 4:
        # Extract the RGB and alpha channel separately
        overlay_rgb = overlay[:, :, :3]
        alpha_channel = overlay[:, :, 3] / 255.0  # Normalize alpha to be between 0 and 1
        
        # Adjust alpha (opacity) for better visibility based on effect type
        if effect_type == "graffiti":
            alpha_channel *= 1.0  # Less opaque for graffiti
        elif effect_type == "fog":
            alpha_channel *= 0.6  # More transparent for fog
        else:
            alpha_channel *= 1.2  # Rain effect

        alpha_channel = np.clip(alpha_channel, 0, 1)  # Ensure values are between 0 and 1

        # Blend each channel individually
        for c in range(0, 3):
            background[:, :, c] = (alpha_channel * overlay_rgb[:, :, c] + (1 - alpha_channel) * background[:, :, c])
    else:
        # If no alpha channel, apply a fixed transparency level
        alpha_channel = 0.7  # Adjust transparency here (0: fully transparent, 1: fully opaque)
        blended = cv2.addWeighted(background, 1, overlay, alpha_channel, 0)
        background = blended

    # Save the result without opening a window
    cv2.imwrite(output_path, background)

def main():
    if len(sys.argv) < 4:
        print("Usage: python image_overlay.py <background_path> <output_path> <effect_type>")
        print("Example: python image_overlay.py traffic.jpg output.jpg graffiti")
        sys.exit(1)
    
    background_path = sys.argv[1]
    output_path = sys.argv[2]
    effect_type = sys.argv[3].lower()

    add_overlay(background_path, output_path, effect_type)

if __name__ == "__main__":
    main()
