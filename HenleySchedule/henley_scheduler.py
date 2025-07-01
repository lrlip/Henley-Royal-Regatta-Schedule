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

HENLEY_TIMETABLE_URL = "https://www.hrr.co.uk/2024-competition/race-timetable/"
VALID_GMT_OFFSETS = range(-12, 15)
console = Console()

# Config and cache directories
APP_NAME = "HenleySchedule"
CONFIG_DIR = appdirs.user_config_dir(APP_NAME)
CACHE_DIR = appdirs.user_cache_dir(APP_NAME)
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.yaml")
CACHE_FILE = os.path.join(CACHE_DIR, "cache.json")
CACHE_EXPIRY = 3600  # Cache expiry in seconds (1 hour)


class HenleySchedule():
    def __init__(self,
                 crew: List[str] = None,
                 gmt_offset: int = 1,
                 boat_type: str = None,
                 trophy: str = None,
                 offline: bool = False,
                 notify: bool = False,
                 save_config: bool = False):
        
        self.crew = crew if crew else []
        self.gmt_offset = gmt_offset
        self.boat_type = boat_type
        self.trophy = trophy

        # Initialize config and cache directories
        os.makedirs(CONFIG_DIR, exist_ok=True)
        os.makedirs(CACHE_DIR, exist_ok=True)

        # Load user config if exists
        self._load_config()
        

        self._validate_gmt_offset()
        self.url = HENLEY_TIMETABLE_URL
        self.trophy_boat_pair = self.load_trophy_boat_pair(
            'HenleySchedule/static/trohpy_boat_pair.json')

    def load_trophy_boat_pair(self, file_path: str) -> dict:
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            # Look for the file in the installed package
            package_dir = os.path.dirname(os.path.abspath(__file__))
            alt_path = os.path.join(package_dir, 'static', 'trohpy_boat_pair.json')
            with open(alt_path, 'r') as file:
                return json.load(file)

    def _load_config(self):
        """Load user configuration if it exists"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = yaml.safe_load(f)
                    
                # Only load config values if they're not already set
                if not self.crew and 'default_crews' in config:
                    self.crew = config['default_crews']
                if self.gmt_offset == 1 and 'gmt_offset' in config:
                    self.gmt_offset = config['gmt_offset']
                if not self.boat_type and 'default_boat_type' in config:
                    self.boat_type = config['default_boat_type']
                if not self.trophy and 'default_trophy' in config:
                    self.trophy = config['default_trophy']
                    
                logging.info(f"Loaded configuration from {CONFIG_FILE}")
            except Exception as e:
                logging.error(f"Error loading config: {e}")

    def _save_config(self):
        """Save current settings as default configuration"""
        config = {
            'default_crews': self.crew,
            'gmt_offset': self.gmt_offset,
            'default_boat_type': self.boat_type,
            'default_trophy': self.trophy
        }
        
        try:
            with open(CONFIG_FILE, 'w') as f:
                yaml.dump(config, f)
            console.print(f"[green]Configuration saved to {CONFIG_FILE}[/green]")
        except Exception as e:
            console.print(f"[red]Error saving configuration: {e}[/red]")

    def _load_cache(self) -> Optional[Dict[str, Any]]:
        """Load cached race data if it exists and is not expired"""
        if not os.path.exists(CACHE_FILE):
            return None
            
        try:
            with open(CACHE_FILE, 'r') as f:
                cache = json.load(f)
                
            # Check if cache is expired
            cache_time = cache.get('timestamp', 0)
            if time.time() - cache_time > CACHE_EXPIRY:
                logging.info("Cache expired, will fetch fresh data")
                return None
                
            return cache.get('data')
        except Exception as e:
            logging.error(f"Error loading cache: {e}")
            return None

    def _save_cache(self, data: Dict[str, Any]):
        """Save race data to cache"""
        cache = {
            'timestamp': time.time(),
            'data': data
        }
        
        try:
            with open(CACHE_FILE, 'w') as f:
                json.dump(cache, f)
            logging.info(f"Data cached to {CACHE_FILE}")
        except Exception as e:
            logging.error(f"Error saving cache: {e}")

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
            self._save_cache(races_data)
            
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
            
            trophy_boat = self.trophy_boat_pair.get(
                trophy_name, 'Boat Not Found')
                
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
            
            # If no crew filter, show all races
            if not self.crew:
                show_race = True
            else:
                for search_string in self.crew:
                    if search_string.lower() in race['berks_station'].lower():
                        berks_highlighted = f"[bold]{race['berks_station']}[/bold]"
                        show_race = True
                    if search_string.lower() in race['bucks_station'].lower():
                        bucks_highlighted = f"[bold]{race['bucks_station']}[/bold]"
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
        table.add_column("GB time", style="yellow")
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

    def get_site_content(self) -> Optional[BeautifulSoup]:
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            return BeautifulSoup(response.content, "html.parser")
        except requests.RequestException as e:
            console.print(f"[red]Error fetching race data: {e}[/red]")
            return None

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
        """Extracts and cleans text from a BeautifulSoup element."""
        return element.text.replace('\n', '').strip() if element else default

    @staticmethod
    def _get_time_table_rows(soup: BeautifulSoup) -> List[BeautifulSoup]:
        return soup.find_all('tr', {"class": 'timetable-row-r'})

    def _validate_gmt_offset(self):
        if self.gmt_offset not in VALID_GMT_OFFSETS:
            logging.error("Invalid GMT offset. Must be between -12 and +14.")
