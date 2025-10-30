import logging
from typing import List, Dict, Optional, Union
from urllib.parse import urlencode
import httpx

logger = logging.getLogger(__name__)


class TeachersService:
    """
    Сервис для получения списка преподавателей и расписания с сайта БГЭУ.
    """

    BASE_URL = "http://bseu.by/schedule/"

    def __init__(self) -> None:
        self.client = httpx.AsyncClient(verify=False)

    async def __aenter__(self) -> "TeachersService":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    @staticmethod
    def _default_headers() -> Dict[str, str]:
        return {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Referer": TeachersService.BASE_URL,
            "Origin": "http://bseu.by",
        }

    async def _request(
        self,
        data: Dict[str, Union[str, int]],
        *,
        expect_json: bool = True,
    ) -> Optional[Union[Dict, List, str]]:
        """
        Метод для POST-запросов к API сайта.

        :param data: Данные формы для отправки
        :param expect_json: Ожидать ли JSON-ответ (иначе возвращается текст)
        :return: JSON-объект, список, строка с HTML или None при ошибке
        """
        try:
            encoded_content = urlencode(data, encoding="windows-1251")
            response = await self.client.post(
                self.BASE_URL,
                headers=self._default_headers(),
                content=encoded_content,
            )
            response.encoding = "windows-1251"
            response.raise_for_status()

            if expect_json:
                return response.json()
            else:
                return response.text

        except httpx.RequestError as e:
            logger.error(f"Ошибка запроса к {self.BASE_URL}: {e}")
        except ValueError as e:
            logger.error(f"Ошибка парсинга JSON: {e}")
        except Exception as e:
            logger.error(f"Неизвестная ошибка: {e}")
        return None

    @staticmethod
    def get_teacher_schedule_action(tid: int, taid: int, sid: int) -> str:
        return (
            f"tid.{len(str(tid))}.{tid}"
            f"taid.{len(str(taid))}.{taid}"
            f"sid.{len(str(sid))}.{sid}"
            "__id.22.main.TSchedA.GetTSched__sp.8.tresults__fp.4.main"
        )

    async def get_teachers_list_by_request(
        self, teacher_name: str
    ) -> List[Dict]:

        body = {
            "__act": "__id.24.main.TSchedA.getTeachers",
            "tname": teacher_name
        }

        result = await self._request(body, expect_json=True)
        return result if isinstance(result, list) else []

    async def get_schedule_page_by_request(
        self, teacher_name: str, action: Optional[str] = None
    ) -> str:
        if action is None:
            action = self.get_teacher_schedule_action(0, 0, 0)

        data = {
            "faculty": "-1",
            "form": "-1",
            "course": "-1",
            "group": "-1",
            "tname": teacher_name,
            "period": "3",
            "__act": action,
        }

        result = await self._request(data, expect_json=False)
        return result or ""

    async def close(self) -> None:
        await self.client.aclose()
