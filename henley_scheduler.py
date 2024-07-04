import requests
from bs4 import BeautifulSoup
import argparse
import logging
from typing import List, Dict, Optional
from ics import Calendar, Event

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

HENLEY_TIMETABLE_URL = "https://www.hrr.co.uk/2024-competition/race-timetable/"
VALID_GMT_OFFSETS = range(-12, 15)

TROHPY_BOAT_PAIR = {'Britannia': 'M4+',
                    'Diamond': 'M1x',
                    'Diamonds': 'M1x',
                    'Goblets': 'M2-',
                    'Hambleden': 'W2-',
                    'Island': 'W8+',
                    "Ladies'": 'M8+',
                    'P. Albert': 'M4+',
                    'P. Wales': 'M4x',
                    'P. Royal': 'W1x',
                    'P.Grace': 'M4x',
                    'Princess Grace': 'W4x',
                    'Queen Mother': 'M4x',
                    'Remenham': 'W8+',
                    'Stewards': 'M4-',
                    'Stoner': 'W2x',
                    'Temple': 'M8+',
                    'Town': 'W4-',
                    'Visitors': 'M4-',
                    'Wyfold': 'M4-'
                    }


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


def convert_time_to_local(gb_time: str, gmt_offset: int) -> str:
    time_hour = int(gb_time[:2])
    local_time_hour = (time_hour + gmt_offset) % 24
    return f'{local_time_hour:02d}{gb_time[2:5]}'


def clean_text(element: Optional[BeautifulSoup], default: str = "") -> str:
    """Extracts and cleans text from a BeautifulSoup element."""
    return element.text.replace('\n', '').strip() if element else default


def create_ics_event(calendar: Calendar,
                     race_date: str,
                     local_time: str,
                     berk_station: str,
                     bucks_station: str,
                     trophy_name: str,
                     trophy_boat: str):
    event = Event()
    event.name = f'{trophy_name} - {trophy_boat}'
    event.begin = f'{race_date} {local_time}:00'
    event.description = f'Race between {berk_station} and {bucks_station}'
    calendar.events.add(event)


def print_race_schedule(race_elements, search_strings: List[str], gmt_offset: int) -> None:
    logging.debug("Printing race schedule.")
    print('GB time  ', 'Local Time  ', 'Berks station'.ljust(
        40), 'Bucks station'.ljust(40), 'Trophy')

    for race_element in race_elements:
        trophy_name = clean_text(race_element.find(
            'td', class_='timetable-field-trophy'))
        trophy_boat = TROHPY_BOAT_PAIR.get(trophy_name, 'Boat Not Found')

        berk_station = clean_text(race_element.find(
            'td', class_='timetable-field-berks'))
        bucks_station = clean_text(race_element.find(
            'td', class_='timetable-field-bucks'))
        bucks_berks = berk_station + ', ' + bucks_station

        for search_string in search_strings:
            if search_string.lower() not in bucks_berks.lower():
                continue

            time_str = clean_text(race_element.find(
                'td', class_='timetable-field-time'))
            gb_time = time_str[:5]
            local_time = convert_time_to_local(
                gb_time, gmt_offset=gmt_offset)

            print(gb_time.ljust(9), local_time.ljust(12),
                  berk_station.ljust(40), bucks_station.ljust(40), f'{trophy_name} - {trophy_boat}')

            calendar = Calendar()
            create_ics_event(calendar,
                             '2024-02-07', local_time,
                             berk_station, bucks_station, trophy_name, trophy_boat)
        with open('race_schedule.ics', 'w') as f:
            f.writelines(calendar)


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
        race_elements = parse_race_data(soup)
        print(f'Race Schedule for {race_date}')
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
                        help='List of Strings that should be matched, seperated by a space')
    parser.add_argument('--gmt', type=int, default=1, required=False,
                        help='GMT offset for local time display (default: 1 for NL time)')
    args = parser.parse_args()
    main(args.crew, args.gmt)
