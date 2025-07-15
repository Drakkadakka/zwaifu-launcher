#!/usr/bin/env python3
"""
Generate mobile app icons for Z-Waifu PWA
"""

import os
from PIL import Image, ImageDraw, ImageFont
import sys

def create_icon(size, output_path):
    """Create a simple icon with Z-Waifu branding"""
    # Create a new image with a dark background
    img = Image.new('RGBA', (size, size), (26, 26, 26, 255))  # Dark background
    draw = ImageDraw.Draw(img)
    
    # Calculate dimensions
    padding = size // 8
    inner_size = size - (padding * 2)
    
    # Draw main circle/background
    circle_color = (0, 153, 102, 255)  # Z-Waifu green
    draw.ellipse([padding, padding, padding + inner_size, padding + inner_size], 
                 fill=circle_color)
    
    # Add text or symbol
    try:
        # Try to use a font if available
        font_size = max(size // 4, 12)
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    # Add "ZW" text
    text = "ZW"
    text_color = (255, 255, 255, 255)  # White text
    
    # Calculate text position to center it
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    draw.text((x, y), text, fill=text_color, font=font)
    
    # Save the image
    img.save(output_path, 'PNG')
    print(f"Created icon: {output_path} ({size}x{size})")

def main():
    # Ensure static/mobile directory exists
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'mobile')
    os.makedirs(static_dir, exist_ok=True)
    
    # Generate icons for different sizes
    icon_sizes = [16, 32, 192, 512]
    
    for size in icon_sizes:
        output_path = os.path.join(static_dir, f'icon-{size}x{size}.png')
        create_icon(size, output_path)
    
    print("All mobile app icons generated successfully!")
    print(f"Icons saved to: {static_dir}")

if __name__ == "__main__":
    main() 