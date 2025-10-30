from datetime import datetime
import logging
import traceback
from typing import Optional

from .services.file_service import save_schedule
from .services.teachers_service import TeachersService
from .services.parsers_service import ParsersService

logger = logging.getLogger("parser")
logging.basicConfig(level=logging.INFO)


async def parse(teachers: list[str], first_week_date: Optional[datetime] = None):

    logger.info("Сбор данных запущен")

    teachers_service = TeachersService()
    parsers_service = ParsersService()

    all_csv = None
    for raw_name in teachers:
        found_teachers = await teachers_service.get_teachers_list_by_request(
            raw_name
        )
        if not found_teachers:
            logger.warning(
                "Преподаватель {} не найден!".format(
                    raw_name
                )
            )
            continue

        teacher = found_teachers[0]
        schedule_action = teachers_service.get_teacher_schedule_action(
            teacher.get("tid"),
            teacher.get("taid"),
            teacher.get("sid")
        )

        try:
            html = await teachers_service.get_schedule_page_by_request(
                teacher.get("tname"),
                schedule_action
            )
        except Exception:
            logger.error(
                "Ошибка во время сбора данных. "
                "Преподаватель: {}. Детали: {}".format(
                    teacher.get("tname"), traceback.format_exc()
                )
            )
            continue

        origin = parsers_service.parse_semester_schedule_page(html)
        plain = parsers_service.convert_origin_to_plain(origin)

        if first_week_date:
            all_csv = parsers_service.create_google_calendar_csv_from_plain_origin(
                plain,
                teacher.get("tname"),
                first_week_date,
                all_csv
            )

        if not origin:
            logger.warning("Преподаватель {} - пустое расписание".format(
                teacher.get("tname")
            ))
            continue

        logger.debug("Расписание для преподавателя {} собрано!".format(
            teacher.get("tname")
        ))

    # Сохраняем расписание (если None - сохраняем пустую строку)
    await save_schedule(
        all_csv if all_csv else ""
    )

    logger.info("Расписание обновлено. Сбор завершен")
