import sys
from PyQt6.QtWidgets import QApplication, QInputDialog

# Ensure the pet module is correctly imported
try:
    from pet import Pet, PetApp
except ImportError as e:
    print(f"Error importing module: {e}")
    sys.exit(1)

def main():
    # Create the QApplication instance
    app = QApplication(sys.argv)

    # Ask the user for a pet name
    name, ok = QInputDialog.getText(None, "Pet Name", "Enter your pet's name:")
    if not ok or not name.strip():
        print("No valid name provided. Exiting...")
        sys.exit(0)  # Exit gracefully if no valid name is given

    # Create the pet with the entered name
    try:
        user_pet = Pet(name.strip())
    except Exception as e:
        print(f"Error creating Pet instance: {e}")
        sys.exit(1)

    # Launch the app
    try:
        window = PetApp(user_pet)
        window.show()
    except Exception as e:
        print(f"Error launching PetApp: {e}")
        sys.exit(1)

    # Execute the application event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()