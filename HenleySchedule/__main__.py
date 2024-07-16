import argparse
from typing import List

from HenleySchedule.henley_scheduler import HenleySchedule


def main(search_strings: List[str], gmt_offset: int) -> None:
    scheduler = HenleySchedule(crew=search_strings,
                               gmt_offset=gmt_offset)
    scheduler.show_race_schedule()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Fetch and display race timetable.')
    parser.add_argument('--crew', type=str, nargs='+', default='NED', required=False,
                        help='List of Strings that should be matched, separated by a space')
    parser.add_argument('--gmt', type=int, default=1, required=False,
                        help='GMT offset for local time display (default: 1 for NL time)')
    args = parser.parse_args()
    main(args.crew, args.gmt)
