from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    url = 'https://internshala.com/internships/machine-learning-internship/'
    page.goto(url, timeout=60000, wait_until='domcontentloaded')
    page.wait_for_timeout(5000)
    print('URL:', page.url)
    print('BODY_SNIPPET:\n', page.locator('body').inner_text()[:2000])
    selectors = ['.individual_internship', '.internship_card', '.internship-item', 'a[href*="/internship/"]', '[data-href*="/internship/"]']
    for sel in selectors:
        try:
            print('SELECTOR', sel, 'COUNT', page.locator(sel).count())
        except Exception as e:
            print('SELECTOR', sel, 'ERR', repr(e))
    browser.close()
