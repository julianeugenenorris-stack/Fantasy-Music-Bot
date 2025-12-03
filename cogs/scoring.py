from datetime import datetime, timedelta
import asyncio

from cogs.draft import Draft
from cogs.scraper import *

season_week_length: int = 52


async def weekly_update(draft: Draft, interaction, day=None, hour=None, minute=None):
    if day is None or hour is None or minute is None:
        weekday, hour_timer, minute_timer = draft.get_update_time()
    else:
        # set the update time
        # 0 is moday, 6 is sunday
        weekday = day
        # 24 hour clock
        hour_timer = hour
        # 60 minute clock
        minute_timer = minute

        draft.set_draft_update_time([day, hour, minute])
        draft.next_stage()

    while True:
        now = datetime.now()
        days_until = (weekday - now.weekday()) % 7
        if days_until < 0 or (days_until == 0 and (now.hour, now.minute) >= (hour_timer, minute_timer)):
            days_until += 7
        run_next_time = datetime(
            year=now.year,
            month=now.month,
            day=now.day,
            hour=hour_timer,
            minute=minute_timer,
        ) + timedelta(days=days_until)

        sleep = (run_next_time - now).total_seconds()

        if sleep < 0:
            print(
                f"Warning: Next run ({next_run}) is in the past. Correcting...")
            next_run += timedelta(weeks=1)
            sleep = (next_run - now).total_seconds()

        await interaction.followup.send(f"Weekly update scheduled at {run_next_time}. Update is in {((sleep / 3600) / 24):.1f} days." if (sleep / 3600) > 24 else f"Weekly update scheduled at {run_next_time}. Update is in {(sleep / 3600):.2f} hours.")
        print(
            f"Weekly update scheduled at {run_next_time}. Sleeping for {sleep} seconds.")
        await asyncio.sleep(sleep)

        await update(draft, interaction)

        if draft.get_week_in_season() >= season_week_length:
            # Season is over → finalize
            await interaction.send("Season has ended. Finalizing results...")
            draft.next_stage()
            draft.end_season()
            break


async def update(draft: Draft, interaction):
    await interaction.response.send_message("Starting weekly artist score update...")

    try:
        if draft is None:
            await interaction.followup.send("No draft loaded, skipping update.")
            return

        await interaction.followup.send("Downloading latest artists and listeners...")
        download_pages()

        websiteArrays = parse_all_pages()
        draft.set_all_artists(websiteArrays[0])
        draft.set_current_listeners(websiteArrays[1])

        draft.week_in_season += 1

        draft.update_weekly_score(websiteArrays[1])
        draft.update_monthly_score()
        draft.update_total_score()

        draftName = f"draft{draft.get_name()}"
        save_object(draft, draftName)

        for p in draft.get_all_players():
            save_object(p, f"player{p.get_id()}.txt")

        await interaction.followup.send("Weekly update completed!")
    except Exception as e:
        await interaction.followup.send(f"Error during weekly update: {e}")
