import PySimpleGUI as Sg
import os
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO


class App:
    OK_FILETYPES = (".png", ".jpg", ".jpeg", ".tiff", ".bmp")
    MAX_IMAGE_DIM = MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT = (1280, 720)

    left_col = [[Sg.Text('In Folder'), Sg.In(enable_events=True, key='-IN FOLDER-'), Sg.FolderBrowse()],
                [Sg.Listbox(values=[], enable_events=True, size=(40, 20), key='-FILE LIST-',
                            select_mode=Sg.LISTBOX_SELECT_MODE_SINGLE)],
                [Sg.Checkbox('Horizontal Centre', default=True, enable_events=True, key='-H CEN-'),
                 Sg.Checkbox('Vertical Centre', default=False, enable_events=True, key='-V CEN-')],
                [Sg.Text('_' * 60)],
                [Sg.Text('Out Folder'), Sg.In(enable_events=True, key='-OUT FOLDER-'), Sg.FolderBrowse()],
                [Sg.Save('Save + Next', key='-SAVE-', disabled=True)]]

    images_col = [[Sg.Text(size=(80, 1), key='-TOUT-')],
                  [Sg.Graph(canvas_size=MAX_IMAGE_DIM,
                            graph_bottom_left=(0, -MAX_IMAGE_HEIGHT),
                            graph_top_right=(MAX_IMAGE_WIDTH, 0),
                            enable_events=True,
                            key="-GRAPH-")
                   ]]

    layout = [[Sg.Column(left_col, element_justification='c'), Sg.VSeperator(),
               Sg.Column(images_col, element_justification='c')]]

    def __init__(self):
        self.window = Sg.Window('Watermarking', App.layout, resizable=True, return_keyboard_events=True)

        self.current_filename = None
        self.current_image = None
        self.watermarked_image = None
        self.current_ratio = None
        self.centre_horizontal = True
        self.centre_vertical = False
        self.out_folder = None

        self._running = True
        self.event_loop()

    def event_loop(self):
        while self._running:
            event, values = self.window.read()
            print(event, values)

            if event == Sg.WIN_CLOSED or event == 'Exit':
                self._running = False
                break  # Runs into window.close()

            if event == '-IN FOLDER-':  # Folder name was filled in, make a list of files in the folder
                folder = values['-IN FOLDER-']
                try:
                    file_list = os.listdir(folder)  # get list of files in folder
                except Exception:
                    file_list = []
                file_names = [f for f in file_list if os.path.isfile(os.path.join(folder, f))
                              and f.lower().endswith(App.OK_FILETYPES)]  # Pick out the valid images
                self.window['-FILE LIST-'].update(file_names)  # Put the valid files in the UI list

            elif event == '-OUT FOLDER-':  # Set the folder to save files into
                self.out_folder = values['-OUT FOLDER-']
                self.window['-SAVE-'].update(disabled=False)

            elif event == '-FILE LIST-':  # A file was chosen from the listbox
                self.current_filename = values['-FILE LIST-'][0]
                if values['-IN FOLDER-']:
                    self.image_selected(os.path.join(values['-IN FOLDER-'], self.current_filename))

            elif event == '-H CEN-':  # Toggled Horizontal Centering
                self.centre_horizontal = values['-H CEN-']

            elif event == '-V CEN-':  # Toggled Vertical Centering
                self.centre_vertical = values['-V CEN-']

            elif event == '-GRAPH-' and self.current_filename:  # The image was clicked
                # Generate a watermarked image at the clicked location
                self.watermarked_image = self.watermark(self.current_image,
                                                        [x / self.current_ratio for x in values['-GRAPH-']])
                # Draw the watermarked image to the screen
                watermarked, _ = App.resize(self.watermarked_image)
                self.window['-GRAPH-'].Erase()
                self.window['-GRAPH-'].DrawImage(data=App.convert_to_bytes(watermarked), location=(0, 0))

            elif event == '-SAVE-' or (event == 's' and values['-OUT FOLDER-']):
                save_name = self.current_filename
                # Set the next item in the list box as the current item,
                try:
                    next_photo = self.window['-FILE LIST-'].get_list_values()[
                        self.window['-FILE LIST-'].get_list_values().index(self.current_filename) + 1
                        ]
                except Exception as E:
                    print(f'** Error {E} **')
                    next_photo = self.current_filename

                self.window['-FILE LIST-'].set_value(next_photo)
                self.current_filename = next_photo
                if self.current_filename:
                    self.image_selected(os.path.join(values['-IN FOLDER-'], self.current_filename))

                # If there is a watermarked image, save it (do this after rendering the new image for smoothness)
                if self.watermarked_image:
                    out_name = 'watermarked_' + save_name
                    self.watermarked_image.save(os.path.join(self.out_folder, out_name))
                    self.watermarked_image = None

        self.window.close()

    def image_selected(self, filepath):
        try:
            self.window['-TOUT-'].update(filepath)
            self.current_image = Image.open(filepath)
            image, self.current_ratio = App.resize(self.current_image)
            self.window['-GRAPH-'].Erase()
            self.window['-GRAPH-'].DrawImage(data=App.convert_to_bytes(image), location=(0, 0))
        except Exception as E:
            print(f'** Error {E} **')
            pass  # something weird happened making the full filename

    def watermark(self, input_image, centre, watermark_text='michaelllewelyn.com',
                  opacity=0.5):
        # The opaque white colour used for the watermark
        op_white = (255, 255, 255, round(255 * opacity))

        # Load the image to watermark and convert to RGBA so we can overlay the transparent layer
        photo = input_image.convert('RGBA')

        # Load Helvetica Bold
        font = ImageFont.truetype("fonts/Helvetica.ttf", round(photo.width / 15))

        # Draw the watermark text on a new RGBA layer
        text_layer = Image.new("RGBA", photo.size, (255, 255, 255, 0))
        text_drawing = ImageDraw.Draw(text_layer)
        text_width, text_height = text_drawing.textsize(watermark_text, font=font)

        x_pos = min(centre[0], photo.width)
        y_pos = min(-centre[1], photo.height)
        if self.centre_horizontal:
            x_pos = photo.width // 2
        if self.centre_vertical:
            y_pos = photo.height // 2

        text_drawing.text((x_pos - (text_width // 2),
                           y_pos - (text_height // 2)),
                          watermark_text, font=font, fill=op_white)

        # Merge the photo and watermark layers
        return Image.alpha_composite(photo, text_layer).convert("RGB")

    @staticmethod
    def resize(image):
        width, height = image.size
        if (ratio := min(App.MAX_IMAGE_WIDTH / width, App.MAX_IMAGE_HEIGHT / height)) < 1:
            image = image.resize((int(width * ratio), int(height * ratio)))
        else:
            ratio = 1

        return image, ratio

    @staticmethod
    def convert_to_bytes(image):
        with BytesIO() as bio:
            image.save(bio, format="PNG")
            del image
            return bio.getvalue()


if __name__ == '__main__':
    watermarking = App()
