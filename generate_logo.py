from PIL import Image, ImageDraw, ImageFont
import os

def create_topocoin_logo():
    # Create a 256x256 image
    img = Image.new('RGBA', (256, 256), (0, 123, 255, 255))  # Blue background
    draw = ImageDraw.Draw(img)

    # Draw a circle for the coin
    draw.ellipse((32, 32, 224, 224), fill=(255, 215, 0, 255))  # Gold color

    # Add text "TPC"
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
    except:
        font = ImageFont.load_default()

    # Center the text
    text = "TPC"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (256 - text_width) // 2
    y = (256 - text_height) // 2
    draw.text((x, y), text, fill=(0, 0, 0, 255), font=font)

    # Save the image
    img.save('logo.png')
    print("Logo created: logo.png")

if __name__ == "__main__":
    create_topocoin_logo()