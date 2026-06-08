from playwright.sync_api import sync_playwright

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    page = browser.new_page()

    page.goto(
        "https://in.indeed.com/jobs?q=frontend+developer"
    )

    page.wait_for_timeout(5000)

    card = page.locator(
        "[data-testid='slider_item']"
    ).first

    card.click()

    page.wait_for_timeout(5000)

    print(
        page.locator("body").inner_text()
    )

    input(
        "Press Enter to close..."
    )

    browser.close()