from typing import Literal
from dotenv import load_dotenv, dotenv_values

from cogs.scraper import *
from cogs.embedtemplates import *
from cogs.scoring import *
from cogs.draft import Draft
from cogs.client import start_client

import random
import discord
from discord.ext import commands


load_dotenv()
config = dotenv_values()
GUILD_ID = discord.Object(id=config.get("GUILD_ID"))
DISCORD_TOKEN = config.get("DISCORD_TOKEN")
OWNER_ID = config.get("OWNER_ID")

client = start_client(GUILD_ID, OWNER_ID)
draft: Draft = None


draft_command_cooldown: int = 1
team_command_cooldown: int = 60


@client.event
async def on_guild_join(guild):
    print(f"joined: {guild}")


@client.tree.command(name="createdraft", description="Start Music Draft", guild=GUILD_ID)
async def create_draft(interaction: discord.Interaction, draftname: str, rounds: int):
    global draft

    if int(rounds) > 100:
        await interaction.response.send_message("Please enter a number below 100.", delete_after=10, ephemeral=True)
        return

    if draft is None:
        draft = Draft(name=draftname, rounds=int(rounds))
        await interaction.response.send_message(f"Draft {draftname} is now open.")
        return

    if draft is not None:
        await interaction.response.send_message(f"Draft {draft.draft_name} is already open.")
        return

    await interaction.response.send_message(f"Draft {draft.draft_name} was already created in the guild.\nOnly one draft per guild id.", delete_after=10, ephemeral=True)


@client.tree.command(name="startdraft", description="Start Music Draft", guild=GUILD_ID)
async def start_draft(interaction: discord.Interaction):
    global draft

    if draft is None:
        await interaction.response.send_message("No draft class is open.\n/createdraft to make one", delete_after=10, ephemeral=True)
        return

    try:
        if draft.is_stage(stage=[2, 3, 4]):
            await interaction.response.send_message("Draft is already over.", delete_after=10, ephemeral=True)
            return
        if draft.is_stage(stage=1):
            await interaction.response.send_message("already started draft", delete_after=10, ephemeral=True)
            return
    except:
        await interaction.response.send_message("No draft class is open.\n/createdraft to make one", delete_after=10, ephemeral=True)
        return

    if draft.get_size() < 1:
        await interaction.response.send_message("Not enough players in draft", delete_after=10, ephemeral=True)
        return

    await interaction.response.send_message("Starting draft...")

    await interaction.followup.send("Downloading artists and listeners...")
    website_arrays = get_full_artists_data()

    draft.next_stage()
    draft.all_artists = website_arrays[0]
    draft.starting_listeners = website_arrays[1]
    draft.current_listeners = website_arrays[1]

    draft_name = f"draft{draft.draft_name}"
    save_object(draft, draft_name)

    for p in draft.get_all_players():
        save_object(p, f"player{p.user_id}.txt")

    await interaction.followup.send("Draft ready! Starting Draft Lobby.")

    # start draft
    random.shuffle(draft.draft_players)
    draft.start_matchups()
    firstPlayer = draft.get_all_players()[0]
    user = await client.fetch_user(firstPlayer.user_id)
    await interaction.followup.send(f"{user.mention} You are on the board.\nUse /draft to select a player using their name exactly as written on spotify.\n(must have more than half a million monthly listeners.)")


@client.tree.command(name="settings", description="Show settings of the draft.", guild=GUILD_ID)
@commands.cooldown(1, team_command_cooldown, commands.BucketType.user)
async def settings(interaction: discord.Interaction,
                   action: Literal["get", "set"] = "get",
                   rounds: int | None = None,
                   monthly: float | None = None,
                   change: float | None = None,
                   aoty_range: Literal["90+", "89-85", "84-82",
                                       "81-79", "78-75", "74-65", "64-"] | None = None,
                   aoty_score: float | None = None,
                   billboard_score: float | None = None,
                   billboard_spot: int | None = None, ):
    global draft

    if draft is None:
        await interaction.response.send_message(f"Load or start a draft to start a season.")
        return

    if action == "get":
        settings = draft.get_settings()
        formatted_string = ", ".join(
            [f"{key}: {value}" for key, value in settings.items()])
        await interaction.response.send_message(formatted_string)
        return
    if action == "set":
        draft.new_settings(rounds=rounds, monthly=monthly, change=change, aoty_score=aoty_score, aoty_range=aoty_range,
                           billboard_score=billboard_score, billboard_spot=billboard_spot+1)
        settings = draft.get_settings()
        formatted_string = ", ".join(
            [f"{key}: {value}" for key, value in settings.items()])
        await interaction.response.send_message(F"New settings are:\n{formatted_string}")
        return


@settings.error
async def mycommand_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"This command is on cooldown! Try again in {error.retry_after:.2f} seconds.")
    else:
        raise error


@client.tree.command(name="join", description="Join fantasy draft as a player.", guild=GUILD_ID)
@commands.cooldown(1, draft_command_cooldown, commands.BucketType.user)
async def join(interaction: discord.Interaction, team_name: str):
    global draft

    if draft is None:
        await interaction.response.send_message(f"Load or start a draft to join.")
        return

    if draft.is_stage(stage=[1, 2, 3]):
        await interaction.response.send_message("Draft already started", delete_after=10, ephemeral=True)
        return

    user = interaction.user
    if draft is not None:
        for p in draft.get_all_players():
            if p.user_id == user.id:
                await interaction.response.send_message("You're already in the draft!", delete_after=10, ephemeral=True)
                return

    draft.add_new_player(user, user.id, user.name, team_name)

    player = None
    for p in draft.get_all_players():
        if p.user_id == user.id:
            player = p
            break

    draft_name = f"draft{draft.draft_name}"
    save_object(draft, draft_name)

    await interaction.response.send_message(f"{interaction.user.name} as joined the draft with team **{player.team_name}**.")


@join.error
async def mycommand_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"This command is on cooldown! Try again in {error.retry_after:.2f} seconds.")
    else:
        raise error


@client.tree.command(name="startseason", description="This will begin the fantasy season, set the update schedual (0=monday, 6=sunday) (24 hour format).", guild=GUILD_ID)
async def start_season(interaction: discord.Interaction, day: int, hour: int, minute: int):
    if draft is None:
        await interaction.response.send_message(f"Load or start a draft to start a season.")
        return

    if draft.is_stage([3, 4]):
        await interaction.response.send_message(f"{draft.draft_name}'s fantasy season is already started.")
        return

    if draft.is_stage([0, 1]):
        await interaction.response.send_message(f"{draft.draft_name}'s has not drafted.")
        return

    await interaction.response.send_message(f"Starting {draft.draft_name}'s fantasy season.")

    draft.update_starting_player_listeners()

    # start season
    client.loop.create_task(weekly_update(
        draft, interaction, day=day, hour=hour, minute=minute))


@client.tree.command(name="draft", description="Draft artists to fantasy team.", guild=GUILD_ID)
@commands.cooldown(1, draft_command_cooldown, commands.BucketType.user)
async def draft_artist(interaction: discord.Interaction, artist_name: str):
    artist_selected = artist_name
    try:
        if draft.is_stage(0):
            await interaction.response.send_message("Need to start draft before drafting players", delete_after=10, ephemeral=True)
            return
        elif draft.is_stage([2, 3, 4]):
            await interaction.response.send_message("Draft is already finished", delete_after=10, ephemeral=True)
            return
    except:
        await interaction.response.send_message("Need to create or import a draft room.", delete_after=10, ephemeral=True)
        return

    user = interaction.user

    if draft.is_stage(stage=[2, 3]):
        await interaction.response.send_message(
            "Draft is already over.", delete_after=10, ephemeral=True)
        return

    if draft.get_all_players()[draft.turn].user_id == user.id:
        for artist in draft.all_artists:
            if artist_selected == artist:
                player = draft.get_all_players()[draft.turn]

                if artist_selected in draft.drafted_artists:
                    await interaction.response.send_message(f"{artist_selected} has already been drafted. Draft another artist.", delete_after=10, ephemeral=True)
                    return

                await interaction.response.send_message(f"{user.name} has drafted {artist_selected}!")
                player.draft_artist(artist_selected)
                draft.drafted_artists.add(artist_selected)

                draft.next_turn()

                if draft.is_stage(1):
                    nextPlayer = draft.get_all_players()[draft.turn]
                    user = await client.fetch_user(nextPlayer.user_id)

                    draft_name = f"draft{draft.draft_name}"
                    save_object(draft, draft_name)

                    await interaction.followup.send(f"{user.mention} You are on the board.\nUse /draft to select a player using their name exactly as written on spotify.\n(must have more than half a million monthly listeners.)")
                    return
                else:
                    draft_name = f"draft{draft.draft_name}"
                    save_object(draft, draft_name)

                    await interaction.followup.send("Draft Completed.")
                    return
        await interaction.response.send_message(f"The artist {artist_selected} is not in the draft pool.", delete_after=10, ephemeral=True)
        return
    else:
        await interaction.response.send_message("It is not your turn.", delete_after=10, ephemeral=True)
        return


@draft_artist.error
async def mycommand_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"This command is on cooldown! Try again in {error.retry_after:.2f} seconds.")
    else:
        raise error


@client.tree.command(name="reloaddraft", description="Join fantasy draft as a player.", guild=GUILD_ID)
async def reload_draft(interaction: discord.Interaction, name: str):
    global draft

    if draft is None:
        try:
            draft = load_object(f"draft{name}")
            await interaction.response.send_message(f"{name} has been reloaded.")
            if draft.is_stage(3):
                await interaction.followup.send(f"Restarting {draft.draft_name}'s fantasy season.")
                client.loop.create_task(weekly_update(
                    draft, interaction))
                return
            if draft.is_stage(2):
                await interaction.followup.send(f"Start the fantasy season with /startseason.")
                return
            if draft.is_stage(1):
                nextPlayer = draft.get_all_players()[draft.turn]
                user = await client.fetch_user(nextPlayer.user_id)
                await interaction.followup.send(f"{user.mention} You Are On The Board.\nUse /draft to select a player using their name exactly as written on spotify.\n(must have more than half a million monthly listeners.)")
            return
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", delete_after=10, ephemeral=True)
            return
    try:
        await interaction.response.send_message(f"{draft.draft_name} has already been created.", delete_after=10, ephemeral=True)
        return
    except FileNotFoundError:
        await interaction.response.send_message(f"{name} is not found.", delete_after=10, ephemeral=True)
        return


@client.tree.command(name="team", description="Show a players team.", guild=GUILD_ID)
@commands.cooldown(1, team_command_cooldown, commands.BucketType.user)
async def show_team(interaction: discord.Interaction):
    global draft
    if draft is None:
        await interaction.response.send_message(f"Load or start a draft to start a season.")
        return

    if draft.is_stage(0):
        await interaction.response.send_message("Need to start draft before checking team.", delete_after=10, ephemeral=True)
        return

    user = interaction.user

    player = None
    for p in draft.get_all_players():
        if p.user_id == user.id:
            player = p
            break

    if player is None:
        await interaction.response.send_message("You are not in this draft.", delete_after=10, ephemeral=True)
        return

    embed = team_template(player, draft)

    if type(embed) is str:
        await interaction.response.send_message(embed, delete_after=10, ephemeral=True)
        return

    await interaction.response.send_message(embed=embed)


@show_team.error
async def show_teamte(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"This command is on cooldown! Try again in {error.retry_after:.2f} seconds.")
    else:
        raise error


@client.tree.command(name="billboard", description="Show a players team.", guild=GUILD_ID)
@commands.cooldown(1, team_command_cooldown, commands.BucketType.user)
async def show_billboard(interaction: discord.Interaction):
    global draft
    if draft is None:
        await interaction.response.send_message(f"Load or start a draft use.")
        return

    if draft.is_stage([0, 1]):
        await interaction.response.send_message("Need to start draft before checking billboard", delete_after=10, ephemeral=True)
        return

    await interaction.response.defer()

    embeds = billboard_template(draft)
    view = TemplateView(embeds)

    await interaction.followup.send(embed=embeds[0], view=view)


@draft_artist.error
async def show_billboard(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"This command is on cooldown! Try again in {error.retry_after:.2f} seconds.")
    else:
        raise error


@client.tree.command(name="artistinfo", description="Show a players team.", guild=GUILD_ID)
@commands.cooldown(1, team_command_cooldown, commands.BucketType.user)
async def show_artist(interaction: discord.Interaction, artist_name: str, show: bool | None = True):
    global draft
    if draft is None:
        await interaction.response.send_message(f"Load or start a draft use.")
        return

    if artist_name in draft.all_artists:
        await interaction.response.defer(thinking=True)
        embed = artists_info_template(artist_name, draft)
    else:
        await interaction.response.send_message(content="This artist is not in the artist pool or has less than 500,000 monthly listeners", delete_after=10, ephemeral=True)
        return

    if show is False:
        if embed is None:
            await interaction.followup.send(content="No information available for this artist.", ephemeral=True)
        else:
            await interaction.followup.send(embed=embed, ephemeral=True)
        return

    if embed is None:
        await interaction.followup.send(content="No information available for this artist.")
    else:
        await interaction.followup.send(embed=embed)


@draft_artist.error
async def mycommand_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"This command is on cooldown! Try again in {error.retry_after:.2f} seconds.")
    else:
        raise error


@client.tree.command(name="albums", description="Show all albums for each artist on team.", guild=GUILD_ID)
@commands.cooldown(1, team_command_cooldown, commands.BucketType.user)
async def show_album(interaction: discord.Interaction, time: Literal["mine", "league"], show: bool | None):
    if draft is None:
        await interaction.response.send_message(f"Load or start a draft to start a season.")
        return

    if draft.is_stage([0, 1, 2]):
        await interaction.response.send_message("Need to finish draft before checking albums", delete_after=10, ephemeral=True)
        return

    user = interaction.user

    player = None
    for p in draft.get_all_players():
        if p.user_id == user.id:
            player = p
            break

    if player is None:
        await interaction.response.send_message("You are not in this draft.", delete_after=10, ephemeral=True)
        return

    if time == "mine":
        embed = artists_albums_template(player)
    elif time == "league":
        embed = new_league_albums_template(draft)

    if show is False:
        await interaction.response.send_message(embed, ephemeral=True)
        return

    await interaction.response.send_message(embed=embed)


@show_team.error
async def mycommand_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"This command is on cooldown! Try again in {error.retry_after:.2f} seconds.")
    else:
        raise error


@client.tree.command(name="listeners", description="Show a teams listeners for a certain time or time frame.", guild=GUILD_ID)
@commands.cooldown(1, team_command_cooldown, commands.BucketType.user)
async def show_listeners(interaction: discord.Interaction, time: Literal["week", "matchup", "total"], week: int | None, show: bool | None):
    if draft is None:
        await interaction.response.send_message(f"Load or start a draft to start a season.")
        return

    if draft.is_stage([0, 1, 2]):
        await interaction.response.send_message("Need to finish draft before checking scores", delete_after=10, ephemeral=True)
        return

    user = interaction.user

    player = None
    for p in draft.get_all_players():
        if p.user_id == user.id:
            player = p
            break

    if player is None:
        await interaction.response.send_message("You are not in this draft.", delete_after=10, ephemeral=True)
        return

    if week is not None:
        if week <= draft.week_in_season + 1:
            embed = certain_week_template(user, player, draft, week - 1)
        else:
            await interaction.response.send_message("Can't look at weeks in the future.", delete_after=10, ephemeral=True)
            return
    else:
        listeners_template(player, draft, type)

    if show is False:
        await interaction.response.send_message(embed, ephemeral=True)
        return

    await interaction.response.send_message(embed=embed)


@show_team.error
async def mycommand_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"This command is on cooldown! Try again in {error.retry_after:.2f} seconds.")
    else:
        raise error


@client.tree.command(name="scores", description="Show a teams scores for a certain time frame.", guild=GUILD_ID)
@commands.cooldown(1, team_command_cooldown, commands.BucketType.user)
async def show_scores(interaction: discord.Interaction, time: Literal["week", "matchup", "total"], type: None | Literal["billboard", "change", "aoty", "listeners", "all"], show: bool | None):
    if draft is None:
        await interaction.response.send_message(f"Load or start a draft to start a season.")
        return

    if draft.is_stage([0, 1, 2]):
        await interaction.response.send_message("Need to finish draft and start season before checking scores", delete_after=10, ephemeral=True)
        return

    user = interaction.user

    player = None
    for p in draft.get_all_players():
        if p.user_id == user.id:
            player = p
            break

    if player is None:
        await interaction.response.send_message("You are not in this draft.", delete_after=10, ephemeral=True)
        return

    if type is None:
        type = "all"

    if time == "week":
        embed = weekly_scores_template(player, type)
    if time == "matchup":
        embed = matchup_scores_template(player, type)
    if time == "total":
        embed = total_scores_template(player, type)

    if show is False:
        await interaction.response.send_message(embed, ephemeral=True)
        return

    await interaction.response.send_message(embed=embed)


@show_team.error
async def mycommand_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"This command is on cooldown! Try again in {error.retry_after:.2f} seconds.")
    else:
        raise error


@client.tree.command(name="overview", description="Shows overview of all players in league and their scoring totals.", guild=GUILD_ID)
@commands.cooldown(1, team_command_cooldown, commands.BucketType.user)
async def show_overview(interaction: discord.Interaction, time: Literal["week", "matchup", "total"], type: Literal["billboard", "change", "aoty", "listeners", "all"], show: bool | None):
    if draft is None:
        await interaction.response.send_message(f"Load or start a draft to start a season.")
        return

    if draft.is_stage([0, 1, 2]):
        await interaction.response.send_message("Need to finish draft before checking scores", delete_after=10, ephemeral=True)
        return

    await interaction.response.defer()

    embeds = overview_template(draft, type, time)
    view = TemplateView(embeds)

    if show is False:
        await interaction.followup.send(embeds=embeds, view=view, ephemeral=True)
        return
    else:
        await interaction.followup.send(embeds=embeds, view=view)
        return


@show_team.error
async def show_overview(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"This command is on cooldown! Try again in {error.retry_after:.2f} seconds.")
    else:
        raise error


@client.tree.command(name="matchup", description="Shows matchup of all players in league and their scoring totals.", guild=GUILD_ID)
@commands.cooldown(1, team_command_cooldown, commands.BucketType.user)
async def show_matchup(interaction: discord.Interaction, people: Literal["mine", " all"], type: Literal["billboard", "change", "aoty", "listeners", "all"], show: bool | None):
    if draft is None:
        await interaction.response.send_message(f"Load or start a draft to start a season.")
        return

    if draft.is_stage([0, 1, 2]):
        await interaction.response.send_message("Need to finish draft before checking scores", delete_after=10, ephemeral=True)
        return

    user = interaction.user
    await interaction.response.defer()

    player = None
    for p in draft.get_all_players():
        if p.user_id == user.id:
            player = p
            break

    if people == "mine":
        embed = build_player_matchup(draft, player, type)
        if show is False:
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            return
        else:
            await interaction.followup.send(embed=embed, view=view)
            return
    elif people == "all":
        if "BYE" in draft.matchups[draft.matchup_count][0]:
            embeds = matchup_template(
                draft, draft.matchups[draft.matchup_count][1], type)
        else:
            embeds = matchup_template(
                draft, draft.matchups[draft.matchup_count][0], type)
        view = TemplateView(embeds)

        if show is False:
            await interaction.followup.send(embeds=embeds, view=view, ephemeral=True)
            return
        else:
            await interaction.followup.send(embeds=embeds, view=view)
            return


@show_team.error
async def show_matchup(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"This command is on cooldown! Try again in {error.retry_after:.2f} seconds.")
    else:
        raise error


@client.tree.command(name="trade", description="Send a trade offer to player.", guild=GUILD_ID)
async def trade(interaction: discord.Interaction):
    if draft is None:
        await interaction.response.send_message(f"Load or start a draft to start a season.")
        return

    if draft.is_stage([0, 1]):
        await interaction.response.send_message("Need to start draft before checking scores", delete_after=10, ephemeral=True)
        return

    user = interaction.user


@show_team.error
async def trade(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"This command is on cooldown! Try again in {error.retry_after:.2f} seconds.")
    else:
        raise error

"""
TESTING COMMANDS

TODO REMOVE THESE AFTER FINISHING

"""


@client.tree.command(name="testupdate", description="Draft artists to fantasy team.", guild=GUILD_ID)
async def draftArtist(interaction: discord.Interaction, update: bool):

    await interaction.response.send_message("Starting weekly artist score update...")
    try:
        if draft is None:
            await interaction.followup.send("No draft loaded, skipping update.")
            return

        await interaction.followup.send("Starting weekly league update. Please don't use any commands during the update...")
        if update:
            await update_draft(draft, interaction)
        await update_score(draft, interaction)
        await save_changes(draft, interaction)
        await interaction.followup.send("League update is completed!")

    except Exception as e:
        await interaction.followup.send(f"Error during weekly update: {e}")


@client.tree.command(name="stage", description="Draft artists to fantasy team.", guild=GUILD_ID)
async def draft_artist(interaction: discord.Interaction):
    await interaction.response.send_message(f"Draft is at stage {draft.stage}.", delete_after=10, ephemeral=True)


@client.tree.command(name="testschedual", description="Draft artists to fantasy team.", guild=GUILD_ID)
async def draft_artist(interaction: discord.Interaction):
    print(f"Current Matchup {draft.week_matchups}")
    print(f"All Matchups {draft.matchups}")
    print(f"Matchup Week {draft.matchup_count}")
    print(f"Week in Matchup {draft.week_in_matchup}")
    await interaction.response.send_message(f"Done.", delete_after=10, ephemeral=True)


@client.tree.command(name="printplayerinfo", description="Draft artists to fantasy team.", guild=GUILD_ID)
async def draftArtist(interaction: discord.Interaction):
    player_info = None
    for player in draft.get_all_players():
        player_info = player.artist_info
    print(str(player_info))
    await interaction.response.send_message(f"Done.", delete_after=10, ephemeral=True)


@client.tree.command(name="printdraftinfo", description="Draft artists to fantasy team.", guild=GUILD_ID)
async def draftArtist(interaction: discord.Interaction):
    draft.start_matchups()
    print(str(draft.matchups))
    await interaction.response.send_message(f"Done.", delete_after=10, ephemeral=True)


@client.tree.command(name="removelastalbum", description="Draft artists to fantasy team.", guild=GUILD_ID)
async def draftArtist(interaction: discord.Interaction, artist: str):
    player_info = None
    for player in draft.get_all_players():
        player_info: list = player.artist_info[
            artist]["albums_on_record"]
        player_info.remove(player_info[0])
    await interaction.response.send_message(f"Done.", delete_after=10, ephemeral=True)


client.run(DISCORD_TOKEN)
