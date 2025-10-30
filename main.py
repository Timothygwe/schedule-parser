from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

import config
from parser.services.file_service import read_schedule
from parser.parser import parse
from scheduler import lifespan

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/schedule",
    description="Получение CSV данных расписания",
    responses={
        200: {
            "content": {"text/csv": {}},
            "description": "CSV данные расписания",
        }
    },
    response_class=Response
)

async def get_schedule():
    csv_content = await read_schedule()
    return Response(
        content=csv_content,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": 'attachment; filename="schedule.csv"'
        }
    )


@app.post(
    "/parse",
    description="Запуск парсера для обновления расписания"
)
async def trigger_parse():
    """Запускает парсер вручную для обновления расписания"""
    await parse(
        teachers=config.SAMPLE_PROFESSORS,
        first_week_date=config.FIRST_WEEK_DATE
    )
    return {"message": "Парсер запущен, расписание обновляется"}


if __name__ == "__main__":
    uvicorn.run(
        app, host=config.HOST, port=config.PORT
    )
