import requests
from bs4 import BeautifulSoup
import argparse
import logging
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

HENLEY_TIMETABLE_URL = "https://www.hrr.co.uk/2024-competition/race-timetable/"


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


def print_race_schedule(race_elements, search_strings: List[str], gmt_offset: int) -> None:
    logging.debug("Printing race schedule.")
    print('GB time  ', 'Local Time ', 'Berks station'.ljust(
        40), 'Bucks station'.ljust(40))

    for race_element in race_elements:
        berk_station = clean_text(race_element.find(
            'td', class_='timetable-field-berks'))
        bucks_station = clean_text(race_element.find(
            'td', class_='timetable-field-bucks'))
        bucks_berks = berk_station + ', ' + bucks_station

        for search_string in search_strings:
            if search_string.lower() in bucks_berks.lower():
                time_str = clean_text(race_element.find(
                    'td', class_='timetable-field-time'))
                gb_time = time_str[:5]
                local_time = convert_time_to_local(
                    gb_time, gmt_offset=gmt_offset)

                print(gb_time.ljust(9), local_time.ljust(11),
                      berk_station.ljust(40), bucks_station.ljust(40))


def parse_race_date(soup: BeautifulSoup):
    return clean_text(soup.find(class_='d-none d-md-inline'))


def main(search_strings: List[str],
         gmt_offset: int) -> None:
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
