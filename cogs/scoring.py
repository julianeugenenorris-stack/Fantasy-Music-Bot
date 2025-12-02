from datetime import datetime, timedelta
import asyncio

from cogs.scraper import *


async def weeklyUpdate(draft, day, hour, minute, interaction):
    # set the update time
    # 0 is moday, 6 is sunday
    weekdayTimer = day
    # 24 hour clock
    hourTimer = hour
    # 60 minute clock
    minuteTimer = minute

    while True:
        now = datetime.now()
        dayTarget = weekdayTimer - now.weekday()
        if dayTarget < 0 or (dayTarget == 0 and (now.hour, now.minute) >= (hourTimer, minuteTimer)):
            dayTarget += 7
        runNext = datetime(
            year=now.year,
            month=now.month,
            day=now.day,
            hour=hourTimer,
            minute=minuteTimer,
        ) + timedelta(days=dayTarget)

        sleep = (runNext - now).total_seconds()

        if sleep < 0:
            print(
                f"Warning: Next run ({next_run}) is in the past. Correcting...")
            # Skip to the next scheduled week
            next_run += timedelta(weeks=1)
            sleep = (next_run - now).total_seconds()

        await interaction.followup.send(f"Weekly update scheduled at {runNext}. Sleeping for {(sleep / 3600):.2f} hours.")
        # print(f"Weekly update scheduled at {runNext}. Sleeping for {sleep} seconds.")
        await asyncio.sleep(sleep)

        # --- RUN YOUR UPDATE CODE ---
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

            draftName = f"draft{draft.get_name()}"
            save_object(draft, draftName)

            draft.update_weekly_score(websiteArrays[1])
            draft.update_monthly_score()
            draft.update_total_score()

            for p in draft.get_all_players():
                save_object(p, f"player{p.get_id()}.txt")

            await interaction.followup.send("Weekly update completed!")
        except Exception as e:
            await interaction.followup.send(f"Error during weekly update: {e}")
