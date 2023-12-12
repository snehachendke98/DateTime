from datetime import timedelta, datetime
import json
from pytz import timezone
from parsedatetime import Calendar
import pytz


def contains_relative_keyword(input_text):
    keywords = ["today", "tomorrow", "yesterday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday",
                "sunday",
                "sun", "mon", "tue", "thur", "fri", "sat", "wed"]
    return any(keyword in input_text.lower() for keyword in keywords)


def converted_text(inputText):
    converted_text = inputText.lower()

    if contains_relative_keyword(inputText):
        digit_found = False
        if not digit_found:
            if "am" not in inputText and "pm" not in inputText:
                converted_text += " 12pm"

    return converted_text


def extract_date(inputText, adjusted_time, cal, timezone_str):
    text = converted_text(inputText)
    parsed_date, parsed_status = cal.parseDT(datetimeString=text, sourceTime=adjusted_time)
    time_component = (str(parsed_date).split(" ")[1]).split("+")[0]

    if parsed_status == 0:
        return "Date not found"

    parsed_time = datetime.strptime(time_component, "%H:%M:%S").time()
    current_time = '{:%H:%M:%S}'.format(adjusted_time)

    if str(parsed_time) == str(current_time):
        return "Date not found"

    return str(str(parsed_date).split(" ")[0] + "T" + time_component)


def extract_date_time(serviceInput):
    inputText = serviceInput['inputText']
    timezone_str = serviceInput['timeZone']
    now = datetime.now(timezone(timezone_str))
    original_time_str = now.strftime('%Y-%m-%d %H:%M:%S.%f%z')
    original_time = datetime.strptime(original_time_str, '%Y-%m-%d %H:%M:%S.%f%z')
    utc_offset = original_time.utcoffset()
    if contains_relative_keyword(inputText):
        adjusted_time = original_time + utc_offset
    else:
        adjusted_time = original_time
    original_timezone = pytz.timezone(timezone_str)
    target_timezone = pytz.timezone('UTC')
    cal = Calendar()
    parsed_date = extract_date(inputText, adjusted_time, cal, timezone_str)
    if parsed_date != 'Date not found':
        dt = datetime.strptime(parsed_date, '%Y-%m-%dT%H:%M:%S')
        utc_offset_diff = target_timezone.utcoffset(dt) - original_timezone.utcoffset(dt)
        converted_time = dt + utc_offset_diff
        final_parsed_date = int(converted_time.timestamp() * 1000)
        response = {'parsedDateTime': final_parsed_date}
    else:
        response = {'parsedDateTime': ""}
    return json.dumps(response)