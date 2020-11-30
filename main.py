import glob
import os
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


def watermark(input_image_path, output_image_path, watermark_text='michaelllewelyn.com',
              opacity=0.5, vertical_offset=1/8):
    # The opaque white colour used for the watermark
    op_white = (255, 255, 255, round(255 * opacity))

    # Load the image to watermark and convert to RGBA so we can overlay the transparent layer
    photo = Image.open(input_image_path).convert('RGBA')

    # Load Helvetica Bold
    font = ImageFont.truetype("fonts/Helvetica-Bold.ttf", round(photo.width / 15))

    # Draw the watermark text on a new RGBA layer in the centre + vertical offset
    text_layer = Image.new("RGBA", photo.size, (255, 255, 255, 0))
    text_drawing = ImageDraw.Draw(text_layer)
    text_width, text_height = text_drawing.textsize(watermark_text, font=font)
    text_drawing.text(((photo.width-text_width) // 2,
                       (photo.height-text_height) // 2 + round(photo.height * vertical_offset)),
                      watermark_text, font=font, fill=op_white)

    # Merge the photo and watermark layers
    out = Image.alpha_composite(photo, text_layer)

    # out.show()
    out.save(output_image_path)


if __name__ == '__main__':
    in_folder = '../unmarked-website-folders/2018 Jul-Aug Botswana/'
    out_folder = '../watermarked-website-folders/2018 Jul-Aug Botswana/'
    in_type = 'jpeg'

    # Loop over all the files in the in_folder
    images = glob.glob(in_folder + '*.' + in_type)
    count = len(images)
    completed = 0
    for image in images:
        print(title := image.split('\\')[-1].split('.')[0])

        watermark(image, out_folder + title + '_watermarked.png')
        completed += 1

        print(f"Completed {completed} out of {count}.")
