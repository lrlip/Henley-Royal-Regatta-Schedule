import requests
from bs4 import BeautifulSoup
import argparse
import logging
from typing import List, Dict, Optional
from tabulate import tabulate
from colorama import Fore, Style, init

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

HENLEY_TIMETABLE_URL = "https://www.hrr.co.uk/2024-competition/race-timetable/"
VALID_GMT_OFFSETS = range(-12, 15)

# Initialize colorama
init(autoreset=True)


def fetch_race_data(url: str) -> Optional[str]:
    logging.debug(f"Fetching race data from {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()
        logging.debug("Successfully fetched race data.")
        return response.content
    except requests.RequestException as e:
        logging.error(f"Error fetching race data: {e}")
        return None


def parse_race_data(soup) -> List[BeautifulSoup]:
    logging.debug("Parsing race data.")
    return soup.find_all('tr', {"class": 'timetable-row-r'})


def convert_time_to_local(gb_time: str, gmt_offset: int) -> List[str]:

    if int(gb_time[:2]) < 8:
        gb_hours = int(gb_time[:2]) + 12
    else:
        gb_hours = int(gb_time[:2])
    gb_time_hour = gb_hours

    local_time_hour = (gb_hours + gmt_offset) % 24

    return [f'{gb_time_hour:02d}{gb_time[2:5]}', f'{local_time_hour:02d}{gb_time[2:5]}']


def clean_text(element: Optional[BeautifulSoup], default: str = "") -> str:
    """Extracts and cleans text from a BeautifulSoup element."""
    return element.text.replace('\n', '').strip() if element else default


def print_race_schedule(race_elements, search_strings: List[str], gmt_offset: int) -> None:
    logging.debug("Printing race schedule.")
    table = []
    headers = ['Race #', Fore.CYAN + 'GB time', 'Local Time', 'Berks station',
               'Bucks station', 'Trophy' + Style.RESET_ALL, 'Boat']

    for race_element in race_elements:
        race_number = clean_text(race_element.find(
            'td', class_='timetable-field-race'))
        trophy_name = clean_text(race_element.find(
            'td', class_='timetable-field-trophy'))
        berk_station = clean_text(race_element.find(
            'td', class_='timetable-field-berks'))
        bucks_station = clean_text(race_element.find(
            'td', class_='timetable-field-bucks'))
        bucks_berks = berk_station + ', ' + bucks_station

        for search_string in search_strings:
            if search_string.lower() in bucks_berks.lower():
                # Make the matching crews bold
                if search_string.lower() in berk_station.lower():
                    berk_station = Style.BRIGHT + berk_station + Style.NORMAL
                if search_string.lower() in bucks_station.lower():
                    bucks_station = Style.BRIGHT + bucks_station + Style.NORMAL

                time_str = clean_text(race_element.find(
                    'td', class_='timetable-field-time'))
                gb_time = time_str[:5]
                gb_time_upd, local_time = convert_time_to_local(
                    gb_time, gmt_offset=gmt_offset)

                table.append([race_number, Fore.YELLOW + gb_time_upd + Style.RESET_ALL,
                              Fore.GREEN + local_time + Style.RESET_ALL,
                              berk_station, bucks_station, trophy_name])

    if table:
        print(tabulate(table, headers=headers, tablefmt='simpel'))
    else:
        print("No matching races found.")

    print()
    print(Fore.BLUE + "Go to Youtube: https://www.youtube.com/results?search_query=Henley+royal+regatta+live" + Style.RESET_ALL)


def parse_race_date(soup: BeautifulSoup):
    return clean_text(soup.find(class_='d-none d-md-inline'))


def main(search_strings: List[str], gmt_offset: int) -> None:

    if gmt_offset not in VALID_GMT_OFFSETS:
        logging.error("Invalid GMT offset. Must be between -12 and +14.")
        return

    page_content = fetch_race_data(HENLEY_TIMETABLE_URL)

    if page_content:
        soup = BeautifulSoup(page_content, "html.parser")
        race_date = parse_race_date(soup)
        header = f'Race Schedule for {race_date}'
        separator = '-' * len(header)
        print(Fore.BLUE + Style.BRIGHT + header + Style.RESET_ALL)
        print(Fore.BLUE + Style.BRIGHT + separator + Style.RESET_ALL)
        race_elements = parse_race_data(soup)
        if race_elements:
            print_race_schedule(race_elements=race_elements,
                                search_strings=search_strings,
                                gmt_offset=gmt_offset)
        else:
            logging.warning("No race elements found.")
    else:
        logging.error("Failed to retrieve or parse the race data.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Fetch and display race timetable.')
    parser.add_argument('--crew', type=str, nargs='+', default='NED', required=False,
                        help='List of Strings that should be matched, separated by a space')
    parser.add_argument('--gmt', type=int, default=1, required=False,
                        help='GMT offset for local time display (default: 1 for NL time)')
    args = parser.parse_args()
    main(args.crew, args.gmt)
