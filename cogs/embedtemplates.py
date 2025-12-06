import discord
from cogs.player import Player
from cogs.draft import Draft
from cogs.scraper import *

WEEK_MONTH_CONVER = 4.34524


def team_template(user, player: Player, draft: Draft):
    embed = discord.Embed(
        title=f"{user.name}'s Team",
        color=discord.Color.blue(),
    )

    embed.set_thumbnail(url=user.display_avatar.url)
    count = 1
    for artist_name in player.get_all_artists():
        top_ranking = draft.get_all_artists().index(artist_name) + 1

        embed.add_field(name=f"{count}:\t{artist_name}",
                        value=f"Picked at #{player.get_all_artists().index(artist_name) + 1}. Ranked {top_ranking} in league ranking"
                        if player.get_artist(artist_name)["picked"] else
                        f"Artist was picked up. Ranked {top_ranking} in league ranking", inline=False)

        count += 1

    return embed


def artists_info_template(artist_name: str, draft: Draft):
    try:
        artist_id = get_artist_id(artist_name)
        albums_raw = get_all_artist_albums(artist_id)
        albums_formatted = ", ".join(albums_raw)
        most_recent_oaty = get_most_recent_album_user_score(artist_id)
        split_name = artist_name.replace(" ", "-")
        artist_url = split_name.lower()
        print(
            f"Length of artists: {len(draft.get_all_artists())}\nLength of Listeners: {len(draft.get_current_listeners())}")
        index_artist = draft.get_all_artists().index(artist_name)
        monthly_listeners = draft.get_current_listeners()[index_artist]

        recent_album_name = albums_raw[0] if albums_raw else "No albums found"
    except Exception as e:
        print(f"Error: {e}")
        return

    embed = discord.Embed(
        title=f"{artist_name}'s Info",
        url=f"https://www.albumoftheyear.org/artist/{artist_id}-{artist_url}/",
        color=discord.Color.red(),
    )

    embed.add_field(
        name=f"Most recent album for {artist_name}",
        value=f"User Score for {recent_album_name}: {most_recent_oaty}",
        inline=False
    )

    embed.add_field(
        name=f"Current albums on aoty",
        value=f"{albums_formatted}",
        inline=False
    )

    embed.add_field(
        name=f"Current monthly listeners",
        value=f"{monthly_listeners:,}",
        inline=False
    )

    embed.add_field(
        name=f"Current artist rank",
        value=f"#{index_artist+1:,}",
        inline=False
    )

    embed.set_footer(
        text=f"These are albums counted in last update, all new albums will be scored in the next update."
    )

    return embed


def billboard_template(draft: Draft):
    artist_info = draft.get_billboard_current_songs()
    titles = artist_info[0]
    artists = artist_info[1]

    embeds = []

    # create embeds in groups of 10
    for start in range(0, 100, 10):
        end = start + 10
        embeds.append(build_billboard_embed(start, end, titles, artists))

    return embeds


def build_billboard_embed(start, end, titles, artists):
    embed = discord.Embed(
        title=f"Billboard Hot 100: #{start+1}–{end}",
        color=discord.Color.dark_gold(),
    )

    embed.set_thumbnail(
        url="https://upload.wikimedia.org/wikipedia/commons/2/2b/Billboard_Hot_100_logo.jpg"
    )
    embed.set_footer(text="Features and 'With's are not included.")

    # Loop through 10 tracks
    for index in range(start, end):
        # prevent index errors
        if index >= len(titles):
            break

        title = titles[index]
        artist_list = artists[index]

        # Ensure artists is always a list of strings
        artist_list = [", ".join(a) if isinstance(
            a, list) else a for a in artist_list]

        artists_tag = ", ".join(artist_list)

        embed.add_field(
            name=f"#{index+1}: \"{title}\"",
            value=f"By: {artists_tag}",
            inline=False,
        )

    return embed


def artists_albums_template(user, player: Player, draft: Draft):
    embed = discord.Embed(
        title=f"{user.name}'s Team Artsits Albums",
        color=discord.Color.blue(),
    )

    embed.set_thumbnail(url=user.display_avatar.url)

    artist_info = player.get_artists_information()

    for count, (name, data) in enumerate(artist_info.items(), start=1):

        albums = ", ".join(data.get("albums_on_record", []))

        embed.add_field(
            name=f"{count}: {name}",
            value=f"{albums}",
            inline=False
        )

    return embed


def weekly_listeners_template(user, player: Player, draft: Draft):
    embed = discord.Embed(
        title=f"{user.name}'s Team Last Week",
        color=discord.Color.blue(),
    )

    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_footer(
        text=f"# is listeners counted this in week {draft.week_in_season}.")

    artist_info = player.get_artists_information()  # dict: {artist: {...}}

    for count, (artist_name, data) in enumerate(artist_info.items(), start=1):

        # safely get weekly score
        weekly = data.get("weekly")

        embed.add_field(
            name=f"{count}: {artist_name}",
            value=f"{weekly[len(weekly)-1]:,}",
            inline=False
        )

    embed.add_field(
        name=f"Total Weekly Listeners:",
        value=f"{player.weekly_listeners:,}",
        inline=False
    )

    return embed


def monthly_listeners_template(user, player: Player, draft):
    embed = discord.Embed(
        title=f"{user.name}'s Team Last Month",
        color=discord.Color.gold(),
    )

    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_footer(text="# is listeners for each week added together.")

    artist_info = player.get_artists_information()  # dict: {artist: {...}}

    monthly_listeners = 0

    for count, (artist_name, data) in enumerate(artist_info.items(), start=1):

        # safely get weemonthlykly score
        monthly = data.get("monthly")
        monthly_listeners += monthly[len(monthly)-1]
        embed.add_field(
            name=f"{count}: {artist_name}",
            value=f"{monthly[len(monthly)-1]:,}",
            inline=False
        )

    embed.add_field(
        name=f"Total Monthly Listeners:",
        value=f"{monthly_listeners:,}",
        inline=False
    )

    return embed


def total_listeners_template(user, player: Player, draft):
    embed = discord.Embed(
        title=f"{user.name}'s Team Total Listeners",
        color=discord.Color.purple(),
    )

    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_footer(text="# is listeners.")

    artist_info = player.get_artists_information()  # dict: {artist: {...}}

    for count, (artist_name, data) in enumerate(artist_info.items(), start=1):

        # safely get weekly score
        yearly = data.get("yearly_total")

        embed.add_field(
            name=f"{count}: {artist_name}",
            value=f"{yearly:,}",
            inline=False
        )

    embed.add_field(
        name=f"Total Listeners:",
        value=f"{player.total_listeners:,}",
        inline=False
    )

    return embed


def weekly_scores_template(user, player: Player, draft: Draft):
    embed = discord.Embed(
        title=f"{user.name}'s Team Last Week",
        color=discord.Color.blue(),
    )

    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_footer(text="# is listeners per month.")

    artist_scores = player.get_artists_information()  # dict: {artist: {...}}

    if not artist_scores:
        embed.add_field(
            name="No Scores Found",
            value="This player has no artist data yet.",
            inline=False
        )
        return embed

    for count, (artist_name, data) in enumerate(artist_scores.items(), start=1):

        # safely get weekly score
        weekly = data.get("weekly", 0)

        embed.add_field(
            name=f"{count}: {artist_name}",
            value=f"{weekly:,}",
            inline=False
        )

    return embed


def monthly_scores_template(user, player, draft):
    embed = discord.Embed(
        title=f"{user.name}'s Team Last Month",
        color=discord.Color.gold(),
    )

    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_footer(text="# is listeners per month.")

    monthly_scores = player.getMonthlyArtistScores()
    count = 1

    for artist_name in enumerate(player.get_all_artists()):
        # Get score from dict safely
        listeners = monthly_scores.get(artist_name)

        if listeners is None:
            if artist_name in draft.get_all_artists():
                return "Need more information to perform this command."
            listeners = 0

        embed.add_field(
            name=f"{count}: {artist_name}",
            value=f"{listeners:,}",
            inline=False,
        )
        count += 1

    return embed


def total_scores_template(user, player, draft):
    embed = discord.Embed(
        title=f"{user.name}'s Team Total Listeners",
        color=discord.Color.purple(),
    )

    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_footer(text="# is listeners.")

    total_scores = player.get_total_score()
    count = 1

    for artist_name in player.get_all_artists():
        listeners = total_scores.get(artist_name)

        if listeners is None:
            if artist_name in draft.get_all_artists():
                return "Need more information to perform this command."
            listeners = 0

        embed.add_field(
            name=f"{count}: {artist_name}",
            value=f"{listeners:,}",
            inline=False,
        )
        count += 1

    return embed
