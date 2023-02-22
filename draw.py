import sys
from PIL import Image
from pynput import mouse
import pyautogui

# Get the filename from the command line argument
if len(sys.argv) < 2:
    print("Usage: python script_name.py image_file")
    sys.exit()
filename = sys.argv[1]

# Open the image using PIL
try:
    image = Image.open(filename)
except IOError:
    print("Error: Failed to open the image file.")
    sys.exit()


def draw_line(coords):
    if coords[0]:
        start_x, start_y = coords[0]
        if coords[1]:
            end_x, end_y = coords[1]

            pyautogui.moveTo(start_x, start_y)
            pyautogui.dragTo(end_x, end_y, button='left')
        else:
            pyautogui.click(start_x, start_y)


def compress_coordinates(coords):
    if len(coords) <= 2:
        return coords

    result = [coords[0]]

    i = 0
    while i < len(coords) - 1:
        if coords[i+1][0] - coords[i][0] == 1:
            i += 1
        else:
            result.append(coords[i])
            i += 1

            if coords[i]:
                result.append(coords[i])
    result.append(coords[-1])

    return result


def is_pixel_mostly_white(pixel):
    r, g, b = pixel
    return (r >= 180) and (g >= 180) and (b >= 180)


def pair_coordinates(coords):
    pairs = []
    for i in range(0, len(coords)-1, 2):
        pairs.append([coords[i], coords[i+1]])
    return pairs

# Define a function to parse the image


def parse_image(img, x1, y1, x2, y2):

    # Calculate width and height of selection
    selection_width = abs(x2 - x1)
    selection_height = abs(y2 - y1)

    # Resize image to fit selection while maintaining aspect ratio
    aspect_ratio = image.size[1] / image.size[0]
    new_width = int(selection_width)
    new_height = int(new_width * aspect_ratio)

    if new_height > selection_height:
        new_height = int(selection_height)
        new_width = int(new_height / aspect_ratio)

    img = image.resize((new_width, new_height))

    # Parse the pixel values and cursor locations in the selection box
    pixel_array = []
    for y in range(img.size[1]):
        row = []
        for x in range(img.size[0]):
            pixel = img.getpixel((x, y))
            cursor_x = x + x1
            cursor_y = y + y1
            if not is_pixel_mostly_white(pixel):
                row.append((int(cursor_x), int(cursor_y)))
        if row:
            pixel_array.append(row)
    if not pixel_array:
        print("Image is mostly white, skipping pixel array storage.")
        return None
    print("Image parsed successfully.")
    return pixel_array


# Define a callback function to handle mouse clicks
def on_click(x, y, button, pressed):
    global click_count, click_coords
    if pressed:
        click_count += 1
        click_coords.append((x, y))
        if click_count == 2:
            groups = []
            # Parse the image in the selection box
            x1, y1 = click_coords[0]
            x2, y2 = click_coords[1]

            coordinate_array = parse_image(image, x1, y1, x2, y2)
            for coord in coordinate_array:
                groups.append(compress_coordinates(coord))
            flat_list = pair_coordinates(
                [item for sublist in groups for item in sublist])

            for group in flat_list:
                draw_line(group)

            sys.exit()


# Print instructions for the user
print("Press Ctrl+C to exit.")

# Create a mouse listener and start listening for clicks
click_count = 0
click_coords = []
with mouse.Listener(on_click=on_click) as listener:
    listener.join()
