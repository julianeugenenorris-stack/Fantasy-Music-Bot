from datetime import datetime, timedelta
import asyncio

from cogs.draft import Draft
from cogs.scraper import *

season_week_length: int = 52
season_month_length: int = 4


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

        draft.draft_update_time = [day, hour, minute]
        print("starting season")
        draft.next_stage()

        await interaction.followup.send("Starting first weekly update. Don't send commands till it is finished...")
        await update_draft(draft, interaction)
        await update_score(draft, interaction)
        await save_changes(draft, interaction)
        await interaction.followup.send("League update is completed! Starting season...")

        for p in draft.draft_players:
            save_object(p, f"player{p.user_id}.txt")

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
                f"Warning: Next run ({run_next_time}) is in the past. Correcting...")
            run_next_time = run_next_time + timedelta(weeks=1)
            sleep = (run_next_time - now).total_seconds()

        await interaction.followup.send(f"Weekly update scheduled at {run_next_time}. Update is in {((sleep / 3600) / 24):.1f} days." if (sleep / 3600) > 24 else f"Weekly update scheduled at {run_next_time}. Update is in {(sleep / 3600):.2f} hours.")
        print(
            f"Weekly update scheduled at {run_next_time}. Sleeping for {sleep} seconds.")
        await asyncio.sleep(sleep)

        await interaction.followup.send("Starting weekly league update. Please don't use any commands during the update...")
        await update_draft(draft, interaction)
        await update_score(draft, interaction)
        await save_changes(draft, interaction)
        await interaction.followup.send("League update is completed!")

        if draft.week_in_season >= season_week_length:
            # Season is over
            await interaction.followup.send("Season has ended. Finalizing results.")
            draft.next_stage()
            draft.end_season()
            break


async def update_draft(draft: Draft, interaction):
    try:
        if draft is None:
            await interaction.followup.send("No draft loaded, skipping update.")
            return

        # Update league (draft) info

        await interaction.followup.send("Downloading artists and listeners...")
        website_arrays = get_full_artists_data()

        draft.all_artists = website_arrays[0]

        draft.next_week()

        draft.update_weekly_listeners(website_arrays[1])
        draft.update_total_listeners()

        await interaction.followup.send("Weekly league information loaded...")
    except Exception as e:
        await interaction.followup.send(f"Error during weekly update: {e}")


async def update_score(draft: Draft, interaction):
    try:
        if draft is None:
            await interaction.followup.send("No draft loaded, skipping scoring update.")
            return

        await interaction.followup.send("Scoring Billboard Hot 100...")
        draft.score_billboard()
        await interaction.followup.send("Scoring Billboard Hot 100 completed!")

        await interaction.followup.send("Scoring Last Aoty Albums...")
        draft.score_aoty()
        await interaction.followup.send("Scoring Last Aoty Albums completed!")

        await interaction.followup.send("Scoring Change In listeners...")
        draft.score_change()
        await interaction.followup.send("Scoring Change In Listeners completed!")

        await interaction.followup.send("Scoring Change In listeners...")
        draft.score_listeners()
        await interaction.followup.send("Scoring Change In Listeners completed!")

        await interaction.followup.send("Scoring Full Week...")
        draft.score_total()
        await interaction.followup.send("Scoring Full Week completed!")

        await interaction.followup.send("Weekly scores updated...")
    except Exception as e:
        await interaction.followup.send(f"Error during weekly score update: {e}")


async def save_changes(draft: Draft, interaction):
    try:
        if draft is None:
            await interaction.followup.send("No draft loaded, skipping saving update.")
            return

        await interaction.followup.send("Saving changes ...")
        draftName = f"draft{draft.draft_name}"

        save_object(draft, draftName)

        for p in draft.draft_players:
            save_object(p, f"player{p.user_id}.txt")

            await interaction.followup.send("Changes saved!")
    except Exception as e:
        await interaction.followup.send(f"Error during saving: {e}")
