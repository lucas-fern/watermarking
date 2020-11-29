from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import os


def watermark(input_image_path, output_image_path, watermark_text='michaelllewelyn.com',
              opacity=0.5, vertical_offset=1/8):
    # The opaque white colour used for the watermark
    op_white = (255, 255, 255, round(255 * opacity))

    # Load the image to watermark and convert to RGBA so we can overlay the transparent layer
    photo = Image.open(input_image_path).convert('RGBA')

    # Load Helvetica Bold
    font = ImageFont.truetype("Helvetica-Font/Helvetica-Bold.ttf", round(photo.width / 15))

    # Draw the watermark text on a new RGBA layer in the centre + vertical offset
    text_layer = Image.new("RGBA", photo.size, (255, 255, 255, 0))
    text_drawing = ImageDraw.Draw(text_layer)
    text_width, text_height = text_drawing.textsize(watermark_text, font=font)
    text_drawing.text(((photo.width-text_width) // 2,
                       (photo.height-text_height) // 2 + round(photo.height * vertical_offset)),
                      watermark_text, font=font, fill=op_white)

    # Merge the photo and watermark layers
    out = Image.alpha_composite(photo, text_layer)

    out.show()
    out.save(output_image_path)


if __name__ == '__main__':
    in_folder = '../unmarked-website-folders/test/'
    out_folder = '../watermarked-website-folders/test/'

    # Loop over all the files in the in_folder
    for image in os.listdir(in_folder):
        title, extension = image.split('.')
        watermark(in_folder + image, out_folder + title + '_watermarked.png')
