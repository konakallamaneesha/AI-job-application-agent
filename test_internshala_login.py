from playwright.sync_api import sync_playwright

with sync_playwright() as p:

    context = p.chromium.launch_persistent_context(
        user_data_dir="internshala_profile",
        channel="chrome",
        headless=False
    )

    page = context.new_page()

    page.goto("https://internshala.com")

    print("Current URL:", page.url)

    input("Check if already logged in and press ENTER...")

    context.close()