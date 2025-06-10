import re
from datetime import datetime

# Adjust the date pattern to match your locale, e.g. 'DD/MM/YY, HH:MM AM/PM' or 'MM/DD/YY, HH:MM'
# LINE_PATTERN = re.compile(
#     r'^(?P<date>\d{1,2}\/\d{1,2}\/\d{2,4})\,\s(?P<time>\d{1,2}\:\d{2})\s*\-\s*(?P<sender>[^:]*?)\:\s*(?P<message>.*)$'
# )

LINE_PATTERN = re.compile(
    r'(^(?P<date>\d{1,2}\/\d{1,2}\/\d{2,4})\,\s(?P<time>\d{1,2}\:\d{2})\s\W\s(?P<sender>[^:]*)\:(?P<message>.*)$|^(?P<message2>.*)$)'
)


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

            # Construct full datetime string
            dt_format = '%d/%m/%y, %H:%M' # '%m/%d/%y, %I:%M' if '/' in date_str else 
            if date_str and time_str:
                date_str = f"{date_str}, {time_str}"
                try:
                    timestamp = datetime.strptime(date_str, dt_format)
                except ValueError:
                    # Attempt alternative year-length or delimiter:
                    try:
                        timestamp = datetime.strptime(date_str, '%d/%m/%Y, %H:%M')
                    except ValueError:
                        continue  # skip malformed lines
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
