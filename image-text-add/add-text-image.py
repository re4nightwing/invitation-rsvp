from PIL import Image, ImageDraw, ImageFont
import os

# Define the function to create personalized invitation cards


def create_invitation(input_image_path, output_dir, name, font_path, y_position, font_size):
  # Create output directory if it doesn't exist
  if not os.path.exists(output_dir):
    os.makedirs(output_dir)

  # Load the font
  try:
    font = ImageFont.truetype(font_path, font_size)
  except IOError:
    print("Font file not found. Please check the font path.")
    return 0

  try:
    # Load the base invitation image
    image = Image.open(input_image_path)
    draw = ImageDraw.Draw(image)

      # Get image dimensions
    image_width, image_height = image.size

      # Calculate text size and x position for centering
    text_bbox = draw.textbbox((0, 0), name, font=font)  # Get bounding box
    text_width = text_bbox[2] - text_bbox[0]  # Width of the text
    x_position = (image_width - text_width) // 2  # Center text horizontally

      # Draw the name on the image
    draw.text((x_position, y_position), name, font=font, fill="black")

      # Save the personalized invitation
    output_path = os.path.join(output_dir, f"invitation_{name}.png")
    image.save(output_path)
    print(f"Saved: {output_path}")
  except Exception as e:
    flash(f'An error occurred: {str(e)}', 'danger')


# Input parameters
input_image_path = "template.png"
output_dir = "personalized_invitations"
name = "Dulan Pabasara"
font_path = "Birthstone-Regular.ttf"
y_position = 485
font_size = 30

# Generate invitations
create_invitation(input_image_path, output_dir, name, font_path, y_position, font_size)
