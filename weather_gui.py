import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import threading
from weather_api import WeatherAPI

class WeatherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather App")
        self.root.geometry("600x500")
        self.root.configure(bg="#2c3e50")
        
        # Initialize API (you'll need to set your API key)
        self.api_key = "YOUR_API_KEY_HERE"  # Replace with your actual API key
        self.weather_api = WeatherAPI(self.api_key)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main title
        title_label = tk.Label(
            self.root, 
            text="🌤️ Weather App", 
            font=("Arial", 24, "bold"),
            bg="#2c3e50", 
            fg="white"
        )
        title_label.pack(pady=20)
        
        # Search frame
        self.create_search_frame()
        
        # Weather display frame
        self.weather_frame = tk.Frame(self.root, bg="#34495e", relief=tk.RAISED, bd=2)
        self.weather_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        
        # Loading label
        self.loading_label = tk.Label(
            self.weather_frame,
            text="Enter a city name to get weather information",
            font=("Arial", 14),
            bg="#34495e",
            fg="#bdc3c7"
        )
        self.loading_label.pack(expand=True)
    
    def create_search_frame(self):
        """Create the search input frame"""
        search_frame = tk.Frame(self.root, bg="#2c3e50")
        search_frame.pack(pady=10)
        
        tk.Label(
            search_frame, 
            text="Enter City:", 
            font=("Arial", 12),
            bg="#2c3e50", 
            fg="white"
        ).pack(side=tk.LEFT, padx=5)
        
        self.city_entry = tk.Entry(
            search_frame, 
            font=("Arial", 12),
            width=20,
            relief=tk.FLAT,
            bg="#ecf0f1"
        )
        self.city_entry.pack(side=tk.LEFT, padx=5)
        
        self.search_btn = tk.Button(
            search_frame,
            text="Get Weather",
            font=("Arial", 10, "bold"),
            bg="#3498db",
            fg="white",
            relief=tk.FLAT,
            padx=20,
            command=self.get_weather_threaded
        )
        self.search_btn.pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key to search
        self.city_entry.bind('<Return>', lambda e: self.get_weather_threaded())
        
    def get_weather_threaded(self):
        """Run weather fetching in a separate thread"""
        threading.Thread(target=self.get_weather, daemon=True).start()
        
    def get_weather(self):
        """Fetch weather data from API"""
        city = self.city_entry.get().strip()
        if not city:
            self.root.after(0, lambda: messagebox.showerror("Error", "Please enter a city name!"))
            return
            
        # Show loading (safely update from thread)
        self.root.after(0, lambda: self.update_loading_text("Loading weather data..."))
        
        try:
            # Get current weather
            status_code, current_data = self.weather_api.get_current_weather(city)
            
            if status_code is None:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Network error: {current_data}"))
                self.root.after(0, lambda: self.update_loading_text("Enter a city name to get weather information"))
                return
            elif status_code == 401:
                self.root.after(0, self.show_api_key_error)
                return
            elif status_code == 404:
                self.root.after(0, lambda: messagebox.showerror("Error", f"City '{city}' not found!"))
                self.root.after(0, lambda: self.update_loading_text("Enter a city name to get weather information"))
                return
            elif status_code != 200:
                self.root.after(0, lambda: messagebox.showerror("Error", "Failed to fetch weather data!"))
                self.root.after(0, lambda: self.update_loading_text("Enter a city name to get weather information"))
                return
                
            # Get forecast
            forecast_status, forecast_data = self.weather_api.get_forecast(city)
            forecast_data = forecast_data if forecast_status == 200 else None
            
            # Update UI in main thread
            self.root.after(0, lambda: self.display_weather(current_data, forecast_data))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
            self.root.after(0, lambda: self.update_loading_text("Enter a city name to get weather information"))
    
    def update_loading_text(self, text):
        """Safely update loading label text"""
        try:
            if self.loading_label.winfo_exists():
                self.loading_label.config(text=text)
        except tk.TclError:
            # Widget has been destroyed, ignore
            pass
    
    def show_api_key_error(self):
        """Show error message for missing/invalid API key"""
        error_msg = """API Key Required!

To use this weather app, you need a free API key from OpenWeatherMap:

1. Go to https://openweathermap.org/api
2. Sign up for a free account
3. Get your API key
4. Replace 'YOUR_API_KEY_HERE' in weather_gui.py with your actual API key

The free tier includes 1000 API calls per day."""
        
        messagebox.showerror("API Key Error", error_msg)
        self.update_loading_text("API key required - see error message for instructions")
    
    def display_weather(self, current_data, forecast_data):
        """Display weather information in the GUI"""
        # Clear previous content
        for widget in self.weather_frame.winfo_children():
            widget.destroy()
            
        # Current weather section
        self.create_current_weather_display(current_data)
        
        # Forecast section (if available)
        if forecast_data:
            self.create_forecast_display(forecast_data)
    
    def create_current_weather_display(self, current_data):
        """Create the current weather display"""
        current_frame = tk.Frame(self.weather_frame, bg="#34495e")
        current_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # City and country
        city_label = tk.Label(
            current_frame,
            text=f"{current_data['name']}, {current_data['sys']['country']}",
            font=("Arial", 18, "bold"),
            bg="#34495e",
            fg="white"
        )
        city_label.pack()
        
        # Current temperature
        temp_label = tk.Label(
            current_frame,
            text=f"{current_data['main']['temp']:.1f}°C",
            font=("Arial", 36, "bold"),
            bg="#34495e",
            fg="#f39c12"
        )
        temp_label.pack()
        
        # Weather description
        desc_label = tk.Label(
            current_frame,
            text=current_data['weather'][0]['description'].title(),
            font=("Arial", 14),
            bg="#34495e",
            fg="#ecf0f1"
        )
        desc_label.pack()
        
        # Weather details
        self.create_weather_details(current_frame, current_data)
    
    def create_weather_details(self, parent_frame, current_data):
        """Create weather details grid"""
        details_frame = tk.Frame(parent_frame, bg="#34495e")
        details_frame.pack(pady=10)
        
        details = [
            ("Feels like:", f"{current_data['main']['feels_like']:.1f}°C"),
            ("Humidity:", f"{current_data['main']['humidity']}%"),
            ("Pressure:", f"{current_data['main']['pressure']} hPa"),
            ("Wind:", f"{current_data['wind']['speed']} m/s"),
        ]
        
        for i, (label, value) in enumerate(details):
            row = i // 2
            col = i % 2
            
            detail_frame = tk.Frame(details_frame, bg="#34495e")
            detail_frame.grid(row=row, column=col, padx=20, pady=5, sticky="w")
            
            tk.Label(
                detail_frame,
                text=label,
                font=("Arial", 10),
                bg="#34495e",
                fg="#bdc3c7"
            ).pack(side=tk.LEFT)
            
            tk.Label(
                detail_frame,
                text=value,
                font=("Arial", 10, "bold"),
                bg="#34495e",
                fg="white"
            ).pack(side=tk.LEFT, padx=(5, 0))
    
    def create_forecast_display(self, forecast_data):
        """Create the forecast display"""
        forecast_frame = tk.Frame(self.weather_frame, bg="#2c3e50")
        forecast_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Label(
            forecast_frame,
            text="5-Day Forecast",
            font=("Arial", 14, "bold"),
            bg="#2c3e50",
            fg="white"
        ).pack(pady=(10, 5))
        
        # Create forecast items
        forecast_container = tk.Frame(forecast_frame, bg="#2c3e50")
        forecast_container.pack(fill=tk.X)
        
        # Get daily forecasts (one per day)
        daily_forecasts = []
        seen_dates = set()
        
        for item in forecast_data['list'][:15]:
            date = datetime.fromtimestamp(item['dt']).date()
            if date not in seen_dates:
                daily_forecasts.append(item)
                seen_dates.add(date)
                if len(daily_forecasts) >= 5:
                    break
        
        for item in daily_forecasts:
            self.create_forecast_item(forecast_container, item)
    
    def create_forecast_item(self, parent_frame, item):
        """Create a single forecast item"""
        day_frame = tk.Frame(parent_frame, bg="#34495e", relief=tk.RAISED, bd=1)
        day_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2, pady=5)
        
        # Day name
        day_name = datetime.fromtimestamp(item['dt']).strftime('%a')
        tk.Label(
            day_frame,
            text=day_name,
            font=("Arial", 10, "bold"),
            bg="#34495e",
            fg="white"
        ).pack(pady=2)
        
        # Temperature
        tk.Label(
            day_frame,
            text=f"{item['main']['temp']:.0f}°C",
            font=("Arial", 12, "bold"),
            bg="#34495e",
            fg="#f39c12"
        ).pack()
        
        # Description
        tk.Label(
            day_frame,
            text=item['weather'][0]['main'],
            font=("Arial", 8),
            bg="#34495e",
            fg="#bdc3c7"
        ).pack(pady=2)