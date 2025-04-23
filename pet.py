import sys
import json
import os
import random  # Import random module
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QInputDialog, QMessageBox, QStatusBar, QFileDialog
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

# Save file path
SAVE_FILE = os.path.join(os.path.dirname(__file__), "pet_data.json")


class Pet:
    def __init__(self, name, hunger=5, energy=5, happiness=5, tricks=None):
        """
        Initialize the Pet object with name, hunger, energy, happiness, and tricks.
        """
        self.name = name
        self.hunger = hunger
        self.energy = energy
        self.happiness = happiness
        self.tricks = tricks or []

    def eat(self):
        """
        Feed the pet. Decrease hunger and slightly increase happiness.
        """
        self.hunger = max(0, self.hunger - 3)
        self.happiness = min(10, self.happiness + 1)

    def sleep(self):
        """
        Put the pet to sleep. Increase energy significantly.
        """
        self.energy = min(10, self.energy + 5)

    def play(self):
        """
        Play with the pet. Decrease energy, increase happiness, and slightly increase hunger.
        Returns True if the pet has enough energy to play, otherwise False.
        """
        if self.energy > 0:
            self.energy = max(0, self.energy - 2)
            self.happiness = min(10, self.happiness + 2)
            self.hunger = min(10, self.hunger + 1)
            return True
        return False

    def train(self, trick):
        """
        Teach the pet a new trick by adding it to the tricks list.
        """
        self.tricks.append(trick)

    def get_status(self):
        """
        Return the pet's current status as a formatted string.
        """
        return f"Hunger: {self.hunger}\nEnergy: {self.energy}\nHappiness: {self.happiness}"

    def show_tricks(self):
        """
        Return a comma-separated string of tricks the pet has learned.
        If no tricks are learned, return a default message.
        """
        return ", ".join(self.tricks) if self.tricks else "No tricks learned yet."

    def to_dict(self):
        """
        Convert the pet's attributes to a dictionary for saving to a file.
        """
        return {
            "name": self.name,
            "hunger": self.hunger,
            "energy": self.energy,
            "happiness": self.happiness,
            "tricks": self.tricks
        }

    @staticmethod
    def from_dict(data):
        """
        Create a Pet object from a dictionary.
        """
        return Pet(
            data["name"],
            data["hunger"],
            data["energy"],
            data["happiness"],
            data["tricks"]
        )


class PetApp(QWidget):
    def __init__(self, pet):
        """
        Initialize the PetApp GUI with the given pet object.
        """
        super().__init__()
        self.pet = pet
        self.stars = 0  # Initialize the star count
        self.setWindowTitle("Virtual Pet - PyQt6")
        self.setMinimumWidth(500)

        # Define light and dark mode stylesheets
        self.light_mode_stylesheet = """
            QWidget {
                background-color: #ffffff;  /* White background for light mode */
                font-family: 'Segoe UI', sans-serif;
                font-size: 10.5pt;
            }
            QLabel {
                color: #000000;  /* Black text for light mode */
            }
            QPushButton {
                background-color: #f0f0f0;  /* Light gray button background */
                color: #000000;  /* Black text for contrast */
                border: 1px solid #cccccc;  /* Light gray border */
                border-radius: 8px;
                padding: 4px 8px;  /* Smaller padding for smaller button size */
            }
            QPushButton:hover {
                background-color: #e0e0e0;  /* Slightly darker hover effect */
            }
            QStatusBar {
                background-color: #f0f0f0;  /* Light gray status bar background */
                color: #000000;  /* Black text for contrast */
                padding: 3px;
            }
        """

        self.dark_mode_stylesheet = """
            QWidget {
                background-color: #2b2b2b;  /* Dark gray background for dark mode */
                font-family: 'Segoe UI', sans-serif;
                font-size: 10.5pt;
            }
            QLabel {
                color: #e0e0e0;  /* Light gray text for dark mode */
            }
            QPushButton {
                background-color: #444444;  /* Darker button background */
                color: #ffffff;  /* White text for contrast */
                border: 1px solid #666666;  /* Slightly lighter border */
                border-radius: 8px;
                padding: 4px 8px;  /* Smaller padding for smaller button size */
            }
            QPushButton:hover {
                background-color: #555555;  /* Slightly lighter hover effect */
            }
            QStatusBar {
                background-color: #333333;  /* Darker status bar background */
                color: #e0e0e0;  /* Light gray text for contrast */
                padding: 3px;
            }
        """

        # Start in light mode
        self.setStyleSheet(self.light_mode_stylesheet)
        self.is_light_mode = True

        self.init_ui()

    def init_ui(self):
        """
        Set up the GUI layout and widgets.
        """
        # Pet Image
        self.pet_image = QLabel(self)
        self.pet_image.setFixedSize(150, 150)
        self.pet_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pet_image.setStyleSheet("border: 2px solid #aac4e2; border-radius: 10px; background-color: white;")
        self.load_default_image()

        # Button to upload a pet image
        self.upload_image_button = QPushButton("Upload Pet Image")
        self.upload_image_button.clicked.connect(self.upload_pet_image)

        # Toggle button to switch light/dark mode
        self.toggle_mode_button = QPushButton("Dark Mode")
        self.toggle_mode_button.setCheckable(True)  # Make it a toggle button
        self.toggle_mode_button.setFixedSize(100, 30)  # Smaller button size
        self.toggle_mode_button.clicked.connect(self.toggle_mode)

        # About button to explain achievements
        self.about_button = QPushButton("About")
        self.about_button.setFixedSize(100, 30)  # Smaller button size
        self.about_button.clicked.connect(self.show_about)

        # Pet Status Title
        self.status_title = QLabel("Pet Status", self)
        self.status_title.setStyleSheet("font-weight: bold; text-decoration: underline; font-size: 12pt;")
        self.status_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Status and Tricks
        self.status_label = QLabel(self.pet.get_status(), self)
        self.tricks_label = QLabel("Tricks: " + self.pet.show_tricks(), self)

        # Button Controls
        self.feed_button = QPushButton("Feed")
        self.feed_button.clicked.connect(self.feed_pet)

        self.sleep_button = QPushButton("Sleep")
        self.sleep_button.clicked.connect(self.sleep_pet)

        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.play_with_pet)

        self.train_button = QPushButton("Train Trick")
        self.train_button.clicked.connect(self.train_pet)

        self.status_button = QPushButton("Show Status")
        self.status_button.clicked.connect(self.update_status)

        self.save_button = QPushButton("Save Pet")
        self.save_button.clicked.connect(self.save_pet)

        # Layouts
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.pet_image)
        left_layout.addWidget(self.upload_image_button)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.status_title)  # Add the Pet Status title
        right_layout.addWidget(self.status_label)
        right_layout.addWidget(self.tricks_label)

        info_layout = QHBoxLayout()
        info_layout.addLayout(left_layout)
        info_layout.addLayout(right_layout)

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)
        grid.addWidget(self.feed_button, 0, 0)
        grid.addWidget(self.sleep_button, 0, 1)
        grid.addWidget(self.play_button, 1, 0)
        grid.addWidget(self.train_button, 1, 1)
        grid.addWidget(self.status_button, 2, 0)
        grid.addWidget(self.save_button, 2, 1)

        main_layout = QVBoxLayout()
        main_layout.addLayout(info_layout)
        main_layout.addSpacing(10)
        main_layout.addLayout(grid)

        # Add a status bar to display the pet's name and achievements
        self.status_bar = QStatusBar(self)
        self.status_bar.showMessage(f"Pet Name: {self.pet.name} | Achievements: {self.stars} ⭐")
        main_layout.addWidget(self.status_bar)

        # Add the toggle mode and about buttons below the status bar
        bottom_buttons_layout = QHBoxLayout()
        bottom_buttons_layout.addWidget(self.toggle_mode_button)
        bottom_buttons_layout.addWidget(self.about_button)
        main_layout.addLayout(bottom_buttons_layout)

        self.setLayout(main_layout)

    def toggle_mode(self):
        """
        Toggle between light mode and dark mode.
        """
        if self.is_light_mode:
            self.setStyleSheet(self.dark_mode_stylesheet)
            self.toggle_mode_button.setText("Light Mode")
        else:
            self.setStyleSheet(self.light_mode_stylesheet)
            self.toggle_mode_button.setText("Dark Mode")
        self.is_light_mode = not self.is_light_mode

    def show_about(self):
        """
        Show a message box explaining how achievement stars are awarded.
        """
        QMessageBox.information(
            self,
            "About Achievements",
            "Achievement stars are awarded when:\n"
            "- Hunger and Energy are balanced (both equal to 5).\n"
            "- Keep your pet happy and healthy to earn more stars!"
        )

    def load_default_image(self):
        """
        Load the default image or a placeholder if no image is available.
        """
        if os.path.exists("spider circle.png"):
            pixmap = QPixmap("spider circle.png").scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            
        else:
            pixmap = QPixmap(150, 150)
            pixmap.fill(Qt.GlobalColor.gray)
        self.pet_image.setPixmap(pixmap)

    def upload_pet_image(self):
        """
        Open a file dialog to allow the user to upload a pet image.
        """
        file_path, _ = QFileDialog.getOpenFileName(self, "Upload Pet Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            pixmap = QPixmap(file_path).scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.pet_image.setPixmap(pixmap)

    def update_status(self):
        self.status_label.setText(self.pet.get_status())
        self.tricks_label.setText("Tricks: " + self.pet.show_tricks())
        self.status_bar.showMessage(f"Pet Name: {self.pet.name} | Achievements: {self.stars} ⭐")  # Update the status bar with the pet's name and stars
        self.check_for_star()

    def check_for_star(self):
        """
        Check if the pet's hunger and energy are balanced and award a star if they are.
        Change the pet's values to random integers between 1 and 10 after awarding a star.
        """
        if self.pet.hunger == 5 and self.pet.energy == 5:
            self.stars += 1

            # Show the achievement message
            QMessageBox.information(self, "Achievement Unlocked!", "You earned a star for balancing hunger and energy!")

            # Change the pet's values to random integers between 1 and 10
            self.pet.hunger = random.randint(1, 10)
            self.pet.energy = random.randint(1, 10)
            self.pet.happiness = random.randint(1, 10)

            # Update the status bar with the new star count
            self.status_bar.showMessage(f"Pet Name: {self.pet.name} | Achievements: {self.stars} ⭐")

            # Update the UI to reflect the new random values
            self.status_label.setText(self.pet.get_status())

    def feed_pet(self):
        self.pet.eat()
        self.update_status()

    def sleep_pet(self):
        self.pet.sleep()
        self.update_status()

    def play_with_pet(self):
        if self.pet.play():
            self.update_status()
        else:
            QMessageBox.warning(self, "Too Tired", f"{self.pet.name} is too tired to play!")

    def train_pet(self):
        """
        Ask the user a math question (randomized operation). If they answer correctly,
        allow them to teach a new trick to the pet. Ensure trick is unique and not empty.
        """
        # Generate random numbers and choose a math operation
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        operation = random.choice(["+", "-", "*", "/"])

        if operation == "+":
            correct_answer = num1 + num2
        elif operation == "-":
            correct_answer = num1 - num2
        elif operation == "*":
            correct_answer = num1 * num2
        elif operation == "/":
            # Avoid division by zero and round to 1 decimal
            num2 = random.randint(1, 10)
            correct_answer = round(num1 / num2, 1)
            operation = "/"  # Confirm symbol

        # Ask the question
        question = f"What is {num1} {operation} {num2}?"
        answer, ok = QInputDialog.getText(self, "Math Challenge", question)

        if ok and answer.strip():
            try:
                user_answer = float(answer.strip()) if operation == "/" else int(answer.strip())

                if user_answer == correct_answer:
                    # Prompt for trick name
                    trick, ok = QInputDialog.getText(self, "Teach a Trick", "Enter a new trick:")
                    if ok and trick.strip():
                        trick = trick.strip()
                        if trick in self.pet.tricks:
                            QMessageBox.information(self, "Duplicate Trick", f"{self.pet.name} already knows this trick!")
                        else:
                            self.pet.train(trick)
                            QMessageBox.information(self, "Trick Learned", f"{self.pet.name} learned a new trick: {trick}!")
                            self.update_status()
                    else:
                        QMessageBox.information(self, "No Trick", "No trick was taught.")
                else:
                    QMessageBox.warning(self, "Wrong Answer", f"Incorrect! The correct answer was: {correct_answer}")
            except ValueError:
                QMessageBox.warning(self, "Invalid Input", "Please enter a valid number.")
        else:
            QMessageBox.information(self, "No Answer", "You did not answer the question.")

    def save_pet(self):
        try:
            with open(SAVE_FILE, "w") as f:
                json.dump(self.pet.to_dict(), f)
            QMessageBox.information(self, "Saved", "Pet state saved!")
        except (PermissionError, IOError) as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save pet data: {e}")


def load_pet():
    try:
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
            return Pet.from_dict(data)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        QMessageBox.critical(None, "Load Error", f"Failed to load pet data: {e}")
        return None


def main():
    app = QApplication(sys.argv)
    pet = load_pet()

    if not pet:
        name, ok = QInputDialog.getText(None, "Pet Name", "Enter your pet's name:")
        if not ok or not name.strip():
            sys.exit()
        pet = Pet(name.strip())

    window = PetApp(pet)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()