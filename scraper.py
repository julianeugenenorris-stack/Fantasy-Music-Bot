from bs4 import BeautifulSoup
from datetime import datetime
import requests
import time
import os
import glob
import pickle

scrapeRespectClock = 0.2  # seconds between requests


def download_pages():
    if not os.path.exists("data"):
        os.makedirs("data")

    url = "https://kworb.net/spotify/listeners"
    page = 1

    while True:
        time.sleep(scrapeRespectClock)
        try:
            page_url = f"{url}{page}.html" if page > 1 else f"{url}.html"
            r = requests.get(page_url)
            r.raise_for_status()  # raise an HTTPError for bad responses
        except requests.exceptions.RequestException:
            print(f"No more pages found. Total pages downloaded: {page-1}")
            break

        # Parse the page to see if it contains table rows
        soup = BeautifulSoup(r.content, "html.parser")
        rows = soup.select("tbody tr")
        if not rows:
            print(f"No rows found on page {page}. Stopping download.")
            break

        # Save the page locally
        with open(get_data_file_location(f"page_{page}.html"), "wb") as f:
            f.write(r.content)

        print(f"Downloaded page {page}")
        page += 1

    return


def delete_downloaded_pages():
    folder = "data"

    # If folder doesn't exist, nothing to delete
    if not os.path.exists(folder):
        print("No data folder found.")
        return

    # Delete all HTML files: page_1.html, page_2.html, etc.
    files = glob.glob(os.path.join(folder, "page_*.html"))

    if not files:
        print("No page files to delete.")
        return

    for file in files:
        os.remove(file)
        print(f"Deleted {file}")


def parse_all_pages():
    artists = []
    listeners = []
    page = 1

    while True:
        filename = get_data_file_location(
            f"page_{page}.html")  # <- use full path

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


def write_list_to_file(data, filename):
    if not os.path.exists("data"):
        os.makedirs("data")

    with open(get_data_file_location(filename), "w", encoding="utf-8") as f:
        f.write("\n".join(map(str, data)))


def cache_is_current():
    os.makedirs("data", exist_ok=True)
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
    os.makedirs("data", exist_ok=True)
    with open(get_data_file_location("lastRan.txt"), "w") as f:
        f.write(datetime.now().strftime("%Y-%m-%d"))


def read_file(filename):
    if not os.path.exists("data"):
        os.makedirs("data")

    array = []
    try:
        with open(get_data_file_location(filename), "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()  # remove newline and extra spaces
                if line:             # skip empty lines
                    array.append(line)
    except FileNotFoundError:
        print(f"File {filename} not found.")
    return array


def save_object(obj, filename):
    if not os.path.exists("data"):
        os.makedirs("data")
    with open(get_data_file_location(filename), "wb") as f:
        pickle.dump(obj, f)


def load_object(filename):
    if not os.path.exists("data"):
        os.makedirs("data")
    with open(get_data_file_location(filename), "rb") as f:
        return pickle.load(f)


def get_data_file_location(filename):
    base_folder = os.path.dirname(os.path.abspath(__file__))
    data_folder = os.path.join(base_folder, "data")
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
    return os.path.join(data_folder, filename)
