from matplotlib import lines
from playwright.sync_api import sync_playwright


def search_indeed(query):

    jobs = []

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        page = browser.new_page()

        page.goto(
            f"https://in.indeed.com/jobs?q={query}"
        )

        page.wait_for_timeout(5000)

        cards = page.locator(
            "[data-testid='slider_item']"
        )

        count = min(cards.count(), 2)

        print("CARDS FOUND:", count)

        for i in range(count):

            try:

                card = cards.nth(i)

                title = card.locator(
                    "span[title]"
                ).inner_text()

                card_text = card.inner_text()

                lines = card_text.split("\n")
                print("\nRAW LINES:")
                for idx, line in enumerate(lines):
                    print(idx, "=>", line)

                company = ""
                location = ""

                if len(lines) >= 3:
                    company = lines[2]

                if len(lines) >= 4:
                    location = lines[3]

                print("\n")
                print("=" * 50)
                print("TITLE:", title)
                print("COMPANY:", company)
                print("LOCATION:", location)
                print("=" * 50)

                jobs.append({
                    "title": title,
                    "company": company,
                    "location": location,
                    "details": card_text,
                    "query": query
                })

            except Exception as e:

                print(
                    f"Error in card {i}: {e}"
                )

        browser.close()

    return jobs