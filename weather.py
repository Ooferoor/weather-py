from datetime import datetime

import requests
from rich import print as rprint
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

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


def get_location(cityname):
    # Searching the API for the name of a city specified
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={cityname}&count=1"
    try:
        # Search through the API in json for whatever the fuck
        response = requests.get(geo_url).json()
        if "results" in response:
            return response["results"][0]
    except Exception as e:
        # if didnt connect to API correctly
        rprint(f"[bold red]Error connecting to API: {e}[/bold red]")
    return None


def show_current_weather():
    console.clear()
    cityname = Prompt.ask("[bold cyan]Enter the city name[/bold cyan]")

    with console.status("[bold yellow]Fetching weather...[/bold yellow]\n"):
        res = get_location(cityname)
        if not res:
            rprint(Panel(f"[bold red]Could not find '{cityname}'.[/bold red]"))
            return

        lat, lon = (
            res["latitude"],
            res["longitude"],
        )  # gets latitude and longitude of a city

        weather_url = (  # After latitute and longtitude of the city is found it searches a location with that latitude and longtitude for the weather and temperature
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,weathercode"
            f"&temperature_unit=fahrenheit&timezone=auto"
        )

        data = requests.get(weather_url).json()
        current = data.get("current", {})

        if not current:
            rprint(
                Panel(
                    f"[bold red]Weather data unavailable for '{cityname}'.[/bold red]"
                )
            )
            return

        temp_f = current.get("temperature_2m")
        feels_like_f = current.get("apparent_temperature")
        humidity = current.get("relative_humidity_2m")
        wind_speed = current.get("wind_speed_10m")
        code = current.get(
            "weathercode"
        )  # how to find the weather from the weather codes (etc, 67: Heavy Freezing Rain)

        temp_c = (temp_f - 32) * 5 / 9 if temp_f is not None else None
        feels_like_c = (feels_like_f - 32) * 5 / 9 if feels_like_f is not None else None

        status = WEATHER_MAP.get(code, "Unknown")

        temp_str = f"{temp_f:.1f}°F ({temp_c:.1f}°C)" if temp_f is not None else "N/A"
        feels_like_str = (
            f"{feels_like_f:.1f}°F ({feels_like_c:.1f}°C)"
            if feels_like_f is not None
            else "N/A"
        )
        humidity_str = f"{humidity}% " if humidity is not None else "N/A"
        wind_str = f"{wind_speed} mph" if wind_speed is not None else "N/A"

        weather_info = (
            f"[bold yellow]City:[/bold yellow] {res['name']}, {res.get('country','')}\n"
            f"[bold yellow]Coordinates:[/bold yellow] {lat}, {lon}\n"
            f"---------------------------\n"
            f"[bold green]Temperature:[/bold green]     {temp_str}\n"
            f"[bold blue]Feels Like:[/bold blue]       {feels_like_str}\n"
            f"[bold blue]Wind Speed:[/bold blue]       {wind_str}\n"
            f"[bold blue]Humidity:[/bold blue]         {humidity_str}\n"
            f"[bold blue]Condition:[/bold blue]        {status}"
        )

        rprint(
            Panel(
                weather_info.strip(),
                title="[bold magenta]Current Weather Results[/bold magenta]",
            )
        )


def show_forecast():
    console.clear()
    cityname = Prompt.ask("[bold cyan]Enter city for 7‑day forecast[/bold cyan]")

    with console.status("[bold blue]Fetching forecast...[/bold blue]"):
        res = get_location(cityname)
        if not res:
            rprint(Panel(f"[bold red]Could not find '{cityname}'.[/bold red]"))
            return

        lat, lon = res["latitude"], res["longitude"]

        forecast_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&daily=weathercode,temperature_2m_max,temperature_2m_min"
            f"&temperature_unit=fahrenheit&timezone=auto"
        )

        data = requests.get(forecast_url).json()
        daily = data.get("daily", {})

        if not daily:
            rprint(Panel(f"[bold red]Forecast data unavailable.[/bold red]"))
            return

        table = Table(
            title=f"7‑Day Forecast for {res['name']}",
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("Date", style="dim")
        table.add_column("Condition")
        table.add_column("High (°F)", justify="right")
        table.add_column("Low (°F)", justify="right")

        for i, date_str in enumerate(daily.get("time", [])):
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%a, %b %d")

            condition = WEATHER_MAP.get(daily.get("weathercode", [])[i], "Unknown")
            high = daily.get("temperature_2m_max", [])[i]
            low = daily.get("temperature_2m_min", [])[i]

            table.add_row(formatted_date, condition, f"{high}°", f"{low}°")

        rprint(table)


def main_menu():  # Loop for the program so it doesn't abruptly stop and you can rerun it without having to do python3 weather.py
    while True:
        console.clear()
        menu_text = (
            "[1] 🌡️  Check Current Weather\n" "[2] 📅  7‑Day Forecast\n" "[3] ❌  Exit"
        )
        rprint(
            Panel(
                Align.center(menu_text),
                title="[bold white]MAIN MENU[/bold white]",
                subtitle="Choose an option",
            )
        )
        choice = Prompt.ask("Select an option", choices=["1", "2", "3"])
        if choice == "1":
            show_current_weather()
            input("\nPress Enter to return to the menu...")
        elif choice == "2":
            show_forecast()
            input("\nPress Enter to return to the menu...")
        else:
            rprint("[bold red]Exiting... Goodbye![/bold red]")
            break


if __name__ == "__main__":
    main_menu()
