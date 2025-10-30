from datetime import datetime, timedelta


def get_nearest_workday(date: datetime) -> datetime:
    day_of_week = date.weekday()
    if day_of_week >= 5:
        days_to_monday = 7 - day_of_week
        return date + timedelta(days=days_to_monday)
    return date


def get_first_week_date() -> datetime:
    now = datetime.now()
    first_semester_start = datetime(now.year, 9, 1)
    second_semester_start = datetime(now.year, 2, 1)
    if now < first_semester_start:
        if now < second_semester_start:
            semester_date = datetime(now.year - 1, 9, 1)
        else:
            semester_date = second_semester_start
    else:
        semester_date = first_semester_start
    return get_nearest_workday(semester_date)

