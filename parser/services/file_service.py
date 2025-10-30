import os
import aiofiles


async def save_schedule(
    data: str, path: str = "data/schedule.csv"
) -> None:
    async with aiofiles.open(
        file=path,
        mode="w",
        encoding="utf-8"
    ) as f:
        await f.write(data)


async def read_schedule(
    path: str = "data/schedule.csv"
) -> str:
    if not os.path.isfile(path):
        return ""
    async with aiofiles.open(
        file=path,
        mode="r",
        encoding="utf-8"
    ) as f:
        content = await f.read()
        return content if content else ""
