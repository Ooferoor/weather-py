import requests
from rich import print as rprint
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

WEATHER_MAP = {
    0: "Clear sky ☀️",
    1: "Mainly clear 🌤️",
    2: "Partly cloudy ⛅",
    3: "Overcast ☁️",
    45: "Foggy 🌫️",
    48: "Depositing rime fog 🌫️",
    51: "Light drizzle 🌧️",
    53: "Moderate drizzle 🌧️",
    55: "Dense drizzle 🌧️",
    56: "Light freezing drizzle 🥶",
    57: "Dense freezing drizzle 🥶",
    61: "Slight rain 🌦️",
    63: "Moderate rain 🌧️",
    65: "Heavy rain ⛈️",
    66: "Light freezing rain 🧊",
    67: "Heavy freezing rain 🧊",
    71: "Slight snow fall ❄️",
    73: "Moderate snow fall ❄️",
    75: "Heavy snow fall ❄️",
    77: "Snow grains 🌨️",
    80: "Slight rain showers 🌦️",
    81: "Moderate rain showers 🌧️",
    82: "Violent rain showers ⛈️",
    85: "Slight snow showers 🌨️",
    86: "Heavy snow showers 🌨️",
    95: "Thunderstorm ⛈️",
    96: "Thunderstorm with slight hail ⛈️",
    99: "Thunderstorm with heavy hail ⛈️",
}


def get_weather():
    console.clear()
    cityname = Prompt.ask("[bold cyan]Enter the city name[/bold cyan]")

    with console.status("[bold yellow]Searching for location...[/bold yellow]"):
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={cityname}&count=1"  # Searching the API for the name of a city specified
        try:
            geo_data = requests.get(
                geo_url
            ).json()  # Search through the API in json for whatever the fuck
        except Exception as e:
            rprint(
                f"[bold red]Error connecting to API: {e}[/bold red]"
            )  # if didnt connect to API correctly
            return

    if "results" in geo_data:  # Search for latitude and longitude of the city specified
        res = geo_data["results"][0]
        lat, lon = res["latitude"], res["longitude"]

        with console.status("[bold blue]Fetching weather data...[/bold blue]"):
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code&temperature_unit=fahrenheit"  # After latitute and longtitude of the city is found it searches a location with that latitude and longtitude for the weather and temperature
            weather_data = requests.get(weather_url).json()
        # Tells the script how to find the temperature and translate it to Celsius from fahrenheit and how to find the weather from the weather codes (etc, 67: Heavy Freezing Rain)
        temp_f = weather_data["current"]["temperature_2m"]
        temp_c = (temp_f - 32) * 5 / 9
        code = weather_data["current"]["weather_code"]
        status = WEATHER_MAP.get(code, "Unknown")

        # UI for result
        weather_info = (
            f"[bold yellow]City:[/bold yellow] {res['name']}, {res.get('country', '')}\n"
            f"[bold yellow]Coordinates:[/bold yellow] {lat}, {lon}\n"
            f"---------------------------\n"
            f"[bold green]Temp Celsius:[/bold green]    {temp_c:.1f}°C\n"
            f"[bold green]Temp Fahrenheit:[/bold green] {temp_f:.1f}°F\n"
            f"[bold green]Condition:[/bold green]       {status}"
        )
        rprint(
            Panel(
                weather_info,
                title="[bold magenta]Weather Results[/bold magenta]",
                expand=False,
            )
        )
    else:
        rprint(
            Panel(
                f"[bold red]Could not find '{cityname}'. Please try again.[/bold red]"
            )
        )


def main_menu():  # Loop for the program so it doesn't abruptly stop and you can rerun it without having to do python3 weather.py
    while True:
        console.clear()
        # Display Menu
        menu_text = "[1] 🌡️  Check Temperature & Weather\n" "[2] ❌  Exit"
        rprint(
            Panel(
                Align.center(menu_text),
                title="[bold white]MAIN MENU[/bold white]",
                subtitle="Choose an option",
            )
        )

        choice = Prompt.ask("Select an option", choices=["1", "2"])

        if choice == "1":
            get_weather()
            input("\nPress Enter to return to the menu...")
        elif choice == "2":
            rprint("[bold red]Exiting... Goodbye![/bold red]")
            break


if __name__ == "__main__":
    main_menu()
