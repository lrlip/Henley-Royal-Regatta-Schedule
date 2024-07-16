import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Optional
from tabulate import tabulate
from colorama import Fore, Style
import json

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

HENLEY_TIMETABLE_URL = "https://www.hrr.co.uk/2024-competition/race-timetable/"
VALID_GMT_OFFSETS = range(-12, 15)


class HenleySchedule():
    def __init__(self,
                 crew: List[str],
                 gmt_offset: int):
        self.crew = crew
        self.gmt_offset = gmt_offset

        self._validate_gmt_offset()
        self.url = HENLEY_TIMETABLE_URL
        self.trophy_boat_pair = self.load_trophy_boat_pair(
            'HenleySchedule/static/trohpy_boat_pair.json')

    def load_trophy_boat_pair(self, file_path: str) -> dict:
        with open(file_path, 'r') as file:
            return json.load(file)

    def show_race_schedule(self):
        soup = self.get_site_content()

        if soup is None:
            return

        race_date = self.clean_text(soup.find(class_='d-none d-md-inline'))
        header = f'Race Schedule for {race_date}'
        separator = '-' * len(header)
        print(Fore.BLUE + Style.BRIGHT + header + Style.RESET_ALL)
        print(Fore.BLUE + Style.BRIGHT + separator + Style.RESET_ALL)

        race_elements = self._get_time_table_rows(soup)
        if race_elements:
            self.print_race_schedule(race_elements=race_elements)
        else:
            logging.warning("No race elements found.")
        pass

    def get_site_content(self) -> BeautifulSoup | None:
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            return BeautifulSoup(response.content, "html.parser")
        except requests.RequestException as e:
            logging.error(f"Error fetching race data: {e}")
            return None

    def gmt_offset_header(self) -> str:
        if int(self.gmt_offset) > 0:
            gmt_offset_str = f'+{self.gmt_offset}'
        else:
            gmt_offset_str = f'{self.gmt_offset}'
        return gmt_offset_str

    def print_race_schedule(self, race_elements) -> None:
        logging.debug("Printing race schedule.")
        table = []

        gmt_offset_str = self.gmt_offset_header()
        headers = [Fore.CYAN + 'Race #',  'GB time', f'GMT {gmt_offset_str}', 'Berks station',
                   'Bucks station', 'Trophy', 'Boat' + Style.RESET_ALL]

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

            for search_string in self.crew:
                show_race = False
                # Make the matching crews bold
                if search_string.lower() in berk_station.lower():
                    berk_station = Style.BRIGHT + berk_station + Style.NORMAL
                    show_race = True
                if search_string.lower() in bucks_station.lower():
                    bucks_station = Style.BRIGHT + bucks_station + Style.NORMAL
                    show_race = True

                if show_race:
                    gb_time = race_time[:5]
                    gb_time_upd, local_time = self._convert_time_str_to_local_time_str(
                        gb_time)

                    table.append([race_number, Fore.YELLOW + gb_time_upd + Style.RESET_ALL,
                                  Fore.GREEN + local_time + Style.RESET_ALL,
                                  berk_station, bucks_station, trophy_name, trophy_boat])

        if table:
            print(tabulate(table, headers=headers, tablefmt='github'))
        else:
            print("No matching races found.")

        print()
        print(Fore.BLUE + "Go to Youtube: https://www.youtube.com/results?search_query=Henley+royal+regatta+live" + Style.RESET_ALL)

    def _convert_time_str_to_local_time_str(self, time_string):
        """Function that convert a time str '12:03' to a local timestring based on the given offset
        """
        hour_str = int(time_string.split(':')[0])
        minutes_str = time_string.split(':')[1]
        if hour_str < 8:
            hour_str += 12

        local_time_hour = (hour_str + self.gmt_offset) % 24

        return [f"{hour_str:02d}:{minutes_str}", f"{local_time_hour:02d}:{minutes_str}"]

    def _convert_pm_time_to_24_hours_time(self, time_string):
        """Function that convert a PM timestring '02:00' to '14:00'

        Args:
            time_string (_type_): _description_
        """
        pass

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
