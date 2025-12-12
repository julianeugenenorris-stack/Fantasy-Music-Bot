from typing import Literal
from dotenv import load_dotenv, dotenv_values

from cogs.scraper import *
from cogs.embedtemplates import *
from cogs.scoring import *
from cogs.draft import Draft

import random
import discord
from discord.ext import commands
from discord import Message

load_dotenv()
config = dotenv_values()
GUILD_ID = discord.Object(id=config.get("GUILD_ID"))
DISCORD_TOKEN = config.get("DISCORD_TOKEN")
OWNER_ID = config.get("OWNER_ID")

draft: Draft = None


class Client(commands.Bot):
    async def on_ready(self):
        print(f"Logged on as {self.user}!")

        if GUILD_ID is None:
            print(f"Syncing without guild, no ID")
            await self.tree.sync()
            return

        try:
            await client.tree.sync()           # sync globally
            # remove all global commands
            client.tree.clear_commands(guild=None, type=None)
            # add commands locally
            synced = await self.tree.sync(guild=GUILD_ID)
            print(f"Synced {len(synced)} command to guild {GUILD_ID.id}")
            return

        except Exception as e:
            print(f'Error syncing command {e}')
            return

    async def on_message(self, message: Message):
        if message.author == self.user:
            return

        if not isinstance(message.channel, discord.DMChannel):
            return

        if not message.content.startswith("ACCEPT") and not message.content.startswith("DECLINE") and not message.content.startswith("CANCEL"):
            return

        if draft is None:
            await message.channel.send(f"Draft is not loaded.")
            return

        accepting_player: Player | None = None
        for p in draft.draft_players:
            if p.user_id == message.author.id:
                accepting_player = p
                break

        response: str = message.content
        split_response = response.split(" ")

        # check if they put a player
        if len(split_response) == 1:
            await message.channel.send(f"Put a players name after accept to accept their trade.")
            return

        sending_player: Player | None = None
        for p in draft.draft_players:
            if p.name == split_response[1]:
                sending_player = p
                break

        if sending_player is None:
            await message.channel.send(f"Player is not in draft.")
            return

        if accepting_player == sending_player:
            if message.content.startswith("CANCEL"):
                user = client.fetch_user(sending_player.user_id)
                draft.accept_trade(sending_player, accepting_player, user)
                draft.cancel_trade(sending_player, accepting_player, user)
                return
            await message.channel.send(f"You can't accept your own trade dumbass. Actually fuck you for trying and making me have to put this here.")
            return

        if message.content.startswith("ACCEPT"):
            if len(sending_player.trade_pieces) > 6:
                if sending_player.trade_pieces[6] == accepting_player.user_id:
                    user = client.fetch_user(sending_player.user_id)
                    draft.accept_trade(sending_player, accepting_player, user)
                    await message.channel.send(f"Trade accepted from {sending_player}.")
                    return
                else:
                    await message.channel.send(f"No trade from player exists.")
                    return
            else:
                await message.channel.send(f"No trade from player exists.")
                return

        if message.content.startswith("DECLINE"):
            if len(sending_player.trade_pieces) > 6:
                if sending_player.trade_pieces[6] == accepting_player.user_id:
                    user = client.fetch_user(sending_player.user_id)
                    draft.decline_trade(sending_player, accepting_player, user)
                    await message.channel.send(f"Trade declined from {sending_player}.")
                    return
                else:
                    await message.channel.send(f"No trade from player exists.")
                    return
            else:
                await message.channel.send(f"No trade from player exists.")
                return
        await message.channel.send(f"Some shit went wrong lmk bby girly I am really tired while writting this.")
        return


def start_client(guild_id: any = None, owner=None):
    global GUILD_ID

    GUILD_ID = guild_id

    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    intents.messages = True

    botDescription: str = "This bot runs a server wide draft. There can only be a single active draft per league. For help, type \"/help\"."

    client: Client = Client(
        command_prefix="!",
        intents=intents,
        owner_id=owner,
        description=str(botDescription),
    )

    return client


client = start_client(GUILD_ID, OWNER_ID)


draft_command_cooldown: int = 5
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

    for p in draft.draft_players:
        save_object(p, f"player{p.user_id}.txt")

    await interaction.followup.send("Draft ready! Starting Draft Lobby.")

    # start draft
    random.shuffle(draft.draft_players)
    draft.start_matchups()
    firstPlayer = draft.draft_players[0]
    user = await client.fetch_user(firstPlayer.user_id)
    await interaction.followup.send(f"{user.mention} You are on the board.\nUse /draft to select a player using their name exactly as written on spotify.\n(must have more than half a million monthly listeners.)")


@client.tree.command(name="settings", description="Show settings of the draft.", guild=GUILD_ID)
@commands.cooldown(1, team_command_cooldown, commands.BucketType.user)
async def settings(interaction: discord.Interaction,
                   action: Literal["get", "set"] = "get",
                   rounds: int | None = None,
                   listener: float | None = None,
                   change: float | None = None,
                   aoty_range: Literal["90+", "89-85",
                                       "84-82", "81-79", "78-75", "74-70", "69-65", "64-"] | None = None,
                   aoty_score: float | None = None,
                   billboard_score: float | None = None,
                   billboard_spot: int | None = None, ):
    global draft

    if draft is None:
        await interaction.response.send_message(f"Load or start a draft to start a season.")
        return

    if action == "get":
        embed = settings_template(draft)
        await interaction.response.send_message(embed=embed)
        return
    if action == "set":
        draft.new_settings(rounds=rounds, listener_mult=listener, change_mult=change, aoty_range=aoty_range,
                           aoty_score=aoty_score, billboard_score=billboard_score, billboard_spot=billboard_spot)
        embed = settings_template(draft)
        await interaction.response.send_message(embed=embed)
        return


@settings.error
async def settings_error(ctx, error):
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
        for p in draft.draft_players:
            if p.user_id == user.id:
                await interaction.response.send_message("You're already in the draft!", delete_after=10, ephemeral=True)
                return

    draft.add_new_player(user, user.id, user.name, team_name)

    player = None
    for p in draft.draft_players:
        if p.user_id == user.id:
            player = p
            break

    draft_name = f"draft{draft.draft_name}"
    save_object(draft, draft_name)

    await interaction.response.send_message(f"{interaction.user.name} as joined the draft with team **{player.team_name}**.")


@join.error
async def join_error(ctx, error):
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
    if draft is None:
        await interaction.response.send_message(f"Load or start a draft to start a season.")
        return
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

    if draft.draft_players[draft.turn].user_id == user.id:
        for artist in draft.all_artists:
            if artist_selected == artist:
                player = draft.draft_players[draft.turn]

                if artist_selected in draft.drafted_artists:
                    await interaction.response.send_message(f"{artist_selected} has already been drafted. Draft another artist.", delete_after=10, ephemeral=True)
                    return

                await interaction.response.send_message(f"{user.name} has drafted {artist_selected}!")
                player.draft_artist(artist_selected)
                draft.drafted_artists.add(artist_selected)

                draft.next_turn()

                if draft.is_stage(1):
                    nextPlayer = draft.draft_players[draft.turn]
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
async def draft_artist_error(ctx, error):
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
                nextPlayer = draft.draft_players[draft.turn]
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
    for p in draft.draft_players:
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
async def show_team_error(ctx, error):
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


@show_billboard.error
async def show_billboard_error(ctx, error):
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


@show_artist.error
async def show_artist_error(ctx, error):
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
    for p in draft.draft_players:
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


@show_album.error
async def show_album_error(ctx, error):
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
    for p in draft.draft_players:
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
        embed = listeners_template(player, draft, time)

    if show is False:
        await interaction.response.send_message(embed, ephemeral=True)
        return

    await interaction.response.send_message(embed=embed)


@show_listeners.error
async def show_listeners_error(ctx, error):
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
    for p in draft.draft_players:
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


@show_scores.error
async def show_scores_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"This command is on cooldown! Try again in {error.retry_after:.2f} seconds.")
    else:
        raise error


@client.tree.command(name="overview", description="Shows overview of all players in league and their scoring totals.", guild=GUILD_ID)
@commands.cooldown(1, team_command_cooldown, commands.BucketType.user)
async def show_overview(interaction: discord.Interaction, time: Literal["week", "matchup", "total"], type: Literal["billboard", "change", "aoty", "listeners", "all"]):
    if draft is None:
        await interaction.response.send_message(f"Load or start a draft to start a season.")
        return

    if draft.is_stage([0, 1, 2]):
        await interaction.response.send_message("Need to finish draft before checking scores", delete_after=10, ephemeral=True)
        return

    await interaction.response.defer()

    embeds = overview_template(draft, type, time)
    view = TemplateView(embeds)

    await interaction.followup.send(embeds=embeds, view=view)


@show_overview.error
async def show_overview_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"This command is on cooldown! Try again in {error.retry_after:.2f} seconds.")
    else:
        raise error


@client.tree.command(name="schedule", description="Shows matchup of all players in league and their scoring totals.", guild=GUILD_ID)
@commands.cooldown(1, team_command_cooldown, commands.BucketType.user)
async def show_schedule(interaction: discord.Interaction, time: Literal["week", "season"]):
    if draft is None:
        await interaction.response.send_message(f"Load or start a draft to start a season.")
        return

    if draft.is_stage([0, 1, 2]):
        await interaction.response.send_message("Need to finish draft before checking scores", delete_after=10, ephemeral=True)
        return

    await interaction.response.defer()

    if time == "week":
        embed = build_schedule_template(draft)
        await interaction.followup.send(embed=embed)
        return
    elif time == "season":
        matchups = draft.matchups
        length_matchups = len(matchups)
        current = matchups.index(draft.week_matchups)
        embeds = []
        matchup_counter = draft.matchup_count

        end = min(52, matchup_counter + 10)

        for week_index in range(draft.matchup_count, end):
            try:
                week_pairs = matchups[current]
                current += 1
            except:
                current = 0
                week_pairs = matchups[current]

            embed = build_schedule_season_template(week_pairs, week_index + 1)
            embeds.append(embed)

        if not embeds:
            await interaction.followup.send("No scheduled matchups found in the next 10 weeks.", ephemeral=True)
            return

        view = TemplateView(embeds)
        await interaction.followup.send(embed=embeds[0], view=view)
        return


@show_schedule.error
async def show_schedule_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"This command is on cooldown! Try again in {error.retry_after:.2f} seconds.")
    else:
        raise error


@client.tree.command(name="matchup", description="Shows matchup of all players in league and their scoring totals.", guild=GUILD_ID)
@commands.cooldown(1, team_command_cooldown, commands.BucketType.user)
async def show_matchup(interaction: discord.Interaction, people: Literal["mine", "all"], type: Literal["billboard", "change", "aoty", "listeners", "all"]):
    if draft is None:
        await interaction.response.send_message(f"Load or start a draft to start a season.")
        return

    if draft.is_stage([0, 1, 2]):
        await interaction.response.send_message("Need to finish draft before checking scores", delete_after=10, ephemeral=True)
        return

    await interaction.response.defer()

    if people == "mine":
        user = interaction.user
        player = None
        for p in draft.draft_players:
            if p.user_id == user.id:
                player = p
                break
        embed = build_player_matchup(
            player, draft.get_opponent(player, draft.matchup_count), type)
        await interaction.followup.send(embed=embed)
        return

    elif people == "all":
        embeds = []
        for p1, p2 in draft.week_matchups:
            embed = build_player_matchup(p1, p2, type)
            embeds.append(embed)
        view = TemplateView(embeds)
        await interaction.followup.send(embeds=embeds, view=view)
        return


@show_matchup.error
async def show_matchup_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"This command is on cooldown! Try again in {error.retry_after:.2f} seconds.")
    else:
        raise error


@client.tree.command(name="trade", description="Send a trade offer to player.", guild=GUILD_ID)
@commands.cooldown(1, team_command_cooldown, commands.BucketType.user)
async def trade(interaction: discord.Interaction, player_user_name: str, my_artist_1: str, my_artist_2: str | None, my_artist_3: str | None, their_artist_1: str, their_artist_2: str | None, their_artist_3: str | None):
    if draft is None:
        await interaction.response.send_message(f"Load or start a draft to start a season.")
        return

    if draft.is_stage([0, 1, 2]):
        await interaction.response.send_message("Need to start draft before checking scores", delete_after=10, ephemeral=True)
        return
    trade_partner: Player | None = None
    for p in draft.draft_players:
        if p.name == player_user_name:
            trade_partner = p
            break

    if trade_partner is None:
        await interaction.response.send_message("Player is not in the draft, use their perm name not nickname.", delete_after=10, ephemeral=True)
        return

    user = interaction.user

    player: Player | None = None
    for p in draft.draft_players:
        if p.user_id == user.id:
            player = p
            break

    if player is None:
        await interaction.response.send_message("You are not in the draft.", delete_after=10, ephemeral=True)
        return

    my_artists = [my_artist_1, my_artist_2, my_artist_3]
    their_artists = [their_artist_1, their_artist_2, their_artist_3]

    is_valid = await draft.validate_trade(
        interaction,
        player,
        trade_partner,
        my_artists,
        their_artists
    )

    if not is_valid:
        return

    if player.trades_sent == 1:
        await interaction.response.send_message(f"You have already sent a trade, get the player to decline it before sending another.", delete_after=10, ephemeral=True)
        return

    if trade_partner.trades_sent == 1:
        await interaction.response.send_message(f"Player already has a trade request, get the player to decline it before sending another.", delete_after=10, ephemeral=True)
        return

    trade_partner_user = await client.fetch_user(trade_partner.user_id)

    embed = build_trade_template(player, their_artist_1,
                                 their_artist_2, their_artist_3, my_artist_1, my_artist_2, my_artist_3)
    player.trade_pieces = [my_artist_1, my_artist_2, my_artist_3, their_artist_1,
                           their_artist_2, their_artist_3, trade_partner_user.id]
    await trade_partner_user.send(embed=embed)
    player.trades_sent = 1
    trade_partner.trades_sent = 1


@trade.error
async def trade_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"This command is on cooldown! Try again in {error.retry_after:.2f} seconds.")
    else:
        raise error


@client.tree.command(name="add_artist", description="Add an artist to team. No scoring from before they were added", guild=GUILD_ID)
@commands.cooldown(1, team_command_cooldown, commands.BucketType.user)
async def add_artist(interaction: discord.Interaction, drop_artist: str, add_artist: str):
    if draft is None:
        await interaction.response.send_message(f"Load or start a draft to start a season.")
        return

    if draft.is_stage([0, 1, 2]):
        await interaction.response.send_message("Need to start draft before adding artists", delete_after=10, ephemeral=True)
        return

    user = interaction.user

    player: Player | None = None
    for p in draft.draft_players:
        if p.user_id == user.id:
            player = p
            break

    if player is None:
        await interaction.response.send_message("You are not in the draft.", delete_after=10, ephemeral=True)
        return
    if draft.check_if_recieved_trade(player):
        await interaction.response.send_message("Can't add player with pending trade, decline or accept it.", delete_after=10, ephemeral=True)
        return
    if drop_artist not in player.artists:
        await interaction.response.send_message(f"Artist {drop_artist} is not in Team {player.team_name}.", delete_after=10, ephemeral=True)
        return
    if add_artist in player.artists:
        await interaction.response.send_message(f"Artist {add_artist} is on the Team {player.team_name}.", delete_after=10, ephemeral=True)
        return
    if add_artist not in draft.all_artists:
        await interaction.response.send_message(f"Artist {add_artist} is not in the artist pool.", delete_after=10, ephemeral=True)
        return
    if player.artsist_adds_left == 0:
        await interaction.response.send_message(f"You have already added and dropped 3 players.", delete_after=10, ephemeral=True)
        return

    await interaction.response.send_message(f"Team {player.team_name} has dropped **{drop_artist}** and added **{add_artist}**.")
    draft.drafted_artists.remove(drop_artist)
    draft.drafted_artists.add(add_artist)
    player.add_artist(add_artist, drop_artist, draft.current_listeners[draft.all_artists.index(
        add_artist)])


@add_artist.error
async def add_artist_error(ctx, error):
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

        msg = await interaction.followup.send("Starting weekly league update. Please don't use any commands during the update...")
        if update is True:
            await update_draft(draft, interaction, msg)
            print(
                f"Week: {draft.week_in_season}, Week in matchup: {draft.week_in_matchup}, Matchup: {draft.matchup_count}")
        else:
            draft.next_week()
            print(
                f"Week: {draft.week_in_season}, Week in matchup: {draft.week_in_matchup}, Matchup: {draft.matchup_count}")
        await update_score(draft, interaction, msg)
        await save_changes(draft, interaction, msg)
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
    for player in draft.draft_players:
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
    for player in draft.draft_players:
        player_info: list = player.artist_info[
            artist]["albums_on_record"]
        player_info.remove(player_info[0])
    await interaction.response.send_message(f"Done.", delete_after=10, ephemeral=True)


@client.tree.command(name="testjoin", description="Join fantasy draft as a player.", guild=GUILD_ID)
@commands.cooldown(1, draft_command_cooldown, commands.BucketType.user)
async def join(interaction: discord.Interaction, team_name: str, user_id: str):
    global draft

    if draft is None:
        await interaction.response.send_message(f"Load or start a draft to join.")
        return

    if draft.is_stage(stage=[1, 2, 3]):
        await interaction.response.send_message("Draft already started", delete_after=10, ephemeral=True)
        return

    user = await client.fetch_user(int(user_id))

    if draft is not None:
        for p in draft.draft_players:
            if p.user_id == user.id:
                await interaction.response.send_message("You're already in the draft!", delete_after=10, ephemeral=True)
                return

    draft.add_new_player(user, user.id, user.name, team_name)

    player = None
    for p in draft.draft_players:
        if p.user_id == user.id:
            player = p
            break

    draft_name = f"draft{draft.draft_name}"
    save_object(draft, draft_name)

    await interaction.response.send_message(f"{user.name} as joined the draft with team **{player.team_name}**.")


@client.tree.command(name="testdraft", description="Draft artists to fantasy team.", guild=GUILD_ID)
@commands.cooldown(1, draft_command_cooldown, commands.BucketType.user)
async def draft_artist(interaction: discord.Interaction, artist_name: str, user_id: str):
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

    user = await client.fetch_user(int(user_id))

    if draft.is_stage(stage=[2, 3]):
        await interaction.response.send_message(
            "Draft is already over.", delete_after=10, ephemeral=True)
        return

    if draft.draft_players[draft.turn].user_id == user.id:
        for artist in draft.all_artists:
            if artist_selected == artist:
                player = draft.draft_players[draft.turn]

                if artist_selected in draft.drafted_artists:
                    await interaction.response.send_message(f"{artist_selected} has already been drafted. Draft another artist.", delete_after=10, ephemeral=True)
                    return

                await interaction.response.send_message(f"{user.name} has drafted {artist_selected}!")
                player.draft_artist(artist_selected)
                draft.drafted_artists.add(artist_selected)

                draft.next_turn()

                if draft.is_stage(1):
                    nextPlayer = draft.draft_players[draft.turn]
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

client.run(DISCORD_TOKEN)
