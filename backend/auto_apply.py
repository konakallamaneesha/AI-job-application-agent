from playwright.sync_api import sync_playwright


def auto_apply(
    job_url,
    resume_path
):

    result = {

        "status": "ready_for_confirmation",

        "questions": []

    }

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        page = browser.new_page()

        print(
            "Opening Job Page..."
        )

        page.goto(
            job_url,
            timeout=60000,
            wait_until="domcontentloaded"
        )

        page.wait_for_timeout(
            5000
        )

        # Click Apply Now

        try:

            page.locator(
                "text=Apply now"
            ).first.click()

            print(
                "Apply clicked"
            )

            page.wait_for_timeout(
                5000
            )

        except Exception as e:

            print(
                f"Apply failed: {e}"
            )

            result["status"] = "apply_failed"

            browser.close()

            return result

        # Upload Resume

        try:

            file_inputs = page.locator(
                "input[type='file']"
            )

            if file_inputs.count() > 0:

                file_inputs.first.set_input_files(
                    resume_path
                )

                print(
                    "Resume Uploaded"
                )

                page.wait_for_timeout(
                    3000
                )

        except Exception as e:

            print(
                f"Resume Upload Failed: {e}"
            )

        # Availability Question

        try:

            if page.get_by_text(
                "Yes, I am available to join immediately"
            ).count() > 0:

                page.get_by_text(
                    "Yes, I am available to join immediately"
                ).click()

                print(
                    "Availability Selected"
                )

        except:

            pass

        # Detect Additional Questions

        try:

            textareas = page.locator(
                "textarea"
            )

            for i in range(
                textareas.count()
            ):

                try:

                    question = textareas.nth(
                        i
                    ).evaluate(
                        """
                        el => {
                            const label =
                            el.closest('div')
                            ?.innerText;

                            return label;
                        }
                        """
                    )

                    if (
                        question
                        and
                        len(question) > 10
                    ):

                        result[
                            "questions"
                        ].append(
                            question
                        )

                except:

                    pass

        except:

            pass

        if len(
            result["questions"]
        ) > 0:

            result[
                "status"
            ] = "questions_found"

            browser.close()

            return result

        print(
            "No additional questions found"
        )

    result["status"] = "ready_for_confirmation"    

    return result