from urllib.request import Request, urlopen
import urllib.parse
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import time
import os
import glob
import pickle
import billboard

respect_clock = 1  # seconds between requests


def get_billboard_100(draft):
    """Returns [song titles, [artists]"""
    chart = billboard.ChartData('hot-100')

    billboard_artists = []
    billboard_songs = []
    special_artists = []

    # remove comma names
    for creator in draft.get_all_artists():
        if creator.rfind(",") != -1:
            special_artists.append(creator.split(",")[0])

    for entry in chart[0:]:
        title = entry.title
        artist: str = entry.artist

        if artist.split(", ") in special_artists:
            artist.remove(",")

        artist_replace: str = artist.replace(
            " & ", ", ").replace(" And ", ", ")

        artist_split_1: str = artist_replace.split(":")[0]
        artist_split_2: str = artist_split_1.split(" Featuring ")[0]
        artist_split_3: str = artist_split_2.split(" With ")[0]
        artist_split_4: str = artist_split_3.split(" Feat. ")[0]
        artist_split_5: str = artist_split_4.split(" Feat ")[0]

        artists: list = artist_split_5.split(", ")
        billboard_artists.append(artists)
        billboard_songs.append(title)

    return billboard_songs, billboard_artists


def get_artist_id(artist_name):
    time.sleep(respect_clock)
    """Returns the special character ID for an artist from AlbumOfTheYear.org."""
    # Replace spaces with "+" for URL
    query = urllib.parse.quote_plus(artist_name)
    search_url = f"https://www.albumoftheyear.org/search/?q={query}"
    print(f"Looking up : {search_url}")

    # Set a browser-like user-agent
    try:
        req = Request(search_url, headers={"User-Agent": "Mozilla/6.0"})
        page = urlopen(req).read()
    except Exception as e:
        print(f"Error getting aoty id: {e}")
        return None

    # Parse HTML
    soup = BeautifulSoup(page, "html.parser")

    # Find the first artist result link
    # Artist links usually start with "/artist/<id>-<name>/"
    artist_link = soup.find("a", href=lambda x: x and x.startswith("/artist/"))

    if artist_link:
        # Extract the part after "/artist/" and before the next "/"
        href = artist_link['href']
        artist_id_tag = href.split("/")[2]  # href = "/artist/183-kanye-west/"
        # artist_id = artist_id_tag.split("-")[0]
        return artist_id_tag
    else:
        return None


def get_all_artist_albums(artist_id):
    time.sleep(respect_clock)
    artist_url = f"https://www.albumoftheyear.org/artist/{artist_id}/"
    print(f"Looking up : {artist_url}")

    try:
        req = Request(artist_url, headers={"User-Agent": "Mozilla/6.0"})
        page = urlopen(req).read()
    except Exception as e:
        print(f"Error getting aoty albums: {e}")
        return []

    soup = BeautifulSoup(page, "html.parser")

    categorized_albums = {}
    current_category = None

    # This is safer because album blocks are structured consistently
    album_blocks = soup.find_all("div", class_="albumBlock")

    albums = []
    for block in album_blocks:
        title_div = block.find("div", class_="albumTitle")
        if not title_div:
            continue

        # KEEP UNICODE
        album_name = title_div.get_text(strip=True)

        # Skip blank names (shouldn't happen anymore)
        if album_name:
            albums.append(album_name)

    return albums


def get_most_recent_album_user_score(artist_id):
    time.sleep(respect_clock)
    """
    Returns the user score of the most recent album for the given artist ID.

    Example:
    get_most_recent_album_user_score("500-clipse") -> "7.2"
    """
    artist_url = f"https://www.albumoftheyear.org/artist/{artist_id}/"
    print(f"Looking up : {artist_url}")

    # Make the request with a browser User-Agent
    try:
        req = Request(artist_url, headers={"User-Agent": "Mozilla/6.0"})
        page = urlopen(req).read()
    except Exception as e:
        print(f"Error getting aoty user score: {e}")
        return 0

    soup = BeautifulSoup(page, "html.parser")

    # Albums are usually listed in a div with class "albumTitle" inside a container
    album_blocks = soup.find_all("div", class_="albumBlock")

    if not album_blocks:
        return None  # No albums found

    # The first album block is usually the most recent
    most_recent_album = album_blocks[0]

    # User score is in a div with class "albumUserScore"
    user_score_div = most_recent_album.find_all("div", class_="rating")

    if user_score_div:
        try:
            score = user_score_div[1].get_text(strip=True)
            return score
        except IndexError:
            score = user_score_div[0].get_text(strip=True)
            return score
    else:
        return None  # No user score found


def download_pages():
    # delete old
    folder = "database"

    if not os.path.exists(folder):
        print("No data folder found.")
        return

    files = glob.glob(os.path.join(folder, "page_*.html"))

    if not files:
        print("No page files to delete.")

    for file in files:
        os.remove(file)
        print(f"Deleted {file}")

    url = "https://kworb.net/spotify/listeners"
    page = 1

    # print new
    while True:
        time.sleep(respect_clock)
        try:
            page_url = f"{url}{page}.html" if page > 1 else f"{url}.html"
            print(f"Looking up : {page_url}")
            r = requests.get(page_url)
            r.raise_for_status()
        except requests.exceptions.RequestException:
            print(f"No more pages found. Total pages downloaded: {page-1}")
            break

        soup = BeautifulSoup(r.content, "html.parser")
        rows = soup.select("tbody tr")
        if not rows:
            print(f"No rows found on page {page}. Stopping download.")
            break

        with open(get_data_file_location(f"page_{page}.html"), "wb") as f:
            f.write(r.content)

        print(f"Downloaded page {page}")
        page += 1

    return


def parse_all_pages():
    artists = []
    listeners = []
    page = 1

    while True:
        filename = get_data_file_location(
            f"page_{page}.html")

        if not os.path.exists(filename):
            break

        with open(filename, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        rows = soup.select("tbody tr")
        if not rows:
            break

        for row in rows:
            name_cell = row.select_one(".text")
            tds = row.find_all("td")
            if not name_cell or len(tds) < 3:
                continue

            artists.append(name_cell.text.strip())
            listeners.append(int(tds[2].text.replace(",", "")))

        page += 1

    lists = [artists, listeners]
    return lists


def get_full_artists_data():
    url = "https://kworb.net/spotify/listeners"
    page = 1
    pages = []

    while True:
        time.sleep(respect_clock)
        try:
            page_url = f"{url}{page}.html" if page > 1 else f"{url}.html"
            r = requests.get(page_url)
            r.raise_for_status()
        except requests.exceptions.RequestException:
            print(f"No more pages found. Total pages downloaded: {page-1}")
            break

        soup = BeautifulSoup(r.content, "html.parser")

        pages.append(soup)

        print(f"Downloaded page {page}")
        page += 1

    artists = []
    listeners = []
    count = 1

    for soup in pages:
        rows = soup.select("tbody tr")
        if not rows:
            continue

        for row in rows:
            name_cell = row.select_one(".text")
            tds = row.find_all("td")
            if not name_cell or len(tds) < 3:
                continue

            count += 1
            artists.append(name_cell.text.strip())
            listeners.append(int(tds[2].text.replace(",", "")))

    return [artists, listeners]


def write_list_to_file(data, filename):
    if not os.path.exists("database"):
        os.makedirs("database")

    with open(get_data_file_location(filename), "w", encoding="utf-8") as f:
        f.write("\n".join(map(str, data)))


def cache_is_current():
    os.makedirs("database", exist_ok=True)
    last_ran_path = get_data_file_location("lastRan.txt")

    if not os.path.exists(last_ran_path):
        return False

    with open(last_ran_path, "r") as f:
        saved = f.read().strip()

    try:
        saved_date = datetime.strptime(saved, "%Y-%m-%d")
    except ValueError:
        return False

    delta = datetime.now() - saved_date
    return delta.days <= 7


def update_timestamp():
    os.makedirs("database", exist_ok=True)
    with open(get_data_file_location("lastRan.txt"), "w") as f:
        f.write(datetime.now().strftime("%Y-%m-%d"))


def read_file(filename):
    if not os.path.exists("database"):
        os.makedirs("database")

    array = []
    try:
        with open(get_data_file_location(filename), "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    array.append(line)
    except FileNotFoundError:
        print(f"File {filename} not found.")
    return array


def save_object(obj, filename):
    if not os.path.exists("database"):
        os.makedirs("database")
    with open(get_data_file_location(filename), "wb") as f:
        pickle.dump(obj, f)


def load_object(filename):
    if not os.path.exists("database"):
        os.makedirs("database")
    with open(get_data_file_location(filename), "rb") as f:
        return pickle.load(f)


def get_data_file_location(filename):
    db_folder = os.getenv("DB_FOLDER")

    if not db_folder:
        db_folder = os.path.join(os.path.expanduser("~"), "database")

    os.makedirs(db_folder, exist_ok=True)

    print(os.path.abspath(os.path.join(db_folder, filename)))

    return os.path.abspath(os.path.join(db_folder, filename))
