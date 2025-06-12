import re
from datetime import datetime

# Adjust the date pattern to match your locale, e.g. 'DD/MM/YY, HH:MM AM/PM' or 'MM/DD/YY, HH:MM'
# LINE_PATTERN = re.compile(
#     r'^(?P<date>\d{1,2}\/\d{1,2}\/\d{2,4})\,\s(?P<time>\d{1,2}\:\d{2})\s*\-\s*(?P<sender>[^:]*?)\:\s*(?P<message>.*)$'
# )

LINE_PATTERN = re.compile(
    r'(^(?P<date>\d{1,2}\/\d{1,2}\/\d{2,4})\,\s(?P<time>\d{1,2}\:\d{2})\s\W\s(?P<sender>[^:]*)\:(?P<message>.*)$|^(?P<message2>.*)$)'
)

date_start = datetime(2025, 6, 11, 0,0)
date_end = datetime(2025, 6, 12, 0,0)


def parse_date(date_str):
    date_format = '%d/%m/%y'
    current_date = None
    if not date_str:
        return None
    try:
        current_date = datetime.strptime(date_str, date_format)
    except ValueError:
        # Attempt alternative year-length or delimiter:
        try:
            current_date = datetime.strptime(date_str, '%d/%m/%Y')
        except ValueError:
            pass
    return current_date


def parse_timestamp(date_str, time_str):   
    # Construct full datetime string
    timestamp = None
    dt_format = '%d/%m/%y, %H:%M' # '%m/%d/%y, %I:%M' if '/' in date_str else 
    if not date_str or not time_str:
        return None

    date_str = f"{date_str}, {time_str}"
    try:
        timestamp = datetime.strptime(date_str, dt_format)
    except ValueError:
        # Attempt alternative year-length or delimiter:
        try:
            timestamp = datetime.strptime(date_str, '%d/%m/%Y, %H:%M')
        except ValueError:
            pass
    return timestamp


def parse_whatsapp_export(file_path):
    """Parse a WhatsApp-exported .txt chat and yield (datetime, sender, message)."""
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            m = LINE_PATTERN.match(line)
            if not m:
                # Handle continuation of a multiline message:
                if 'last_entry' in locals():
                    last_entry['message'] += '\n' + line
                continue

            date_str = m.group('date') if m.group('date') else ''
            time_str = m.group('time') if m.group('time') else ''
            # ampm = m.group('ampm') or ''  # e.g., “PM” or empty if 24-hour
            sender = m.group('sender').strip() if m.group('sender') else ''
            message = m.group('message').strip() if m.group('message') else ''
            message2 = m.group('message2').strip() if m.group('message2') else ''

            date_current = parse_date(date_str)
            if date_current and (date_current < date_start or date_current > date_end):
                continue

            # Construct full datetime string
            if date_str and time_str:
                timestamp = parse_timestamp(date_str, time_str)
                timestamp = timestamp if timestamp else datetime(0,0,0,0,0)
            elif message2:
                message = message2

            entry = {'timestamp': timestamp, 'sender': sender, 'message': message}
            yield entry
            last_entry = entry  # for multiline continuation

# Example usage:
if __name__ == '__main__':
    for entry in parse_whatsapp_export('sample_chat.txt'):
        if entry['timestamp']:
            print(f"[{entry['timestamp']:%Y-%m-%d %H:%M}] {entry['sender']}: {entry['message']}")
        elif entry['message']:
            print(f"[{entry['message']}")
