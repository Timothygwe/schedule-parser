from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI

from parser.parser import parse
import config

scheduler = AsyncIOScheduler()
scheduler.add_job(
    parse, "interval", seconds=config.UPDATE_PERIOD,
    kwargs={
        "teachers": config.SAMPLE_PROFESSORS,
        "first_week_date": config.FIRST_WEEK_DATE
    }
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    yield
    scheduler.shutdown()
