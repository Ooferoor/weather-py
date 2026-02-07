from datetime import datetime

import requests
from rich import print as rprint
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

console = Console()

# The map for translating weather codes to readable text and emojis
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
    return None


def show_current_weather():
    console.clear()
    cityname = Prompt.ask("[bold cyan]Enter the city name[/bold cyan]")

    with console.status("[bold yellow]Searching...[/bold yellow]]\n"):
        res = get_location(
            cityname
        )  # Search for latitude and longitude of the city specified

        if res:
            lat, lon = res["latitude"], res["longitude"]
            # After latitute and longtitude of the city is found it searches a location with that latitude and longtitude for the weather and temperature
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code&temperature_unit=fahrenheit"
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code,apparent_temperature,relative_humidity_2m,wind_speed_10m&temperature_unit=fahrenheit"

            weather_data = requests.get(weather_url).json()

            # Tells the script how to find the temperature and translate it to Celsius from fahrenheit
            temp_f = weather_data["current"]["temperature_2m"]

            temp_c = (temp_f - 32) * 5 / 9

            feels_like_f = weather_data["current"]["apparent_temperature"]

            wind_speed = weather_data["current"]["wind_speed_10m"]
            humidity = weather_data["current"]["relative_humidity_2m"]

            temp_c = (temp_f - 32) * 5 / 9
            feels_like_c = (feels_like_f - 32) * 5 / 9


            # how to find the weather from the weather codes (etc, 67: Heavy Freezing Rain)
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

                f"[bold blue]Feels Like:[/bold blue]      {feels_like_f:.1f}°F ({feels_like_c:.1f}°C)\n"
                f"[bold blue]Wind Speed:[/bold blue]      {wind_speed} mph\n"
                f"[bold blue]Humidity:[/bold blue]        {humidity}%\n"
                f"[bold blue]Condition:[/bold blue]       {status}"
            ))

            rprint(
                Panel(
                    weather_info.strip(),
                    title="[bold magenta]Current Weather Results[/bold magenta]",
                    expand=False,
                )
            )
        else:
            rprint(
                Panel(f"[bold red]Could not find '{cityname}'. fuck you.[/bold red]")
            )


def show_forecast():
    console.clear()

    cityname = Prompt.ask("[bold cyan]Enter city for 7-day forecast[/bold cyan]")

    cityname = Prompt.ask(
        "[bold cyan]Enter city for 7-day forecast (not sure on realiblity right now)[/bold cyan]"
    )

    with console.status("[bold blue]Fetching forecast...[/bold blue]"):
        res = get_location(
            cityname
        )  # Search for latitude and longitude of the city specified

        if res:
            lat, lon = res["latitude"], res["longitude"]
            # This is where I am gonna put the 7 day future broadcast.
            forecast_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=weather_code,temperature_2m_max,temperature_2m_min&temperature_unit=fahrenheit&timezone=auto"

            forecast_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=weather_code,temperature_2m_max,temperature_2m_min&temperature_unit=fahrenheit&timezone=auto,apparent_temperature"
            data = requests.get(forecast_url).json()

            table = Table(
                title=f"7-Day Forecast for {res['name']}",
                show_header=True,
                header_style="bold magenta",
            )
            table.add_column("Date", style="dim")
            table.add_column("Condition")
            table.add_column("High (°F)", justify="right")
            table.add_column("Low (°F)", justify="right")

            daily = data["daily"]
            for i in range(len(daily["time"])):
                date_str = daily["time"][i]
                # Format date to be more readable (e.g., Mon, Jan 26)
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                formatted_date = date_obj.strftime("%a, %b %d")

                condition = WEATHER_MAP.get(daily["weather_code"][i], "Unknown")
                high = daily["temperature_2m_max"][i]
                low = daily["temperature_2m_min"][i]

                table.add_row(formatted_date, condition, f"{high}°", f"{low}°")

            rprint(table)
        else:
            rprint(
                Panel(f"[bold red]Could not find '{cityname}'. fuck you.[/bold red]")
            )


def main_menu():
    # Loop for the program so it doesn't abruptly stop and you can rerun it without having to do python3 weather.py
    while True:
        console.clear()
        # Display Menu
        menu_text = (
            "[1] 🌡️  Check Current Weather\n" "[2] 📅  7-Day Forecast\n" "[3] ❌  Exit"
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
        elif choice == "3":
            rprint("[bold red]Exiting... Goodbye![/bold red]")
            break


if __name__ == "__main__":
    main_menu()

    # Intergrate this with a tui map
