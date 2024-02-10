import csv
from datetime import datetime, timedelta
import pytz
import requests
import time

# Constants
BASE_URL = "https://app.whistle.com/api/pets/{}/dailies/"
HEADERS = {
    "Host": "app.whistle.com",
    "Accept": "application/vnd.whistle.com.v8+json",
    "baggage": "sentry-environment=production,sentry-public_key=f05c29ae6d914e1d8420ad3c1cc866f4,sentry-release=com.whistle.bob%405.21.0%2B5078.1,sentry-sampled=true,sentry-trace_id=0c3a40fae7544980a5666903d1ff1957,sentry-transaction=WLBootViewController",
    "Authorization": "Bearer XXXXX",
    "Accept-Unit-System": "imperial",
    "sentry-trace": "0c3a40fae7544980a5666903d1ff1957-17cb2a9882114044-1",
    "If-None-Match": "W/\"7899a21af3c778a2fde8a31bb60e4b56\"",
    "Accept-Language": "en",
    "Content-Type": "application/json",
    "User-Agent": "Winston/5.21.0 (iPhone; iOS 17.4; Build:5078.1; Scale/3.0)"
}
CSV_HEADERS = ['type', 'title', 'start_time', 'end_time', 'category', 'min_activity', 'calories', 'distance', 'distance_units', 'min_rest', 'duration']
EASTERN_TIMEZONE = pytz.timezone('America/New_York')


def days_since_epoch(date_string):
    time_tuple = time.strptime(date_string, "%Y-%m-%d")
    time_seconds = time.mktime(time_tuple)
    seconds_per_day = 60 * 60 * 24
    days_since_epoch = time_seconds / seconds_per_day
    return int(days_since_epoch)


def fetch_and_save_data(pet_id, start_date, end_date=None):
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    base_url = BASE_URL.format(pet_id)
    start_number = days_since_epoch(start_date)
    end_number = days_since_epoch(end_date)

    csv_file_path = f"daily_items_{pet_id}_{start_date}_{end_date}.csv"

    with open(csv_file_path, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_HEADERS)
        writer.writeheader()

        for number in range(start_number, end_number + 1):
            url = f"{base_url}{number}/daily_items"
            response = requests.get(url, headers=HEADERS)

            if response.status_code == 200:
                data = response.json()
                append_data_to_csv(data, writer)
                print(f"CSV data appended successfully for number {number}")
            else:
                print(f"Failed to fetch data for number {number}. Status code: {response.status_code}")

    print(f"Combined CSV file saved successfully as {csv_file_path}")


def append_data_to_csv(data, writer):
    for item in data.get('daily_items', []):
        start_time = parse_utc_to_eastern(item.get('start_time'))
        end_time = parse_utc_to_eastern(item.get('end_time'))

        row_data = {
            'type': item.get('type'),
            'title': item.get('title'),
            'start_time': start_time,
            'end_time': end_time
        }

        data_fields = item.get('data', {})
        for key in CSV_HEADERS[4:]:
            if key not in ['override_event_types', 'static_map_url']:
                row_data[key] = data_fields.get(key)

        writer.writerow(row_data)


def parse_utc_to_eastern(utc_time):
    utc_datetime = datetime.strptime(utc_time, "%Y-%m-%dT%H:%M:%SZ")
    eastern_datetime = utc_datetime.replace(tzinfo=pytz.utc).astimezone(EASTERN_TIMEZONE)
    return eastern_datetime.strftime("%Y-%m-%d %I:%M:%S %p")


if __name__ == "__main__":
    pet_id = input("Enter the pet ID: ")
    start_date = input("Enter the start date (YYYY-MM-DD): ")
    end_date = input("Enter the end date (YYYY-MM-DD) (optional, press Enter for today's date): ")
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    fetch_and_save_data(pet_id, start_date, end_date)
