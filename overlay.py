import cv2
import numpy as np
import sys

def enhance_overlay(overlay: np.ndarray, effect_type: str) -> np.ndarray:
    """
    @brief Enhances the overlay image based on the specified effect type.
    @param overlay (np.ndarray): The overlay image to enhance.
    @param effect_type (str): The type of effect ('rain', 'fog', 'graffiti', 'lens-flare', 'wet-filter').
    @return np.ndarray: The enhanced overlay image.
    """
    if effect_type == "graffiti":
        # Increase contrast and brightness slightly for graffiti
        return cv2.convertScaleAbs(overlay, alpha=1.2, beta=15)
    elif effect_type == "fog":
        # Increase contrast for fog
        return cv2.convertScaleAbs(overlay, alpha=4.0, beta=30)
    elif effect_type == "lens_flare":
        return cv2.convertScaleAbs(overlay, alpha=1.5, beta=50)
    else:
        # Default enhancement for rain effect
        return cv2.convertScaleAbs(overlay, alpha=1.0, beta=20)

def add_overlay(background_path: str, output_path: str, effect_type: str) -> None:
    """
    @brief Adds a specified overlay effect to a background image.
    @param background_path (str): Path to the background image.
    @param output_path (str): Path to save the output image.
    @param effect_type (str): The type of effect to apply ('rain', 'fog', 'graffiti','lens-flare', 'wet-filter').
    """
    # Define overlay paths
    overlay_paths = {
        "rain": r"Images\rain.png",
        "fog": r"Images\fog.png",
        "graffiti": r"Images\graffiti.png",
        "lens-flare": r"Images\lens_flare.png",
        "wet-filter": r"Images\wet_filter.png"
    }

    # Validate the effect type
    if effect_type not in overlay_paths:
        print("Invalid effect type. Choose from 'rain', 'graffiti', 'fog', 'lens-flare', or 'wet-filter'")
        sys.exit(1)
    
    overlay_path = overlay_paths[effect_type]

    # Read the background image
    background: np.ndarray = cv2.imread(background_path)
    
    # Read the overlay image (supports transparency if the image has 4 channels)
    overlay: np.ndarray = cv2.imread(overlay_path, cv2.IMREAD_UNCHANGED)
    
    # Resize overlay based on effect type
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
        # Resize overlay to match the background size
        overlay = cv2.resize(overlay, (background.shape[1], background.shape[0]))

    # Enhance the overlay for better visibility
    overlay = enhance_overlay(overlay, effect_type)

    # Blend the overlay with the background
    if overlay.shape[2] == 4:
        # Extract the RGB and alpha channel separately
        overlay_rgb: np.ndarray = overlay[:, :, :3]
        alpha_channel: np.ndarray = overlay[:, :, 3] / 255.0  # Normalize alpha to 0-1 range
        
        # Adjust alpha (opacity) based on effect type
        if effect_type == "graffiti":
            alpha_channel *= 1.0  # Less opaque for graffiti
        elif effect_type == "fog":
            alpha_channel *= 0.6  # More transparent for fog
        else:
            alpha_channel *= 1.2  # other effects

        alpha_channel = np.clip(alpha_channel, 0, 1)  # Ensure values are between 0 and 1

        # Blend each channel individually
        for c in range(3):
            background[:, :, c] = (alpha_channel * overlay_rgb[:, :, c] +
                                   (1 - alpha_channel) * background[:, :, c])
    else:
        # If no alpha channel, apply a fixed transparency level
        alpha_channel: float = 0.7  # Adjust transparency here (0: fully transparent, 1: fully opaque)
        background = cv2.addWeighted(background, 1, overlay, alpha_channel, 0)

    # Save the resulting image
    cv2.imwrite(output_path, background)

def main() -> None:
    """
    @brief Main function to handle command-line arguments and apply the overlay effect.
    """
    if len(sys.argv) < 4:
        print("Usage: python3 overlay.py <background_path> <output_path> <effect_type>")
        print("Example: python3 overlay.py traffic.jpg output.jpg graffiti")
        sys.exit(1)
    
    background_path: str = sys.argv[1]
    output_path: str = sys.argv[2]
    effect_type: str = sys.argv[3].lower()

    add_overlay(background_path, output_path, effect_type)

if __name__ == "__main__":
    main()
