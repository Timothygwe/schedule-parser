import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from ..constants.weekdays import WEEK_DAYS


class ParsersService:
    @staticmethod
    def parse_semester_schedule_page(
        html: str
    ) -> Dict[int, Dict[str, List[dict]]]:
        """
        Парсит HTML-страницу с расписанием семестра.
        """
        soup = BeautifulSoup(html, "lxml")
        rows = soup.select("tbody > tr")

        result: Dict[int, Dict[str, List[dict]]] = {}
        current_day: Optional[str] = None

        for row in rows:
            cells = row.find_all("td")
            if not cells:
                continue

            if "wday" in row.get("class", []):
                current_day = cells[0].get_text(strip=True)
                continue
            if cells[0].get("class") == ["wday"]:
                current_day = cells[0].get_text(strip=True)
                continue

            if current_day is None:
                continue

            subject = {}
            week_numbers = []

            for idx, cell in enumerate(cells):
                text = cell.get_text(strip=True)

                if idx == 0:
                    subject["time"] = text
                    times = text.split("-")
                    if len(times) == 2:
                        subject["startTime"], subject["endTime"] = times
                    else:
                        subject["startTime"] = subject["endTime"] = ""
                elif idx == 1:
                    subject["group"] = text
                elif idx == 2:
                    subject["subgroup"] = text
                elif idx == 3:
                    weeks_match = re.search(r"\(([\d,\-\s]+)\)", text)
                    if weeks_match:
                        parts = [
                            p.strip() for p in weeks_match.group(1).split(",")
                        ]
                        for part in parts:
                            if "-" in part:
                                start_week, end_week = map(
                                    int, part.split("-")
                                )
                                week_numbers.extend(
                                    range(start_week, end_week + 1)
                                )
                            else:
                                try:
                                    week_numbers.append(int(part))
                                except ValueError:
                                    continue

                    em_tag = cell.find("em")
                    distype_tag = cell.find(class_="distype")
                    subject["name"] = (
                        em_tag.get_text(strip=True) if em_tag else ""
                    )
                    subject["type"] = (
                        distype_tag.get_text(strip=True) if distype_tag else ""
                    )
                elif idx == 4:
                    subject["classroom"] = text

            for week_num in week_numbers:
                result.setdefault(week_num, {}).setdefault(
                    current_day, []
                ).append(subject.copy())

        return result

    @staticmethod
    def convert_origin_to_plain(
        origin: Dict[int, Dict[str, List[dict]]]
    ) -> List[dict]:
        flat_list = []
        for week_num, days in origin.items():
            for day_name, lessons in days.items():
                for lesson in lessons:
                    lesson_copy = {
                        **lesson,
                        "weekNum": week_num,
                        "dayName": day_name,
                    }
                    flat_list.append(lesson_copy)
        return flat_list

    @staticmethod
    def create_google_calendar_csv_from_plain_origin(
        plain: List[dict],
        teacher_name: str,
        first_week_date: datetime,
        existing_csv: Optional[str] = None,
    ) -> Tuple[str, str]:
        """
        Создает CSV для импорта в Google Calendar из плоского расписания.
        """
        header = (
            '"Subject","Start Date","Start Time","End Date","End Time",'
            '"All Day Event","Description","Location","Private"\n'
        )
        all_csv = existing_csv if existing_csv is not None else header
        result_csv = header
        activity_counter = {}

        short_teacher_name = "".join(
            word[0].upper() for word in teacher_name.split() if word
        )

        for lesson in plain:
            week_num = int(lesson["weekNum"])
            day_name = lesson["dayName"]

            weekday_index = WEEK_DAYS.get(day_name)
            if weekday_index is None:
                continue

            day_offset = (
                weekday_index - first_week_date.weekday()
            ) + (week_num - 1) * 7

            lesson_date = first_week_date + timedelta(days=day_offset)
            date_str = lesson_date.strftime('%m/%d/%Y')

            short_subject = ''.join(
                word[0].upper()
                for word in lesson["name"].replace("-", " ").split()
                if word
            )

            key = "{}-{}-{}-{}-{}".format(
                teacher_name,
                short_subject,
                lesson["group"],
                lesson["subgroup"],
                lesson["type"][:3],
            )

            activity_counter[key] = activity_counter.get(key, 0) + 1
            activity_number = activity_counter[key]

            subject_field = (
                '"{}; БГЭУ: {}; ({}); {}{}; ({}-{}); неделя: {}"'.format(
                    short_teacher_name,
                    lesson["classroom"],
                    short_subject,
                    lesson["group"],
                    lesson["subgroup"],
                    lesson["type"][:3],
                    activity_number,
                    week_num,
                )
            )

            description_field = (
                '{}; БГЭУ: {}; ({}); {}{}; ({}); неделя: {}'.format(
                    teacher_name,
                    lesson["classroom"],
                    lesson["name"],
                    lesson["group"],
                    lesson["subgroup"],
                    lesson["type"],
                    week_num,
                )
            )

            line = (
                '{},'
                '"{}","{}","{}","{}",'
                '"False","{}","БГЭУ: {}","True"\n'.format(
                    subject_field,
                    date_str,
                    lesson["startTime"],
                    date_str,
                    lesson["endTime"],
                    description_field,
                    lesson["classroom"],
                )
            )

            result_csv += line
            all_csv += line

        return all_csv
