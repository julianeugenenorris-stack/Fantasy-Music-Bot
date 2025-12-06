from discord.ui import View, Button
import discord
from cogs.player import Player
from cogs.draft import Draft
from cogs.scraper import *
from discord.ui import View, Button

WEEK_MONTH_CONVER = 4.34524


class BillboardView(View):
    def __init__(self, embeds):
        super().__init__(timeout=120)  # 2 minutes, adjust if needed
        self.embeds = embeds
        self.index = 0

        # Disable previous at start
        self.update_buttons()

    def update_buttons(self):
        self.children[0].disabled = (self.index == 0)
        self.children[1].disabled = (self.index == len(self.embeds) - 1)

    @discord.ui.button(label="◀️ Previous", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction: discord.Interaction, button: Button):
        self.index -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.index], view=self)

    @discord.ui.button(label="Next ▶️", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: Button):
        self.index += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.index], view=self)


def team_template(user, player: Player, draft: Draft):
    embed = discord.Embed(
        title=f"{user.name}'s Team",
        color=discord.Color.dark_magenta(),
    )

    embed.set_thumbnail(url=user.display_avatar.url)
    count = 1
    for artist_name in player.artists:
        top_ranking = draft.all_artists.index(artist_name) + 1

        embed.add_field(name=f"{count}:\t{artist_name}",
                        value=f"Picked at #{player.artists.index(artist_name) + 1}. Ranked {top_ranking} in league ranking"
                        if player.get_artist(artist_name)["picked"] else
                        f"Artist was picked up. Ranked {top_ranking} in league ranking", inline=False)

        count += 1

    return embed


def artists_info_template(artist_name: str, draft: Draft):
    try:
        artist_id = get_artist_id(artist_name)
        albums_raw = get_all_artist_albums(artist_id)
        albums_formatted = ", ".join(albums_raw[0:15])
        most_recent_oaty = get_most_recent_album_user_score(artist_id)
        split_name = artist_name.replace(" ", "-")
        artist_url = split_name.lower()
        index_artist = draft.all_artists.index(artist_name)
        monthly_listeners = draft.current_listeners[index_artist]

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
        value=f"User Score for *{recent_album_name}* - {most_recent_oaty}",
        inline=False
    )

    embed.add_field(
        name=f"Current albums on aoty",
        value=f"{albums_formatted}" if len(
            albums_raw) < 15 else f"{albums_formatted}...",
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
        text=f"These are albums counted in last update, all new albums will be scored in the next update. Only 15 most recent albums displayed."
    )

    return embed


def billboard_template(draft: Draft):
    artist_info = draft.billboard_current_songs
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
        color=discord.Color.yellow(),
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
            value=f"by: {artists_tag}",
            inline=False,
        )

    return embed


def artists_albums_template(user, player: Player, draft: Draft):
    embed = discord.Embed(
        title=f"{user.name}'s Team Artsits Albums",
        color=discord.Color.green(),
    )

    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_footer(text="Only 5 most recent albums displayed.")

    artist_info = player.artist_info

    for count, (name, data) in enumerate(artist_info.items(), start=1):

        albums = ", ".join(data.get("albums_on_record", [])[0:5])

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

    artist_info = player.artist_info

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
        color=discord.Color.blue(),
    )

    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_footer(text="# is listeners for each week added together.")

    artist_info = player.artist_info

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
        color=discord.Color.blue(),
    )

    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_footer(text="# is listeners.")

    artist_info = player.artist_info

    for count, (artist_name, data) in enumerate(artist_info.items(), start=1):

        # safely get weekly score
        yearly = data.get("yearly_total")

        embed.add_field(
            name=f"{count}: {artist_name}",
            value=f"{int(yearly):,}",
            inline=False
        )

    embed.add_field(
        name=f"Total Listeners:",
        value=f"{player.total_listeners:,}",
        inline=False
    )

    return embed

# "billboard", "change", "aoty", "listeners", "all"


def weekly_scores_template(user, player: Player, draft: Draft, type: str):
    embed = discord.Embed(
        title=f"{user.name}'s Team {type.capitalize()} Score Last Week",
        color=discord.Color.green(),
    )
    if type == "all":
        embed.set_thumbnail(url=user.display_avatar.url)

        # dict: {artist: {...}}
        artist_scores = player.artist_info

        if not artist_scores:
            embed.add_field(
                name="No Scores Found",
                value="This player has no artist data yet.",
                inline=False
            )
            return embed

        total_score = player.total_billboard_score

        embed.add_field(
            name=f"Total Weekly Billboard Score:",
            value=f"{total_score}",
            inline=False
        )

        total_score = player.total_aoty_score

        embed.add_field(
            name=f"Total Week's Album Score:",
            value=f"{total_score}",
            inline=False
        )

        total_score = player.weekly_listeners_score

        embed.add_field(
            name=f"Total Weekly Listeners Score:",
            value=f"{total_score:.2f}",
            inline=False
        )

        total_score = player.total_change_score

        embed.add_field(
            name=f"Total Weekly Change Score:",
            value=f"{total_score}",
            inline=False
        )

        return embed

    if type == "billboard":
        embed.set_thumbnail(url=user.display_avatar.url)

        # dict: {artist: {...}}
        artist_scores = player.artist_info

        if not artist_scores:
            embed.add_field(
                name="No Scores Found",
                value="This player has no artist data yet.",
                inline=False
            )
            return embed

        for count, (artist_name, data) in enumerate(artist_scores.items(), start=1):

            weekly_score = data.get("week_billboard_score")
            songs = data.get("songs_on_billboard")
            formatted_songs = ", ".join(songs)

            if weekly_score != 0:
                embed.add_field(
                    name=f"{artist_name}:",
                    value=f"Weekly Billboard Score: {weekly_score:,}\nSongs: {formatted_songs}",
                    inline=False
                )
            else:
                embed.add_field(
                    name=f"{artist_name}:",
                    value=f"Has no billboard songs.",
                    inline=False
                )

        total_score = player.total_billboard_score

        embed.add_field(
            name=f"Total Weekly Billboard Score:",
            value=f"{total_score}",
            inline=False
        )

        return embed

    if type == "aoty":
        embed.set_thumbnail(url=user.display_avatar.url)

        # dict: {artist: {...}}
        artist_scores = player.artist_info

        if not artist_scores:
            embed.add_field(
                name="No Scores Found",
                value="This player has no artist data yet.",
                inline=False
            )
            return embed

        for count, (artist_name, data) in enumerate(artist_scores.items(), start=1):

            new_album_name = data.get("new_album_name")
            new_album_score = data.get("new_album_score")
            new_album_aoty_score = data.get("new_album_aoty_score")

            if new_album_name != "":
                embed.add_field(
                    name=f"{artist_name}:",
                    value=f"New Album: {new_album_name}\nAoty User Score: {new_album_aoty_score}\nAlbum Score Added: {new_album_score}",
                    inline=False
                )
            else:
                embed.add_field(
                    name=f"{artist_name}:",
                    value=f"Has no new albums.",
                    inline=False
                )

        total_score = player.total_aoty_score

        embed.add_field(
            name=f"Total Week's Album Score:",
            value=f"{total_score}",
            inline=False
        )

        return embed

    if type == "listeners":
        embed.set_thumbnail(url=user.display_avatar.url)

        # dict: {artist: {...}}
        artist_scores = player.artist_info

        if not artist_scores:
            embed.add_field(
                name="No Scores Found",
                value="This player has no artist data yet.",
                inline=False
            )
            return embed

        for count, (artist_name, data) in enumerate(artist_scores.items(), start=1):

            weekly_score = data.get("weekly_score")

            embed.add_field(
                name=f"#{count} {artist_name}:",
                value=f"{weekly_score:.2f}",
                inline=False
            )

        total_score = player.weekly_listeners_score

        embed.add_field(
            name=f"Total Weekly Listeners Score:",
            value=f"{total_score:.2f}",
            inline=False
        )

        return embed

    if type == "change":
        embed.set_thumbnail(url=user.display_avatar.url)

        # dict: {artist: {...}}
        artist_scores = player.artist_info

        if not artist_scores:
            embed.add_field(
                name="No Scores Found",
                value="This player has no artist data yet.",
                inline=False
            )
            return embed

        for count, (artist_name, data) in enumerate(artist_scores.items(), start=1):

            listeners_change = data.get("listeners_change")
            score_change = data.get("score_change")

            if listeners_change == 0:
                embed.add_field(
                    name=f"{artist_name}:",
                    value=f"Change In Listeners: {listeners_change}\nChange Score: {score_change}",
                    inline=False
                )
            else:
                embed.add_field(
                    name=f"{artist_name}:",
                    value=f"No change in listeners or less than half a million monthly listeners",
                    inline=False
                )

        total_score = player.total_change_score

        embed.add_field(
            name=f"Total Weekly Change Score:",
            value=f"{total_score}",
            inline=False
        )

        return embed


def total_scores_template(user, player: Player, draft: Draft, type: str):
    embed = discord.Embed(
        title=f"{user.name}'s Team {type.capitalize()} Score Last Week",
        color=discord.Color.green(),
    )
    if type == "all":
        embed.set_thumbnail(url=user.display_avatar.url)

        # dict: {artist: {...}}
        artist_scores = player.artist_info

        if not artist_scores:
            embed.add_field(
                name="No Scores Found",
                value="This player has no artist data yet.",
                inline=False
            )
            return embed

        total_score = player.total_billboard_score

        embed.add_field(
            name=f"Total Weekly Billboard Score:",
            value=f"{total_score}",
            inline=False
        )

        total_score = player.total_aoty_score

        embed.add_field(
            name=f"Total Week's Album Score:",
            value=f"{total_score}",
            inline=False
        )

        total_score = player.weekly_listeners_score

        embed.add_field(
            name=f"Total Weekly Listeners Score:",
            value=f"{total_score:.2f}",
            inline=False
        )

        total_score = player.total_change_score

        embed.add_field(
            name=f"Total Weekly Change Score:",
            value=f"{total_score}",
            inline=False
        )

        return embed

    if type == "billboard":
        embed.set_thumbnail(url=user.display_avatar.url)

        # dict: {artist: {...}}
        artist_scores = player.artist_info

        if not artist_scores:
            embed.add_field(
                name="No Scores Found",
                value="This player has no artist data yet.",
                inline=False
            )
            return embed

        for count, (artist_name, data) in enumerate(artist_scores.items(), start=1):

            total_score = data.get("total_billboard_score")

            if weekly_score != 0:
                embed.add_field(
                    name=f"{artist_name}:",
                    value=f"Total Billboard Score: {total_score:,}",
                    inline=False
                )
            else:
                embed.add_field(
                    name=f"{artist_name}:",
                    value=f"Has no billboard songs.",
                    inline=False
                )

        total_score = player.total_billboard_score

        embed.add_field(
            name=f"Total Weekly Billboard Score:",
            value=f"{total_score}",
            inline=False
        )

        return embed

    if type == "aoty":
        embed.set_thumbnail(url=user.display_avatar.url)

        # dict: {artist: {...}}
        artist_scores = player.artist_info

        if not artist_scores:
            embed.add_field(
                name="No Scores Found",
                value="This player has no artist data yet.",
                inline=False
            )
            return embed

        for count, (artist_name, data) in enumerate(artist_scores.items(), start=1):

            new_album_name = data.get("new_album_name")
            new_album_score = data.get("new_album_score")
            new_album_aoty_score = data.get("new_album_aoty_score")

            if new_album_name != "":
                embed.add_field(
                    name=f"{artist_name}:",
                    value=f"New Album: {new_album_name}\nAoty User Score: {new_album_aoty_score}\nAlbum Score Added: {new_album_score}",
                    inline=False
                )
            else:
                embed.add_field(
                    name=f"{artist_name}:",
                    value=f"Has no new albums.",
                    inline=False
                )

        total_score = player.total_aoty_score

        embed.add_field(
            name=f"Total Week's Album Score:",
            value=f"{total_score}",
            inline=False
        )

        return embed

    if type == "listeners":
        embed.set_thumbnail(url=user.display_avatar.url)

        # dict: {artist: {...}}
        artist_scores = player.artist_info

        if not artist_scores:
            embed.add_field(
                name="No Scores Found",
                value="This player has no artist data yet.",
                inline=False
            )
            return embed

        for count, (artist_name, data) in enumerate(artist_scores.items(), start=1):

            weekly_score = data.get("weekly_score")

            embed.add_field(
                name=f"#{count} {artist_name}:",
                value=f"{weekly_score:.2f}",
                inline=False
            )

        total_score = player.weekly_listeners_score

        embed.add_field(
            name=f"Total Weekly Listeners Score:",
            value=f"{total_score:.2f}",
            inline=False
        )

        return embed

    if type == "change":
        embed.set_thumbnail(url=user.display_avatar.url)

        # dict: {artist: {...}}
        artist_scores = player.artist_info

        if not artist_scores:
            embed.add_field(
                name="No Scores Found",
                value="This player has no artist data yet.",
                inline=False
            )
            return embed

        for count, (artist_name, data) in enumerate(artist_scores.items(), start=1):

            listeners_change = data.get("listeners_change")
            score_change = data.get("score_change")

            if listeners_change == 0:
                embed.add_field(
                    name=f"{artist_name}:",
                    value=f"Change In Listeners: {listeners_change}\nChange Score: {score_change}",
                    inline=False
                )
            else:
                embed.add_field(
                    name=f"{artist_name}:",
                    value=f"No change in listeners or less than half a million monthly listeners",
                    inline=False
                )

        total_score = player.total_change_score

        embed.add_field(
            name=f"Total Weekly Change Score:",
            value=f"{total_score}",
            inline=False
        )

        return embed


def total_scores_template(user, player, draft):
    embed = discord.Embed(
        title=f"{user.name}'s Team Total Listeners",
        color=discord.Color.green(),
    )

    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_footer(text="# is listeners.")

    total_scores = player.get_total_score()
    count = 1

    for artist_name in player.artists:
        listeners = total_scores.get(artist_name)

        if listeners is None:
            if artist_name in draft.all_artists:
                return "Need more information to perform this command."
            listeners = 0

        embed.add_field(
            name=f"{count}: {artist_name}",
            value=f"{listeners:,}",
            inline=False,
        )
        count += 1

    return embed


def matchup_scores_template(user, player, draft):
    embed = discord.Embed(
        title=f"{user.name}'s Team Last Week",
        color=discord.Color.green(),
    )

    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_footer(text="# is listeners per month.")

    artist_scores = player.artist_info

    if not artist_scores:
        embed.add_field(
            name="No Scores Found",
            value="This player has no artist data yet.",
            inline=False
        )
        return embed

    for count, (artist_name, data) in enumerate(artist_scores.items(), start=1):

        # safely get weekly score
        monthly = data.get("monthly", [])

        embed.add_field(
            name=f"{count}: {artist_name}",
            value=f"{monthly[len(monthly)-1]:,}",
            inline=False
        )

    return embed
