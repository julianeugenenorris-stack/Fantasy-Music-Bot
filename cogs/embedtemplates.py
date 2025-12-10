from discord.ui import View, Button
import discord
from cogs.player import Player
from cogs.draft import Draft
from cogs.scraper import *
from discord.ui import View, Button

WEEK_MONTH_CONVER = 4.34524


class TemplateView(View):
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


def team_template(player: Player, draft: Draft):
    embed = discord.Embed(
        title=f"Team **{player.team_name}**",
        color=discord.Color.dark_magenta(),
    )

    embed.set_thumbnail(url=player.user_image)
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


def overview_template(draft: Draft, type, time):
    embeds = []

    for player in draft.draft_players:
        if time == "total":
            embeds.append(total_scores_template(player, type))
        if time == "week":
            embeds.append(weekly_scores_template(player, type))
        if time == "matchup":
            embeds.append(matchup_scores_template(player, type))

    return embeds


def schedule_template(draft: Draft, players, type: str):
    embeds = []

    for p1, p2 in list(draft.week_matchups):
        embed = build_player_matchup(p1, p2, type)
        if embed:
            embeds.append(embed)

    return embeds


def build_schedule_template(draft: Draft):
    embed = discord.Embed(
        title=f"All Matchups This Week.",
        color=discord.Color.dark_grey(),
    )

    embed.set_footer(text=f"Matchups for week {draft.week_in_season}")

    for p1, p2 in list(draft.week_matchups):
        embed.add_field(
            name=f"{p1.team_name}",
            value=f"{p1.name}: {p1.record[0]}-{p1.record[1]}",
            inline=True
        )
        embed.add_field(
            name=f"{p2.team_name}",
            value=f"{p2.name}: {p2.record[0]}-{p2.record[1]}",
            inline=True
        )
        embed.add_field(
            name=f"",
            value=f"",
            inline=False
        )

    return embed


def build_player_matchup(p1: Player | str, p2: Player | str, type: str):
    if isinstance(p1, str) or isinstance(p2, str):
        return discord.Embed(title="This player or thier opponent is on a BYE week.", color=discord.Color.dark_grey())

    players = [p1, p2]
    embed = discord.Embed(
        title=f"Matchup: **{p1.team_name}** vs **{p2.team_name}**",
        color=discord.Color.dark_grey(),
    )
    if type == "all":
        for player in players:
            embed.add_field(
                name=f"Matchup Billboard Score:",
                value=f"{player.matchup_billboard_score:.2f}",
                inline=True
            )

        embed.add_field(
            name=f"",
            value=f"",
            inline=False
        )

        for player in players:
            embed.add_field(
                name=f"Matchup Album Score:",
                value=f"{player.matchup_aoty_score:.2f}",
                inline=True
            )
        embed.add_field(
            name=f"",
            value=f"",
            inline=False
        )
        for player in players:
            embed.add_field(
                name=f"Matchup Listeners Score:",
                value=f"{player.matchup_listeners_score:.2f}",
                inline=True
            )
        embed.add_field(
            name=f"",
            value=f"",
            inline=False
        )
        for player in players:
            embed.add_field(
                name=f"Matchup Change Score:",
                value=f"{player.matchup_change_score:.2f}",
                inline=True
            )
        embed.add_field(
            name=f"",
            value=f"",
            inline=False
        )
        for player in players:
            embed.add_field(
                name=f"Matchup Score Combined:",
                value=f"{player.matchup_score:.2f}",
                inline=True
            )
    if type == "billboard":
        for index, p1_artist in enumerate(p1.artist_info):
            p2_artist = p2.artist_info[index]
            p1_matchup_scores = p1_artist.get("total_billboard_score")
            p2_matchup_scores = p2_artist.get("total_billboard_score")

            embed.add_field(
                name=f"{p1_artist}:",
                value=f"Matchup Billboard Score: {p1_matchup_scores:,.2f}",
                inline=True
            )
            embed.add_field(
                name=f"{p2_artist}:",
                value=f"Matchup Billboard Score: {p2_matchup_scores:,.2f}",
                inline=True
            )
            embed.add_field(
                name=f"",
                value=f"",
                inline=False
            )

        for player in players:
            embed.add_field(
                name=f"Matchup Total Billboard Score:",
                value=f"{player.matchup_billboard_score:.2f}",
                inline=True
            )

    if type == "aoty":
        for player in players:
            for artist in player.artists:
                total_scores = player.artist_info.get("matchup_album_score")

                if total_scores != 0:
                    embed.add_field(
                        name=f"{artist}:",
                        value=f"Matchup Album Score: {total_scores:,.2f}",
                        inline=True
                    )
                else:
                    embed.add_field(
                        name=f"{artist}:",
                        value=f"Has no new albums.",
                        inline=True
                    )

        for player in players:
            embed.add_field(
                name=f"Matchup Total Billboard Score:",
                value=f"{player.matchup_billboard_score:.2f}",
                inline=True
            )

    if type == "listeners":
        for player in players:
            for artist in player.artists:
                total_scores = player.artist_info.get(
                    "matchup_listeners_score")

                if total_scores != 0:
                    embed.add_field(
                        name=f"{artist}:",
                        value=f"Matchup Listeners Score: {total_scores:,.2f}",
                        inline=True
                    )
                else:
                    embed.add_field(
                        name=f"{artist}:",
                        value=f"Has no new albums.",
                        inline=True
                    )

        for player in players:
            embed.add_field(
                name=f"Total Listeners Score:",
                value=f"{player.total_billboard_score:.2f}",
                inline=True
            )

    if type == "change":
        for player in players:
            for artist in player.artists:
                total_scores = player.artist_info.get(
                    "matchup_change_score")

                if total_scores != 0:
                    embed.add_field(
                        name=f"{artist}:",
                        value=f"Matchup Change Score: {total_scores:,.2f}",
                        inline=True
                    )
                else:
                    embed.add_field(
                        name=f"{artist}:",
                        value=f"Has no change.",
                        inline=True
                    )

        for player in players:
            embed.add_field(
                name=f"Matchup Total Change Score:",
                value=f"{player.total_change_score:.2f}",
                inline=True
            )

    return embed


def artists_albums_template(player: Player):
    embed = discord.Embed(
        title=f"Team **{player.team_name}**'s Artsits Albums",
        color=discord.Color.green(),
    )

    embed.set_thumbnail(url=player.user_image)
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


def new_league_albums_template(draft: Draft):
    embed = discord.Embed(
        title=f"New albums this week",
        color=discord.Color.green(),
    )

    embed.set_footer(text="From aoty.")

    for player in draft.draft_players:
        for artist in player.artists:
            info = player.artist_info.get(artist)
            if info["new_album_name"] != "":
                embed.add_field(
                    name=f"Team {player.team_name}: Artist {artist} has new album:",
                    value=f"**{info["new_album_name"]}**",
                    inline=False
                )

    return embed


def listeners_template(player: Player, draft: Draft, time: str):
    embed = discord.Embed(
        title=f"Team **{player.team_name}**'s Listeners This {time.capitalize}" if type != "total" else f"Team **{player.team_name}**'s {time.capitalize} Listeners ",
        color=discord.Color.blue(),
    )

    embed.set_thumbnail(url=player.user_image)

    artist_info = player.artist_info

    if time == "week":
        embed.set_footer(
            text=f"# is listeners counted this in week {draft.week_in_season}.")

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
    elif time == "matchup":
        embed.set_footer(
            text=f"# is listeners counted this in matchup {draft.matchup_count+1}.")

        for count, (artist_name, data) in enumerate(artist_info.items(), start=1):

            matchup = data.get("matchup_listeners")

            embed.add_field(
                name=f"{count}: {artist_name}",
                value=f"{matchup:, }",
                inline=False
            )

        embed.add_field(
            name=f"Total Matchup Listeners:",
            value=f"{player.matchup_listeners:,}",
            inline=False
        )

        return embed
    elif time == "total":
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


def weekly_scores_template(player: Player, type: str):
    embed = discord.Embed(
        title=f"Team **{player.team_name}**'s {type.capitalize()} Score Last Week",
        color=discord.Color.green(),
    )
    if type == "all":
        embed.set_thumbnail(url=player.user_image)

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

            week_total_score = data.get("week_total_score")

            embed.add_field(
                name=f"{artist_name}:",
                value=f"Total Weekly Score: {week_total_score:,.2f}",
                inline=False
            )

        embed.add_field(
            name=f"Total Weekly Billboard Score:",
            value=f"{player.weeks_billboard_score:.2f}",
            inline=False
        )

        embed.add_field(
            name=f"Total Week's Album Score:",
            value=f"{player.weeks_aoty_score:.2f}",
            inline=False
        )

        embed.add_field(
            name=f"Total Weekly Listeners Score:",
            value=f"{player.weeks_listener_score:.2f}",
            inline=False
        )

        embed.add_field(
            name=f"Total Weekly Change Score:",
            value=f"{player.weeks_change_score:.2f}",
            inline=False
        )

        embed.add_field(
            name=f"Total Score Combined:",
            value=f"{player.weeks_score:.2f}",
            inline=False
        )

        return embed

    if type == "billboard":
        embed.set_thumbnail(url=player.user_image)

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

        embed.add_field(
            name=f"Total Weekly Billboard Score:",
            value=f"{player.weeks_billboard_score:.2f}",
            inline=False
        )

        return embed

    if type == "aoty":
        embed.set_thumbnail(url=player.user_image)

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
            week_album_score = data.get("week_album_score")

            if new_album_name != "":
                embed.add_field(
                    name=f"{artist_name}:",
                    value=f"New Album: {new_album_name}\nAoty User Score: {week_album_score}\nAlbum Score Added: {new_album_score}",
                    inline=False
                )
            else:
                embed.add_field(
                    name=f"{artist_name}:",
                    value=f"Has no new albums.",
                    inline=False
                )

        embed.add_field(
            name=f"Total Week's Album Score:",
            value=f"{player.weeks_aoty_score:.2f}",
            inline=False
        )

        return embed

    if type == "listeners":
        embed.set_thumbnail(url=player.user_image)

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

            weekly_score = data.get("weekly_listeners_score")

            embed.add_field(
                name=f"#{count} {artist_name}:",
                value=f"{weekly_score:.2f}",
                inline=False
            )

        embed.add_field(
            name=f"Total Weekly Listeners Score:",
            value=f"{player.weeks_listener_score:.2f}",
            inline=False
        )

        return embed

    if type == "change":
        embed.set_thumbnail(url=player.user_image)

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

        embed.add_field(
            name=f"Total Weekly Change Score:",
            value=f"{player.weeks_change_score:.2f}",
            inline=False
        )

        return embed


def total_scores_template(player: Player, type: str):
    embed = discord.Embed(
        title=f"Team **{player.team_name}**'s {type.capitalize()} Score Last Week",
        color=discord.Color.green(),
    )
    if type == "all":
        embed.set_thumbnail(url=player.user_image)

        # dict: {artist: {...}}
        artist_scores = player.artist_info

        if not artist_scores:
            embed.add_field(
                name="No Scores Found",
                value="This player has no artist data yet.",
                inline=False
            )
            return embed

        embed.add_field(
            name=f"Total Billboard Score:",
            value=f"{player.total_billboard_score:.2f}",
            inline=False
        )

        embed.add_field(
            name=f"Total Album Score:",
            value=f"{player.total_aoty_score:.2f}",
            inline=False
        )

        embed.add_field(
            name=f"Total Listeners Score:",
            value=f"{player.total_listeners_score:.2f}",
            inline=False
        )

        embed.add_field(
            name=f"Total Change Score:",
            value=f"{player.total_change_score:.2f}",
            inline=False
        )

        embed.add_field(
            name=f"Total Score Combined:",
            value=f"{player.total_score:.2f}",
            inline=False
        )

        return embed

    if type == "billboard":
        embed.set_thumbnail(url=player.user_image)

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

            total_scores = data.get("total_billboard_score")

            if total_scores != 0:
                embed.add_field(
                    name=f"{artist_name}:",
                    value=f"Total Billboard Score: {total_scores:,.2f}",
                    inline=False
                )
            else:
                embed.add_field(
                    name=f"{artist_name}:",
                    value=f"Has no billboard songs.",
                    inline=False
                )

        embed.add_field(
            name=f"Total Billboard Score:",
            value=f"{player.total_billboard_score:.2f}",
            inline=False
        )

        return embed

    if type == "aoty":
        embed.set_thumbnail(url=player.user_image)

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

            total_album_score = data.get("total_album_score")

            if total_album_score == 0:
                embed.add_field(
                    name=f"{artist_name}:",
                    value=f"Total Album Score: {total_album_score:,.2f}",
                    inline=False
                )
            else:
                embed.add_field(
                    name=f"{artist_name}:",
                    value=f"Has no new albums.",
                    inline=False
                )

        embed.add_field(
            name=f"Total Album Score:",
            value=f"{player.total_aoty_score:.2f}",
            inline=False
        )

        return embed

    if type == "listeners":
        embed.set_thumbnail(url=player.user_image)

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

            total_listener_score = data.get("yearly_total")

            embed.add_field(
                name=f"#{count} {artist_name}:",
                value=f"{total_listener_score:.2f}",
                inline=False
            )

        embed.add_field(
            name=f"Total Weekly Listeners Score:",
            value=f"{player.total_listeners_score:.2f}",
            inline=False
        )

        return embed

    if type == "change":
        embed.set_thumbnail(url=player.user_image)

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

            total_score_change = data.get("total_score_change")

            if total_score_change == 0:
                embed.add_field(
                    name=f"{artist_name}:",
                    value=f"Change Score: {total_score_change:.2f}",
                    inline=False
                )
            else:
                embed.add_field(
                    name=f"{artist_name}:",
                    value=f"No change in listeners or less than half a million monthly listeners",
                    inline=False
                )

        embed.add_field(
            name=f"Total Weekly Change Score:",
            value=f"{player.weeks_change_score:.2f}",
            inline=False
        )

        return embed


def certain_week_template(player: Player, week):
    embed = discord.Embed(
        title=f"Team **{player.team_name}**'s Listeners In Week {week}",
        color=discord.Color.green(),
    )
    embed.set_thumbnail(url=player.user_image)

    # dict: {artist: {...}}
    artist_scores = player.artist_info

    if not artist_scores:
        embed.add_field(
            name="No Scores Found",
            value="This player has no artist data yet.",
            inline=False
        )
        return embed

    week_total = 0
    for count, (artist_name, data) in enumerate(artist_scores.items(), start=1):

        week_listeners = data.get("weekly")
        week_total += week_listeners[week]

        embed.add_field(
            name=f"#{count} {artist_name}:",
            value=f"{week_listeners[week]:.2f}",
            inline=False
        )

    embed.add_field(
        name=f"Week #{week+1} Total:",
        value=f"{week_total:.2f}",
        inline=False
    )

    return embed


def matchup_scores_template(player: Player, type: str):
    embed = discord.Embed(
        title=f"Team **{player.team_name}**'s {type.capitalize()} Score In Matchup",
        color=discord.Color.green(),
    )

    if type == "all":
        embed.set_thumbnail(url=player.user_image)

        artist_scores = player.artist_info

        if not artist_scores:
            embed.add_field(
                name="No Scores Found",
                value="This player has no artist data yet.",
                inline=False
            )
            return embed

        embed.add_field(
            name=f"Matchup Billboard Score:",
            value=f"{player.matchup_billboard_score:.2f}",
            inline=False
        )

        embed.add_field(
            name=f"Matchup Album Score:",
            value=f"{player.matchup_aoty_score:.2f}",
            inline=False
        )

        embed.add_field(
            name=f"Matchup Listeners Score:",
            value=f"{player.matchup_listeners_score:.2f}",
            inline=False
        )

        embed.add_field(
            name=f"Matchup Change Score:",
            value=f"{player.matchup_change_score:.2f}",
            inline=False
        )

        embed.add_field(
            name=f"Matchup Score Combined:",
            value=f"{player.matchup_score:.2f}",
            inline=False
        )

        return embed

    if type == "billboard":
        embed.set_thumbnail(url=player.user_image)

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

            total_scores = data.get("total_billboard_score")

            if total_scores != 0:
                embed.add_field(
                    name=f"{artist_name}:",
                    value=f"Total Billboard Score: {total_scores:,.2f}",
                    inline=False
                )
            else:
                embed.add_field(
                    name=f"{artist_name}:",
                    value=f"Has no billboard songs.",
                    inline=False
                )

        embed.add_field(
            name=f"Total Billboard Score:",
            value=f"{player.total_billboard_score:.2f}",
            inline=False
        )

        return embed

    if type == "aoty":
        embed.set_thumbnail(url=player.user_image)

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

            total_album_score = data.get("total_album_score")

            if total_album_score == 0:
                embed.add_field(
                    name=f"{artist_name}:",
                    value=f"Total Album Score: {total_album_score:,.2f}",
                    inline=False
                )
            else:
                embed.add_field(
                    name=f"{artist_name}:",
                    value=f"Has no new albums.",
                    inline=False
                )

        embed.add_field(
            name=f"Total Album Score:",
            value=f"{player.total_aoty_score:.2f}",
            inline=False
        )

        return embed

    if type == "listeners":
        embed.set_thumbnail(url=player.user_image)

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

            total_listener_score = data.get("yearly_total")

            embed.add_field(
                name=f"#{count} {artist_name}:",
                value=f"{total_listener_score:.2f}",
                inline=False
            )

        embed.add_field(
            name=f"Total Weekly Listeners Score:",
            value=f"{player.total_listeners_score:.2f}",
            inline=False
        )

        return embed

    if type == "change":
        embed.set_thumbnail(url=player.user_image)

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

            total_score_change = data.get("total_score_change")

            if total_score_change == 0:
                embed.add_field(
                    name=f"{artist_name}:",
                    value=f"Change Score: {total_score_change:.2f}",
                    inline=False
                )
            else:
                embed.add_field(
                    name=f"{artist_name}:",
                    value=f"No change in listeners or less than half a million monthly listeners",
                    inline=False
                )

        embed.add_field(
            name=f"Total Weekly Change Score:",
            value=f"{player.weeks_change_score:.2f}",
            inline=False
        )

        return embed
