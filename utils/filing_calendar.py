from datetime import date, datetime

SEC_HOLIDAYS_2025 = {
    date(2025, 1, 1),   # New Year's Day
    date(2025, 1, 20),  # MLK Jr. Day / Inauguration Day
    date(2025, 2, 17),  # Washington's Birthday
    date(2025, 5, 26),  # Memorial Day
    date(2025, 6, 19),  # Juneteenth
    date(2025, 7, 4),   # Independence Day
    date(2025, 9, 1),   # Labor Day
    date(2025, 10, 13), # Columbus Day
    date(2025, 11, 11), # Veterans Day
    date(2025, 11, 27), # Thanksgiving Day
    date(2025, 12, 25), # Christmas Day
}

def is_sec_holiday(d: date) -> bool:
    return d in SEC_HOLIDAYS_2025

def is_valid_filing_day(d: date) -> bool:
    return d.weekday() < 5 and not is_sec_holiday(d)
