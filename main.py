import tkinter as tk
from weather_gui import WeatherGUI

def main():
    """Main function to run the weather app"""
    root = tk.Tk()
    app = WeatherGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()