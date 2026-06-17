from playwright.sync_api import sync_playwright


def _normalize_text(value):

    if value is None:

        return ""

    return " ".join(
        str(value)
        .replace("\n", " ")
        .split()
    )


def _is_internal_internshala_field(label):

    text = label.lower()

    return any(
        marker in text
        for marker in (
            "confirm_availability",
            "notice_period",
            "last_working_date",
            "custom_question_",
            "link"
        )
    )


def _extract_label(element):

    try:

        text = element.evaluate(
            """
            (el) => {
                const clean = (value) => (value || '').replace(/\s+/g, ' ').trim();
                const isInternal = (value) => {
                    const text = clean(value).toLowerCase();
                    return /confirm_availability|notice_period|last_working_date|custom_question_|\blink\b/.test(text);
                };
                const isVisible = (node) => {
                    if (!node) return false;
                    const style = window.getComputedStyle(node);
                    if (style.display === 'none' || style.visibility === 'hidden') return false;
                    const rect = node.getBoundingClientRect();
                    return rect.width > 0 || rect.height > 0;
                };
                const textOf = (node) => clean(node?.innerText || node?.textContent || '');

                const labels = Array.from(el.labels || [])
                    .map((label) => ({ node: label, text: textOf(label) }))
                    .filter((entry) => entry.text && !isInternal(entry.text));

                if (labels.length > 0) {
                    return labels[0].text;
                }

                let previousLabel = null;
                let current = el.previousElementSibling;

                while (current) {
                    if (current.matches && current.matches('label')) {
                        previousLabel = textOf(current);
                        break;
                    }
                    current = current.previousElementSibling;
                }

                if (previousLabel && !isInternal(previousLabel)) {
                    return previousLabel;
                }

                const questionContainer = el.closest('.question-heading, .question-container, div, form, section, article, li, fieldset');

                if (questionContainer) {
                    const questionHeading = questionContainer.querySelector('.question-heading');
                    if (questionHeading && isVisible(questionHeading)) {
                        const headingText = textOf(questionHeading);
                        if (headingText && !isInternal(headingText)) {
                            return headingText;
                        }
                    }

                    const questionBody = questionContainer.querySelector('.question-container');
                    if (questionBody && isVisible(questionBody)) {
                        const bodyText = textOf(questionBody);
                        if (bodyText && !isInternal(bodyText)) {
                            return bodyText;
                        }
                    }
                }

                const parent = el.closest('div, form, section, article, li, fieldset');

                if (parent) {
                    const lines = Array.from(parent.querySelectorAll('label, .question-heading, .question-container'))
                        .map((node) => textOf(node))
                        .filter(Boolean)
                        .filter((line) => line.length < 160)
                        .filter((line) => !isInternal(line))
                        .filter((line) => !/^(yes|no|male|female|other|select|choose|upload|file)$/i.test(line));

                    if (lines.length > 0) {
                        return lines[0];
                    }

                    const parentLines = textOf(parent)
                        .split(/\n+/)
                        .map((line) => clean(line))
                        .filter(Boolean)
                        .filter((line) => line.length < 160)
                        .filter((line) => !isInternal(line))
                        .filter((line) => !/^(yes|no|male|female|other|select|choose|upload|file)$/i.test(line));

                    if (parentLines.length > 0) {
                        return parentLines[0];
                    }
                }

                const ariaLabel = clean(el.getAttribute('aria-label'));

                if (ariaLabel && !isInternal(ariaLabel)) return ariaLabel;

                return '';
            }
            """
        )

        label = _normalize_text(text)

        if label and not _is_internal_internshala_field(label):

            return label

    except Exception:

        pass

    if hasattr(element, "label") and element.label:

        label = _normalize_text(element.label)

        if label and not _is_internal_internshala_field(label):

            return label

    if hasattr(element, "get_attribute"):

        for attr in (
            "aria-label",
        ):

            value = element.get_attribute(attr)

            if value:

                label = _normalize_text(value)

                if label and not _is_internal_internshala_field(label):

                    return label

    return ""


def _extract_options(page, element, field_type, scope=None):

    if field_type == "select":

        if hasattr(element, "options") and isinstance(element.options, list):

            return [
                _normalize_text(option)
                for option in element.options
                if _normalize_text(option)
            ]

        try:

            options = element.evaluate(
                """
                (el) => Array.from(el.options)
                    .map(option => option.text.trim())
                    .filter(Boolean)
                """
            )

            return [
                _normalize_text(option)
                for option in options
            ]

        except Exception:

            return []

    if field_type == "radio":

        radio_name = None

        if hasattr(element, "get_attribute"):

            radio_name = element.get_attribute("name")

        if not radio_name:

            try:

                radio_name = element.evaluate(
                    "(el) => el.name"
                )

            except Exception:

                radio_name = None

        if radio_name:

            group = (
                scope.locator(
                    f"input[type='radio'][name='{radio_name}']"
                )
                if scope is not None
                else page.locator(
                    f"input[type='radio'][name='{radio_name}']"
                )
            )

            options = []

            for index in range(group.count()):

                option = group.nth(index)

                label = _extract_label(option)

                if label and label not in options:

                    options.append(label)

            return options

    return []


def _find_question_scope(page):

    if hasattr(page, "_additional_questions_scope"):

        return page._additional_questions_scope

    try:

        questions_container = page.locator(".questions-container")

        if questions_container.count() == 0:

            return None

        container_html = questions_container.first.inner_html()

        if not _normalize_text(container_html):

            return None

        return questions_container

    except Exception:

        return None


def _collect_form_fields(page):

    selectors = [
        ("textarea", "textarea"),
        ("text", "input[type='text']"),
        ("number", "input[type='number']"),
        ("url", "input[type='url']"),
        ("email", "input[type='email']"),
        ("select", "select"),
        ("radio", "input[type='radio']"),
        ("checkbox", "input[type='checkbox']")
    ]

    scope = _find_question_scope(page)

    questions = []

    try:

        form_html = page.locator("form").inner_html()

        print("===== FORM HTML =====")
        print(form_html)
        print("===== END =====")

    except Exception:

        print("===== FORM HTML =====")
        print("<form not found>")
        print("===== END =====")

    for field_type, selector in selectors:

        locator = scope.locator(selector) if scope else page.locator(selector)

        for index in range(locator.count()):

            element = locator.nth(index)

            try:

                if hasattr(element, "is_visible") and not element.is_visible():

                    continue

            except Exception:

                pass

            try:

                if hasattr(element, "evaluate") and not element.evaluate("(el) => !el.hidden && !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length)"):

                    continue

            except Exception:

                pass

            label = _extract_label(element)

            if not label:

                continue

            if _is_internal_internshala_field(label):

                continue

            print("LABEL:", label)
            print("TYPE:", field_type)

            question = {
                "label": label,
                "type": field_type
            }

            options = _extract_options(page, element, field_type, scope)

            if options:

                question["options"] = options

            questions.append(question)

    deduped = []
    seen = set()

    for question in questions:

        key = (
            question["label"].lower(),
            question["type"]
        )

        if key not in seen:

            seen.add(key)
            deduped.append(question)

    return deduped


def _fill_question_answers(page, questions, answers):

    if not questions or not answers:

        return

    selectors = [
        ("textarea", "textarea"),
        ("text", "input[type='text']"),
        ("number", "input[type='number']"),
        ("url", "input[type='url']"),
        ("email", "input[type='email']"),
        ("select", "select"),
        ("radio", "input[type='radio']"),
        ("checkbox", "input[type='checkbox']")
    ]

    for question in questions:

        label = _normalize_text(question.get("label", ""))

        if not label:

            continue

        answer = answers.get(question.get("label"))

        if answer is None:

            answer = answers.get(label)

        if answer is None:

            continue

        for field_type, selector in selectors:

            locator = page.locator(selector)

            for index in range(locator.count()):

                element = locator.nth(index)

                element_label = _normalize_text(_extract_label(element))

                if element_label != label:

                    continue

                try:

                    if field_type in ("textarea", "text", "number", "url", "email"):

                        element.fill(str(answer))

                    elif field_type == "select":

                        element.select_option(str(answer))

                    elif field_type == "radio":

                        if isinstance(answer, bool):

                            if answer:

                                element.check()

                        else:

                            try:

                                if str(element.get_attribute("value")).strip().lower() == str(answer).strip().lower():

                                    element.check()

                                else:

                                    option_text = _normalize_text(element.evaluate("(el) => el.nextElementSibling?.textContent || ''"))

                                    if option_text and _normalize_text(option_text) == _normalize_text(str(answer)):

                                        element.check()

                            except Exception:

                                element.check()

                    elif field_type == "checkbox":

                        if answer in (True, "true", "yes", "1"):

                            element.check()

                        else:

                            element.uncheck()

                    break

                except Exception as exc:

                    print(f"Failed to fill question '{label}': {exc}")

                    break


def submit_application(job_url, resume_path=None, questions=None, answers=None):

    print("Launching fresh Playwright session")
    print("Using saved Internshala profile")

    if not job_url:

        return {
            "status": "submit_failed",
            "error": "Missing job URL"
        }

    try:

        with sync_playwright() as playwright:

            context = playwright.chromium.launch_persistent_context(
                user_data_dir="internshala_profile",
                channel="chrome",
                headless=False
            )

            page = context.pages[0] if context.pages else context.new_page()

            print("Opening stored job URL")
            page.goto(
                job_url,
                timeout=60000,
                wait_until="domcontentloaded"
            )

            page.wait_for_timeout(5000)

            if _looks_like_login_page(page):

                context.close()

                return {
                    "status": "submit_failed",
                    "error": "Login required"
                }

            try:

                apply_selectors = [
                    "text=Apply now",
                    "text=Apply Now",
                    "text=/Apply now/i",
                    "text=/Apply Now/i",
                    "a:has-text('Apply')",
                    "button:has-text('Apply')",
                    "[aria-label*='Apply']",
                    "[data-testid*='apply']"
                ]

                apply_button = None

                for selector in apply_selectors:

                    locator = page.locator(selector)

                    if locator.count() > 0:

                        apply_button = locator.first

                        break

                if apply_button is None:

                    page.locator("button").filter(has_text="Apply").first.click()

                else:

                    apply_button.click()

                page.wait_for_timeout(5000)

            except Exception as exc:

                print(f"Apply step failed: {exc}")

            try:

                file_inputs = page.locator("input[type='file']")

                if file_inputs.count() > 0 and resume_path:

                    file_inputs.first.set_input_files(resume_path)

                    page.wait_for_timeout(3000)

            except Exception as exc:

                print(f"Resume upload failed: {exc}")

            try:

                if page.get_by_text("Yes, I am available to join immediately").count() > 0:

                    page.get_by_text("Yes, I am available to join immediately").click()

                    print("Availability selected")

            except Exception as exc:

                print(f"Availability selection failed: {exc}")

            try:

                _fill_question_answers(page, questions, answers)

            except Exception as exc:

                print(f"Question filling failed: {exc}")

            before_url = page.url

            submit_selectors = [
                "#submit",
                "input[type='submit']",
                "input[value='Submit']",
                "button:has-text('Submit')"
            ]

            submit_clicked = False

            for selector in submit_selectors:

                try:

                    locator = page.locator(selector)

                    if locator.count() == 0:

                        continue

                    submit_btn = locator.first

                    if hasattr(submit_btn, "is_visible") and not submit_btn.is_visible():

                        continue

                    print("Submit button found")
                    submit_btn.click()
                    submit_clicked = True
                    print("Submit button clicked")

                    break

                except Exception as exc:

                    print(f"Submit selector failed for {selector}: {exc}")

            if not submit_clicked:

                context.close()

                return {
                    "status": "submit_failed"
                }

            page.wait_for_timeout(5000)

            after_url = page.url

            body_text = page.locator("body").inner_text().lower()

            success_markers = (
                "application submitted",
                "applied successfully",
                "already applied"
            )

            if (
                any(marker in body_text for marker in success_markers)
                or after_url != before_url
                or page.locator("text=/application submitted|applied successfully|already applied/i").count() > 0
            ):

                context.close()

                return {
                    "status": "submitted"
                }

            context.close()

            return {
                "status": "submit_failed"
            }

    except Exception as exc:

        print(f"Submit application failed: {exc}")

        return {
            "status": "submit_failed",
            "error": str(exc)
        }


def _looks_like_login_page(page):

    url = page.url.lower()

    body_text = (
        page.locator("body")
        .inner_text()
        .lower()
    )

    markers = [
        "/login",
        "/sign-up",
        "login",
        "sign up",
        "continue with google",
        "continue with email",
        "student login"
    ]

    return any(
        marker in url
        or marker in body_text
        for marker in markers
    )


def auto_apply(
    job_url,
    resume_path
):

    result = {

        "status": "ready_for_confirmation",

        "questions": []

    }

    playwright = None
    context = None

    try:

        print("Opening Job Page")

        playwright = sync_playwright().start()

        context = playwright.chromium.launch_persistent_context(
            user_data_dir="internshala_profile",
            channel="chrome",
            headless=False
        )

        print("Using Chrome Profile")
        print("Session loaded")

        page = (
            context.pages[0]
            if context.pages
            else context.new_page()
        )

        print("Current URL:", page.url)

        page.goto(
            job_url,
            timeout=60000,
            wait_until="domcontentloaded"
        )

        logged_in = not _looks_like_login_page(page)

        print("Logged In:", logged_in)

        page.wait_for_timeout(
            5000
        )

        print("Current URL:", page.url)

        if _looks_like_login_page(page):

            print("Login detected")
            print("Current URL:", page.url)

            result["status"] = "login_required"

            return result

        print("Before Apply URL:", page.url)

        try:

            apply_selectors = [
                "text=Apply now",
                "text=Apply Now",
                "text=/Apply now/i",
                "text=/Apply Now/i",
                "a:has-text('Apply')",
                "button:has-text('Apply')",
                "[aria-label*='Apply']",
                "[data-testid*='apply']"
            ]

            apply_button = None

            for selector in apply_selectors:

                locator = page.locator(selector)

                if locator.count() > 0:

                    apply_button = locator.first

                    break

            if apply_button is None:

                page.locator("button").filter(has_text="Apply").first.click()

            else:

                apply_button.click()

            print("Apply Button Clicked")
            print("After Apply URL:", page.url)
            print("Page Title:", page.title())

            body = page.locator("body").inner_text()

            print(body[:2000])

            page.wait_for_timeout(
                5000
            )

            print("Current URL:", page.url)

        except Exception as e:

            print(
                f"Apply failed: {e}"
            )

            result["status"] = "apply_failed"

            return result

        if _looks_like_login_page(page):

            print("Login detected")
            print("Current URL:", page.url)

            result["status"] = "login_required"

            return result

        print("Resume Upload Started")

        try:

            file_inputs = page.locator(
                "input[type='file']"
            )

            if file_inputs.count() > 0:

                file_inputs.first.set_input_files(
                    resume_path
                )

                print("Resume Upload Completed")

                page.wait_for_timeout(
                    3000
                )

        except Exception as e:

            print(
                f"Resume Upload Failed: {e}"
            )

        try:

            if page.get_by_text(
                "Yes, I am available to join immediately"
            ).count() > 0:

                page.get_by_text(
                    "Yes, I am available to join immediately"
                ).click()

                print("Availability Selected")

        except Exception:

            pass

        try:

            page.wait_for_timeout(
                3000
            )

            try:

                page.locator(
                    "text=/Additional question\\(s\\)/i"
                ).first.wait_for(
                    timeout=10000
                )

            except Exception:

                pass

            questions_container = page.locator(".questions-container")

            if questions_container.count() == 0:

                result["status"] = "ready_for_confirmation"

                return result

            container_html = questions_container.first.inner_html()

            if not _normalize_text(container_html):

                result["status"] = "ready_for_confirmation"

                print("Questions Count:", 0)

                return result

            questions = _collect_form_fields(page)

            print("=== QUESTIONS DETECTED ===")

            for question in questions:

                print("Detected Question:", question.get("label"))
                print("Field Type:", question.get("type"))
                print("Options:", question.get("options", []))

            print("==========================")
            print("Questions Found")
            print("Questions Count:", len(questions))

            if questions:

                result["questions"] = questions
                result["status"] = "questions_found"

                return result

        except Exception as e:

            print(
                f"Question detection failed: {e}"
            )

        print("No additional questions found")

    finally:

        if result["status"] not in ("login_required", "questions_found", "ready_for_confirmation"):

            if context is not None:

                try:

                    context.close()

                except Exception:

                    pass

            if playwright is not None:

                try:

                    playwright.stop()

                except Exception:

                    pass

    result["status"] = "ready_for_confirmation"

    return result