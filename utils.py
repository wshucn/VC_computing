import datetime


# check if target text is a valid date format
def validate_date(date_text, date_format):
    try:
        datetime.datetime.strptime(date_text, date_format)
        return True
    except ValueError:
        return False
