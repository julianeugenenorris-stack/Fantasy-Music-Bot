from datetime import datetime, timedelta
import asyncio

from cogs.draft import Draft
from cogs.scraper import *


async def restart_end_of_season_timer(draft: Draft):
    return


def start_end_of_season_timer():
    current_datetime = datetime.now()

    one_year_later_approx = current_datetime + timedelta(days=364)


start_end_of_season_timer()
