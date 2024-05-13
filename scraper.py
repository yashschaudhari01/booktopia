import requests
from bs4 import BeautifulSoup
from json import loads as jsonloads
import pandas as pd
import csv


all_details = []
next_json_not_found = []

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9,en-IN;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
}

# Main function to scrape bookid
def scrape(bookid):
    try:
        response = requests.get(
            f"https://www.booktopia.com.au/abc/book/{bookid}.html",     # Creating url from bookid
            headers=headers,
        )
        soup = BeautifulSoup(response.content, "html.parser")

        # Find __NEXT_DATA__ which contains all the data related to the book 
        next_data_soup = (
            soup.find("script", {"id": "__NEXT_DATA__"})
            .string.removeprefix('<script id="__NEXT_DATA__" type="application/json">')
            .removesuffix("</script>")
        )

        next_json = jsonloads(next_data_soup)

        # Parsing the __NEXT_DATA__ json to get all the details

        product_details = next_json.get("props").get("pageProps").get("product")

        title = product_details.get("displayName")
        mrp = product_details.get("retailPrice")
        price_sp = product_details.get("salePrice")

        authors = []

        contributors_list = product_details.get("contributors")

        if len(contributors_list) > 0:
            for each_contributor in contributors_list:
                if each_contributor.get("role") == "Author":
                    authors.append(each_contributor.get("name"))

        booktype = product_details.get("bindingFormat")
        isbn10 = product_details.get("isbn10")
        publicationDate = product_details.get("publicationDate")
        publisher = product_details.get("publisher")
        numberOfPages = product_details.get("numberOfPages")

        output = {
            "Title of the Book": title,
            "Author/s": " | ".join(authors),
            "Book type": booktype,
            "Original Price": mrp,
            "Discounted price": price_sp,
            "ISBN-10": isbn10,
            "Published Date": publicationDate,
            "Publisher": publisher,
            "No. of Pages": numberOfPages,
        }
        all_details.append(output)
    except Exception as e:
        print(e)
        next_json_not_found.append(bookid)
        output = {
            "Title of the Book": "book not found",
            "Author/s": "",
            "Book type": "",
            "Original Price": "",
            "Discounted price": "",
            "ISBN-10": "",
            "Published Date": "",
            "Publisher": "",
            "No. of Pages": "",
        }
        all_details.append(output)


# Enter the input list csv path here
csv_path = r"D:\FP\technolution\input_list.csv"

# Read csv to get bookids
df = pd.read_csv(csv_path)

# Scrapping each bookid
for each_bookid in df["ISBN13"]:
    print(f"Scraping started for bookid : {each_bookid}")
    scrape(each_bookid)
    print(f"Scraping done for bookid : {each_bookid}\n")


# Saving the results to csv
def save_to_csv():
    csv_file_path = "booktopia.csv"

    header = [
        "Title of the Book",
        "Author/s",
        "Book type (paperback, hardcover, ebook, or anything that is mentioned on the site, etc)",
        "Original Price (RRP)",
        "Discounted price",
        "ISBN-10",
        "Published Date ( in YYYY-MM-DD)",
        "Publisher",
        "No. of Pages",
    ]
    with open(csv_file_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        writer.writeheader()

        for entry in all_details:
            writer.writerow(entry)
    print(f"CSV created!!")

# Creating log file to store bookids failed to scrape
def log_not_done_bookids():
    with open("not_done_booktopia.txt", "w", newline="", encoding="utf-8") as txtfile:
        txtfile.write([f"{ech}\n" for ech in next_json_not_found])
    print("Logs created!!")
