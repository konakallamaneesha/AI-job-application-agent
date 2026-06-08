from playwright.sync_api import sync_playwright


def get_job_description(url):

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page()

        page.goto(
            url,
            timeout=60000,
            wait_until="domcontentloaded"
        )

        page.wait_for_timeout(3000)

        jd = page.locator(
            "body"
        ).inner_text()

        browser.close()

    skills = []

    try:

        if "Skill(s) required" not in jd:

            return []

        section = jd.split(
            "Skill(s) required"
        )[1]

        stop_words = [

            "Who can apply",

            "Perks",

            "Number of openings",

            "About",

            "Additional information",

            "Earn certifications"

        ]

        end_index = len(section)

        for word in stop_words:

            pos = section.find(word)

            if pos != -1:

                end_index = min(
                    end_index,
                    pos
                )

        section = section[:end_index]

        for line in section.split("\n"):

            line = line.strip()

            if (
                line
                and len(line) < 50
                and "learn" not in line.lower()
                and "+ " not in line
            ):

                skills.append(line)

    except Exception as e:

        print(
            f"JD Error: {e}"
        )

    print(
        f"JD Skills ({url}):",
        skills
    )

    return skills


def search_internshala(query):

    jobs = []

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page()

        search_query = (
            query.lower()
            .replace(" ", "-")
        )

        try:

            page.goto(
                f"https://internshala.com/internships/{search_query}-internship/",
                timeout=60000,
                wait_until="domcontentloaded"
            )

        except Exception as e:

            print(
                f"Search Error: {e}"
            )

            browser.close()

            return jobs

        page.wait_for_timeout(
            5000
        )

        cards = page.locator(
            ".individual_internship"
        )

        count = min(
            cards.count(),
            10
        )

        print(
            f"{query} -> {count}"
        )

        for i in range(count):

            try:

                card = cards.nth(i)

                text = card.inner_text()

                link = card.get_attribute(
                    "data-href"
                )

                if link:

                    link = (
                        "https://internshala.com"
                        + link
                    )

                else:

                    link = ""

                lines = [

                    line.strip()

                    for line in text.split("\n")

                    if line.strip()

                ]

                title = (
                    lines[0]
                    if len(lines) > 0
                    else ""
                )

                company = (
                    lines[1]
                    if len(lines) > 1
                    else ""
                )

                location = ""

                for line in lines:

                    if (

                        "work from home"
                        in line.lower()

                        or "hyderabad"
                        in line.lower()

                        or "bangalore"
                        in line.lower()

                        or "mumbai"
                        in line.lower()

                        or "pune"
                        in line.lower()

                        or "delhi"
                        in line.lower()

                        or "chennai"
                        in line.lower()

                    ):

                        location = line

                        break

                jobs.append({

                    "title":
                    title,

                    "company":
                    company,

                    "location":
                    location,

                    "details":
                    text,

                    "url":
                    link,

                    "query":
                    query

                })

            except Exception as e:

                print(
                    f"Card Error: {e}"
                )

        browser.close()

    return jobs