from moviepy.editor import (CompositeVideoClip,
                            ImageClip,
                            TextClip,
                            ColorClip)
import os
import sys
import csv
from PyQt6.QtWidgets import (QApplication,
                             QMainWindow,
                             QWidget,
                             QVBoxLayout,
                             QHBoxLayout,
                             QPushButton,
                             QFileDialog,
                             QTextEdit,
                             QSizePolicy,
                             QLabel,
                             QLineEdit)

# clear previous console prints
os.system('cls' if os.name == 'nt' else 'clear')

# setup variables
# default settings
fps = 12
total_duration = 7.0
font_size = 24
font_color = "white"
height_scale = .1
black_bar_scale = 1.4
black_bar_opacity = .6
zoom_factor_start = 2
zoom_factor_end = 1
csv_input = "example.csv"

# definitions
def create_directories(csv_file):
    with open(csv_file, "r") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            # Extract joke details from the CSV row
            setup = row["Setup"]
            punchline = row["Punchline"]
            os.makedirs(setup.rstrip('?'), exist_ok=True)
            with open(setup.rstrip('?') + '/' + 'dad-joke.txt', 'w') as f:
                f.write('"' + setup + '", "' + punchline + '"')
    status_textedit.setPlainText("Created directories from " + csv_file)

def setup_image(image_filepath):
    global image
    image = (ImageClip(image_filepath)
         .set_duration(total_duration)
         .set_position("center"))
    global width, height
    width = image.w
    height = image.h
    image = image.resize(lambda t: zoom_factor_start + (zoom_factor_end - zoom_factor_start) * t / image.duration)
    return image
    print("Image setup!")

def setup_joke(joke_filepath):
    # setup joke
    with open(joke_filepath, "r") as filestream:
        for line in filestream:
            currentline = line.split(",")
            setup = currentline[0].replace('"', '')
            punchline = currentline[1].replace('"', '')
    global text1, text2
    text1 = (TextClip(txt=setup,
                 size=(width, None),
                 fontsize=font_size,
                 color=font_color,
                 method="caption",
                 align="center")
                 .set_position(("center", height_scale*image.h))
                 .set_duration("5.0")
                 .set_start("0.0"))

    # setup punchline
    text2 = (TextClip(txt=punchline,
                 size=(width, None),
                 fontsize=font_size,
                 color=font_color,
                 method="caption",
                 align="center")
                 .set_position(("center", height_scale*image.h))
                 .set_duration("2.0")
                 .set_start("5.0"))
    return text1, text2

def create_video(setup, punchline, image, directory):
    max_text_height = max(setup.h, punchline.h)
    black_bar_y = height_scale*image.h - max_text_height*(black_bar_scale - 1)/2

    black_bar = (ColorClip(size=(image.w, int(black_bar_scale*max_text_height)),
                        color=(0, 0, 0))
                        .set_opacity(black_bar_opacity)
                        .set_position(("center", black_bar_y))
                        .set_duration(image.duration)
                        .set_start("0.0"))

    # create final clip
    final_clip = CompositeVideoClip([image, black_bar, text1, text2],
                                    size=(width, height))
    print(setup.txt)
    final_clip = final_clip.write_videofile(directory + "/" + directory + ".mp4", fps)

def scan_directories_and_create_video():
    created_video = False
    count_missing_image = 0
    string_missing_image = ""
    for dir in os.listdir("."):
        contains_joke = False
        joke_filepath = "path"
        contains_image = False
        image_filepath = "path"
        contains_video = False
        is_ready = False
        if os.path.isdir(dir) and dir != ".git":
            print("Found directory: ", dir)
            for file in os.listdir("./" + dir):
                print("\tFound file: \t", file)
                file_extension = os.path.splitext(file)[1]
                if file_extension == ".txt":
                    contains_joke = True
                    joke_filepath = dir + "/" + file
                if file_extension == ".jpg":
                    contains_image = True
                    image_filepath = file
                if file_extension == ".mp4":
                    contains_video = True               
            print("\tContains joke: \t", contains_joke)
            print("\tContains img: \t", contains_image)
            print("\tContains vid: \t", contains_video)
            if contains_image == False:
                count_missing_image += 1
                string_missing_image += dir + "\n"
            if contains_joke == True and contains_image == True and contains_video == False:
                is_ready = True
            if is_ready == True:
                print("------> ", dir, " is ready for video!")
                image = setup_image(image_filepath)
                text1, text2 = setup_joke(joke_filepath)
                create_video(text1, text2, image, dir)
                status_textedit.append("Created video: " + dir)
                created_video = True
            else:
                print("------> ", dir, " is __NOT__ ready for video!")
    if created_video == False:
        status_textedit.append("Found no directory ready for video...")
        status_textedit.append(str(count_missing_image) + " directories have missing images:")
        status_textedit.append(string_missing_image)


# GUI
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings_window = None  # Initialize the settings window instance variable
        self.setWindowTitle("Create YouTube Shorts")
        self.setGeometry(100, 100, 600, 240)  # Set window's default size

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        layout = QHBoxLayout(self.central_widget)

        # Buttons container
        button_layout = QVBoxLayout()

        # Select CSV button
        self.select_csv_button = QPushButton("✅ Select CSV")
        self.select_csv_button.clicked.connect(self.select_csv)
        button_layout.addWidget(self.select_csv_button)

        # Create Directories button
        self.create_directories_button = QPushButton("📁 Create Directories")
        self.create_directories_button.clicked.connect(self.create_directories)
        button_layout.addWidget(self.create_directories_button)

        # Create Videos button
        self.create_videos_button = QPushButton("▶️ Create Videos")
        self.create_videos_button.clicked.connect(self.create_videos)
        button_layout.addWidget(self.create_videos_button)

        # Create Settings button
        self.settings_button = QPushButton("⚙️ Settings")
        self.settings_button.clicked.connect(self.settings)
        button_layout.addWidget(self.settings_button)

        # Help button
        self.help_button = QPushButton("❓ Help")
        self.help_button.clicked.connect(self.show_help)
        button_layout.addWidget(self.help_button)

        layout.addLayout(button_layout)

        # TextEdit
        self.status_textedit = QTextEdit()
        self.status_textedit.setReadOnly(True)
        layout.addWidget(self.status_textedit)
        global status_textedit
        status_textedit = self.status_textedit

        # Set size policy to expand horizontally and vertically
        self.status_textedit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def select_csv(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("CSV Files (*.csv)")
        if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                global csv_input
                csv_input = selected_files[0]
                self.status_textedit.setPlainText(f"Selected CSV file: {csv_input}")

    def create_directories(self):
        self.status_textedit.setPlainText(f"Creating directories from {csv_input}...")
        create_directories(csv_input)

    def create_videos(self):
        self.status_textedit.setPlainText("Creating videos...")
        # Assign the values from settings to the variables
        if self.settings_window != None:
            settings = self.settings_window.get_settings()
            global fps, total_duration, font_size, font_color, height_scale, black_bar_scale, black_bar_opacity, zoom_factor_start, zoom_factor_end
            fps = int(settings["fps"])
            total_duration = float(settings["total_duration"])
            font_size = int(settings["font_size"])
            font_color = settings["font_color"]
            height_scale = float(settings["height_scale"])
            black_bar_scale = float(settings["black_bar_scale"])
            black_bar_opacity = float(settings["black_bar_opacity"])
            zoom_factor_start = float(settings["zoom_factor_start"])
            zoom_factor_end = float(settings["zoom_factor_end"])
        scan_directories_and_create_video()

    def settings(self):
        self.status_textedit.setPlainText("Opening settings window...")
        if self.settings_window is None:
            self.settings_window = Settings()  # Create the settings window instance
        self.settings_window.show()

    def show_help(self):
        # Show help message or open help dialog here
        help_message = ("**✅ Select CSV:** Opens a file dialog to select CSV. The CSV must have two columns: setup and punchline. Default CSV is example.csv.\n\n"
            "**📁 Create directories:** Creates directories based on 'setup' from selected CSV. Also creates a text-file in the directory.\n\n"
            "**▶️ Create videos:** Checks all directories if they have a text file and an image (jpg), but no video (mp4). If so, generates videos and places them in the corresponding directory.\n\n"
            "**⚙️ Settings:** Change various settings. Opens in a new window, close the window to save values.\n\n"
            "**❓ Help:** ☝️")

        self.status_textedit.setMarkdown(help_message)

# Settings window
class Settings(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings")
        
        # Create the central widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        
        # Create the layout
        layout = QVBoxLayout(self.central_widget)
        
        # Create labels and line edits for each setting
        labels = ["fps", "total_duration", "font_size", "font_color", "height_scale",
                  "black_bar_scale", "black_bar_opacity", "zoom_factor_start", "zoom_factor_end"]
        default_values = [12, 7.0, 24, "white", 0.1, 1.4, 0.6, 2, 1]
        self.line_edits = {}
        for label, default_value in zip(labels, default_values):
            # Create the label
            label_widget = QLabel(label)
            layout.addWidget(label_widget)
            
            # Create the line edit and set the default value
            line_edit = QLineEdit(str(default_value))
            self.line_edits[label] = line_edit
            layout.addWidget(line_edit)
        
    def get_settings(self):
        # Retrieve the values from the line edits and return as a dictionary
        settings = {}
        for label, line_edit in self.line_edits.items():
            settings[label] = line_edit.text()
        return settings


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())