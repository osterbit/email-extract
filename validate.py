import json
from datetime import datetime

def parse_date(date_str):
    # Remove the time zone abbreviation in parentheses
    date_str = date_str.split(' (')[0]
    # Define the format string
    format_str = "%a, %d %b %Y %H:%M:%S %z"
    # Parse and return the datetime object
    return datetime.strptime(date_str, format_str)

def find_min_max_dates(dict_list):
    # Convert all date strings to datetime objects
    date_times = [parse_date(d['date']) for d in dict_list]
    # Find minimum and maximum datetime
    min_date = min(date_times)
    max_date = max(date_times)
    # Return the results
    return min_date, max_date

def main():
    # Load the JSONL file
    with open('target_emails.jsonl', 'r') as file:
        dict_list = [json.loads(line) for line in file]
    
    # Find minimum and maximum dates
    min_date, max_date = find_min_max_dates(dict_list)
    
    # Print the results
    print(f"Minimum date: {min_date}")
    print(f"Maximum date: {max_date}")

if __name__ == "__main__":
    main()