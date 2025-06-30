import re
from datetime import datetime

# Adjust the date pattern to match your locale, e.g. 'DD/MM/YY, HH:MM AM/PM' or 'MM/DD/YY, HH:MM'
# LINE_PATTERN = re.compile(
#     r'^(?P<date>\d{1,2}\/\d{1,2}\/\d{2,4})\,\s(?P<time>\d{1,2}\:\d{2})\s*\-\s*(?P<sender>[^:]*?)\:\s*(?P<message>.*)$'
# )

LINE_PATTERN = re.compile(
    r'^(?P<date>\d{1,2}\.\d{1,2}\.\d{2,4})\,\s(?P<time>\d{1,2}\:\d{2})\s\W\s(?P<sender>[^:]*)\:(?P<message>.*)$'
)

TZ_PATTERN = re.compile(
    r'(?i)(?:\s*т\s*\/*\s*з\s*[-:]?\s*(\d+)|(\d+)\s*т\s*\/*\s*з|\s*ТЗ\s*(\d+)|\s*тз\s*(\d+))'
)
# r'(?i)(?:\s*т\s*\/*\s*з\s*-?\s*(\d+)|(\d+)\s*т\s*\/*\s*з|\s*ТЗ\s*(\d+)|\s*тз\s*(\d+))'

# r'(?i)(?:\s*т\s*\/*\s*з\s*-?\s*(\d{2})|(\d{2})\s*т\s*\/*\s*з|\s*ТЗ\s*(\d{2})|\s*тз\s*(\d{2}))'

# re.compile(
#     "(?i)(?:\s*т\s*[\/]?\s*з\s*-?\s*(\d+)|(\d+)\s*т\s*[\/]?\s*з|\s*т\s*з\s*(\d+))")

DATETIME_FORMAT = '%d.%m.%y, %H:%M'  # Adjust as needed for your locale
DATETIME_FORMAT_2 = '%d.%m.%Y, %H:%M'  # Adjust as needed for your locale
TIME_FORMAT = '%H:%M'
DATE_FORMAT = '%d.%m.%y'
DATE_FORMAT_2 = '%d.%m.%Y'  # Alternative date format

OUT_BP = ['Лісове','Трикутник','Олешки','Лозова']

date_start = datetime(2025, 6, 1, 0,0)
date_end = datetime(2025, 6, 30, 0,0)


def parse_date(date_str):
    date_format = DATE_FORMAT
    current_date = None
    if not date_str:
        return None
    try:
        current_date = datetime.strptime(date_str, date_format)
    except ValueError:
        # Attempt alternative year-length or delimiter:
        try:
            current_date = datetime.strptime(date_str, DATE_FORMAT_2)
        except ValueError:
            pass
    return current_date


def parse_timestamp(date_str, time_str):   
    # Construct full datetime string
    timestamp = None
    dt_format = DATETIME_FORMAT # '%m/%d/%y, %I:%M' if '/' in date_str else
    if not date_str or not time_str:
        return None

    date_str = f"{date_str}, {time_str}"
    try:
        timestamp = datetime.strptime(date_str, dt_format)
    except ValueError:
        # Attempt alternative year-length or delimiter:
        try:
            timestamp = datetime.strptime(date_str, DATETIME_FORMAT)
        except ValueError:
            pass
    return timestamp


def parse_whatsapp_export(file_path):
    """Parse a WhatsApp-exported .txt chat and yield (datetime, sender, message)."""
    messages = []
    last_entry = None

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            m = LINE_PATTERN.match(line)
            if not m:
                # Handle continuation of a multiline message:
                if last_entry:
                    last_entry['message'] += '\n' + line
                continue
            elif last_entry and m:
                if any(bp in last_entry['message'] for bp in OUT_BP):
                    messages.append(last_entry)  # Save the last entry before starting a new one
                last_entry = None  # Reset last_entry after processing

            date_str = m.group('date') if m.group('date') else ''
            time_str = m.group('time') if m.group('time') else ''
            # ampm = m.group('ampm') or ''  # e.g., “PM” or empty if 24-hour
            sender = m.group('sender').strip() if m.group('sender') else ''
            message = m.group('message').strip() if m.group('message') else ''
            # message2 = m.group('message2').strip() if m.group('message2') else ''

            date_current = parse_date(date_str)
            if date_current and (date_current < date_start or date_current > date_end):
                continue

            timestamp = None  # Default to None if no date/time is provided
            # Construct full datetime string
            if date_str and time_str:
                timestamp = parse_timestamp(date_str, time_str)
                timestamp = timestamp if timestamp else datetime(0,0,0,0,0)

            entry = {'timestamp': timestamp, 'sender': sender, 'message': message}
            #yield entry
            last_entry = entry  # for multiline continuation

    # continue from here process messages
    if len(messages) == 0:
        return
    tz_sum = 0
    for entry in messages:
        print(f"Timestamp: {entry['timestamp']}, Sender: {entry['sender']}, Message: {entry['message']}")
        print("\n" + "="*50 + "\n")
        mes = entry['message']
        match = re.search(TZ_PATTERN, mes)
        if match:
            tz = match.group(1) or match.group(2) or match.group(3) or match.group(4)
            tz_sum += float(tz)
    print('Total transport:', tz_sum)



# Example usage:
if __name__ == '__main__':
    parse_whatsapp_export('bp.txt')
