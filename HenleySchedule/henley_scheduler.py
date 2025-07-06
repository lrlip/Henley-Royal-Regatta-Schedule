import os
import sys

# Ensure UTF-8 encoding for the entire application
os.environ["PYTHONIOENCODING"] = "utf-8"

import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Optional, Dict, Any
from tabulate import tabulate
from colorama import Fore, Style
import json
import os
import time
from datetime import datetime, timedelta
import pytz
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
import yaml
import appdirs


# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

HENLEY_TIMETABLE_URL = "https://www.hrr.co.uk/race-timetable/"
VALID_GMT_OFFSETS = range(-12, 15)

# Initialize Rich console with UTF-8 support
console = Console(highlight=False, emoji=True, force_terminal=True, legacy_windows=False)

APP_NAME = "HenleySchedule"
class HenleySchedule():
    def __init__(self,
                 crew: List[str] = None,
                 gmt_offset: int = 1,
                 boat_type: str = None,
                 trophy: str = None):
        
        self.crew = crew if crew else []
        self.gmt_offset = gmt_offset
        self.boat_type = boat_type
        self.trophy = trophy       

        self._validate_gmt_offset()
        self.url = HENLEY_TIMETABLE_URL
        self.trophy_boat_pair = self.load_trophy_boat_pair(
            'HenleySchedule/static/trohpy_boat_pair.yaml')

    def load_trophy_boat_pair(self, file_path: str) -> dict:
        with open(file_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
         


    def show_race_schedule(self):            
       # Fetch fresh data with a progress spinner
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Fetching race data..."),
            console=console
        ) as progress:
            progress.add_task("Downloading", total=None)
            soup = self.get_site_content()
        
        if soup is None:
            return
            
        race_date = self.clean_text(soup.find(class_='d-none d-md-inline'))
        
        # Display header with rich
        console.print(Panel.fit(
            f"[bold blue]Race Schedule for {race_date}[/bold blue]",
            border_style="blue"
        ))

        race_elements = self._get_time_table_rows(soup)
        if race_elements:
            # Extract and save data
            races_data = self._extract_races_data(race_elements)
            
            # Process and display the data
            self._process_and_display_data(races_data)
        else:
            console.print("[yellow]No race elements found.[/yellow]")

    def _extract_races_data(self, race_elements) -> Dict:
        """Extract race data from HTML elements into a structured format"""
        races = []
        
        for race_element in race_elements:
            race_number = self._find_table_element(
                race_element, 'timetable-field-race')
            race_time = self._find_table_element(
                race_element, 'timetable-field-time')
            trophy_name = self._find_table_element(
                race_element, 'timetable-field-trophy')
            berk_station = self._find_table_element(
                race_element, 'timetable-field-berks')
            bucks_station = self._find_table_element(
                race_element, 'timetable-field-bucks')
            
            # Check if the trophy_name contains any of the keys in trophy_boat_pair dictionary
            trophy_boat = self._get_trophy_boat(trophy_name=trophy_name)
                
            gb_time = race_time[:5]
            gb_time_upd, local_time = self._convert_time_str_to_local_time_str(gb_time)
            
            race = {
                'number': race_number,
                'gb_time': gb_time_upd,
                'local_time': local_time,
                'berks_station': berk_station,
                'bucks_station': bucks_station,
                'trophy': trophy_name,
                'boat': trophy_boat
            }
            races.append(race)
            
        return {'races': races}
    
    def _get_trophy_boat(self, trophy_name: str) -> str:
        """Retrieve the boat type from the trophy name
        """
        return next(
                (value for key, value in self.trophy_boat_pair.items() if key in trophy_name),
                'Boat Not Found'
            )

    def _process_and_display_data(self, data: Dict):
        """Process and display race data with filtering"""
        races = data.get('races', [])
        filtered_races = []
        
        for race in races:
            # Apply filters
            if self.trophy and self.trophy.lower() != race['trophy'].lower():
                continue
                
            if self.boat_type and self.boat_type.lower() != race['boat'].lower():
                continue
            
            show_race = False
            berks_highlighted = race['berks_station']
            bucks_highlighted = race['bucks_station']
            
            # Apply special formatting for NED and D.S.R. Laga
            if "NED" in berks_highlighted:
                berks_highlighted = berks_highlighted.replace("NED", "[#FFA500]NED[/#FFA500]")
            if "NED" in bucks_highlighted:
                bucks_highlighted = bucks_highlighted.replace("NED", "[#FFA500]NED[/#FFA500]")
                
            if "D.S.R. Laga" in berks_highlighted:
                berks_highlighted = berks_highlighted.replace("D.S.R. Laga", "[red]D.S.R. Laga[/red]")
            if "D.S.R. Laga" in bucks_highlighted:
                bucks_highlighted = bucks_highlighted.replace("D.S.R. Laga", "[red]D.S.R. Laga[/red]")
            
            # If no crew filter, show all races
            if not self.crew:
                show_race = True
            else:
                for search_string in self.crew:
                    if search_string.lower() in race['berks_station'].lower():
                        berks_highlighted = f"[bold]{berks_highlighted}[/bold]"
                        show_race = True
                    if search_string.lower() in race['bucks_station'].lower():
                        bucks_highlighted = f"[bold]{bucks_highlighted}[/bold]"
                        show_race = True
            
            if show_race:
                race['berks_station'] = berks_highlighted
                race['bucks_station'] = bucks_highlighted
                filtered_races.append(race)
        
        self._display_races_table(filtered_races)

    def _display_races_table(self, races):
        """Display races in a rich formatted table"""
        if not races:
            console.print("[yellow]No matching races found.[/yellow]")
            return
            
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Race #")
        table.add_column("GB time")
        table.add_column(f"GMT {self.gmt_offset_header()}", style="green")
        table.add_column("Berks station")
        table.add_column("Bucks station")
        table.add_column("Trophy")
        table.add_column("Boat")
        
        for race in races:
            table.add_row(
                race['number'],
                race['gb_time'],
                race['local_time'],
                race['berks_station'],
                race['bucks_station'],
                race['trophy'],
                race['boat']
            )
            
        console.print(table)
        
        # Add YouTube link
        console.print("\n[link=https://www.youtube.com/results?search_query=Henley+royal+regatta+live]Watch Live on YouTube[/link]")
        console.print("")

    def get_site_content(self) -> Optional[BeautifulSoup]:
        try:
            # Create data directory if it doesn't exist
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
            os.makedirs(data_dir, exist_ok=True)
            
            response = requests.get(self.url)
            response.raise_for_status()
            
            # Store the HTML content in data directory with current date
            today = datetime.now().strftime('%Y-%m-%d')
            html_file_path = os.path.join(data_dir, f'{today}.html')
            
            with open(html_file_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
                
            logging.info(f"Stored HTML content in {html_file_path}")
            
            # Explicitly set encoding to utf-8
            return BeautifulSoup(response.content, "html.parser", from_encoding='utf-8')
        except requests.RequestException as e:
            console.print(f"[red]Error fetching race data: {e}[/red]")
            return None
        except IOError as e:
            logging.error(f"Error saving HTML content: {e}")
            # Continue with parsing even if saving fails
            return BeautifulSoup(response.content, "html.parser", from_encoding='utf-8')

    def gmt_offset_header(self) -> str:
        if int(self.gmt_offset) > 0:
            gmt_offset_str = f'+{self.gmt_offset}'
        else:
            gmt_offset_str = f'{self.gmt_offset}'
        return gmt_offset_str

    def _convert_time_str_to_local_time_str(self, time_string):
        """Function that convert a time str '12:03' to a local timestring based on the given offset
        """
        hour_str = int(time_string.split(':')[0])
        minutes_str = time_string.split(':')[1]
        if hour_str < 8:
            hour_str += 12

        local_time_hour = (hour_str + self.gmt_offset) % 24

        return [f"{hour_str:02d}:{minutes_str}", f"{local_time_hour:02d}:{minutes_str}"]

    def _find_table_element(self, table_row, class_element: str) -> str:
        return self.clean_text(table_row.find('td', class_=class_element))

    @staticmethod
    def clean_text(element: Optional[BeautifulSoup], default: str = "") -> str:
        if not element:
            return default
        try:
            # Try to get the text with proper UTF-8 encoding
            return element.get_text().replace('\n', '').strip()
        except UnicodeEncodeError:
            # Fallback for encoding issues
            return element.get_text(strip=True, separator=' ')

    @staticmethod
    def _get_time_table_rows(soup: BeautifulSoup) -> List[BeautifulSoup]:
        return soup.find_all('tr', {"class": 'timetable-row-r'})

    def _validate_gmt_offset(self):
        if self.gmt_offset not in VALID_GMT_OFFSETS:
            logging.error("Invalid GMT offset. Must be between -12 and +14.")
