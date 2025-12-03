from datetime import datetime, timedelta
import asyncio

from cogs.draft import Draft
from cogs.scraper import *


async def restart_end_of_season_timer(draft: Draft):
    return


def start_end_of_season_timer():
    current_datetime = datetime.now()

    one_year_later_exact = current_datetime.replace(
        year=current_datetime.year + 1)
    print(one_year_later_exact)


start_end_of_season_timer()
