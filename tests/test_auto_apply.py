import unittest
from unittest.mock import patch

import backend.auto_apply as auto_apply
from backend.auto_apply import _collect_form_fields, _extract_label, _is_internal_internshala_field, submit_application


class FakeElement:
    def __init__(self, tag_name, label, field_type="text", options=None, placeholder=None, visible=True):
        self.tag_name = tag_name
        self.label = label
        self.field_type = field_type
        self.options = options or []
        self.placeholder = placeholder
        self.visible = visible

    def is_visible(self):
        return self.visible


class FakeLocator:
    def __init__(self, elements, selector=None):
        self.selector = selector
        if selector is None:
            self._elements = list(elements)
        else:
            self._elements = [el for el in elements if self._matches(el, selector)]

    def _matches(self, element, selector):
        if selector is None:
            return True

        for clause in selector.split(','):
            text = clause.strip().lower()

            if text == 'textarea':
                if element.tag_name == 'textarea':
                    return True
                continue

            if text in ("input[type='text']", 'input[type="text"]'):
                if element.field_type == 'text':
                    return True
                continue

            if text in ("input[type='number']", 'input[type="number"]'):
                if element.field_type == 'number':
                    return True
                continue

            if text in ("input[type='url']", 'input[type="url"]'):
                if element.field_type == 'url':
                    return True
                continue

            if text in ("input[type='email']", 'input[type="email"]'):
                if element.field_type == 'email':
                    return True
                continue

            if text == 'select':
                if element.tag_name == 'select':
                    return True
                continue

            if text in ("input[type='radio']", 'input[type="radio"]'):
                if element.field_type == 'radio':
                    return True
                continue

            if text in ("input[type='checkbox']", 'input[type="checkbox"]'):
                if element.field_type == 'checkbox':
                    return True

        return False

    def count(self):
        return len(self._elements)

    def nth(self, index):
        return self._elements[index]

    def is_visible(self):
        return all(getattr(element, "visible", True) for element in self._elements)

    def locator(self, selector):
        if not self.selector:
            return FakeLocator([el for el in self._elements if self._matches(el, selector)], selector)
        return FakeLocator([el for el in self._elements if self._matches(el, selector)], selector)


class FakeSection:
    def __init__(self, elements):
        self._elements = elements

    def locator(self, selector):
        return FakeLocator(self._elements, selector)


class FakePage:
    def __init__(self):
        self._elements = {
            ".questions-container": [
                FakeElement("textarea", "Why should we hire you?", "textarea"),
                FakeElement("input", "Current city", "text"),
                FakeElement("input", "Graduation year", "number"),
                FakeElement("input", "Portfolio URL", "url"),
                FakeElement("input", "Email address", "email"),
                FakeElement("select", "Preferred mode", "select", ["Online", "Offline"]),
                FakeElement("input", "Availability", "radio", ["Full-time", "Part-time"]),
                FakeElement("input", "Accept terms", "checkbox"),
            ],
            "textarea": [FakeElement("textarea", "Why should we hire you?", "textarea")],
            "input[type='text']": [FakeElement("input", "Current city", "text")],
            "input[type='number']": [FakeElement("input", "Graduation year", "number")],
            "input[type='url']": [FakeElement("input", "Portfolio URL", "url")],
            "input[type='email']": [FakeElement("input", "Email address", "email")],
            "select": [FakeElement("select", "Preferred mode", "select", ["Online", "Offline"])],
            "input[type='radio']": [FakeElement("input", "Availability", "radio", ["Full-time", "Part-time"])],
            "input[type='checkbox']": [FakeElement("input", "Accept terms", "checkbox")],
        }

    def locator(self, selector):
        if selector == ".questions-container":
            return FakeLocator(self._elements[".questions-container"], selector)
        return FakeLocator(self._elements.get(selector, []), selector)


class FakeSubmitButton:
    def __init__(self, selector, clicked=False):
        self.selector = selector
        self.clicked = clicked

    def click(self):
        self.clicked = True

    def is_visible(self):
        return True


class FakeSubmitLocator:
    def __init__(self, elements):
        self._elements = list(elements)

    def count(self):
        return len(self._elements)

    def first(self):
        return self._elements[0]


class FakeBodyLocator:
    def __init__(self, text):
        self._text = text

    def inner_text(self):
        return self._text


class FakeSubmitPage:
    def __init__(self):
        self.url = "https://internshala.com/application"
        self._button = FakeSubmitButton("#submit")
        self._locator = FakeSubmitLocator([self._button])

    def locator(self, selector):
        if selector == "#submit":
            return self._locator
        if selector == "input[type='submit']":
            return FakeSubmitLocator([])
        if selector == "input[value='Submit']":
            return FakeSubmitLocator([])
        if selector == "button:has-text('Submit')":
            return FakeSubmitLocator([])
        if selector == "body":
            return FakeBodyLocator("Application submitted successfully")
        return FakeSubmitLocator([])

    def wait_for_timeout(self, _):
        return None


class AutoApplyFieldDetectionTests(unittest.TestCase):
    def test_extract_label_ignores_internal_internshala_identifiers(self):
        internal_labels = [
            "confirm_availability_textarea",
            "custom_question_numeric_10",
            "notice_period",
            "last_working_date",
            "link"
        ]

        for label in internal_labels:
            with self.subTest(label=label):
                self.assertTrue(_is_internal_internshala_field(label))
                self.assertEqual(_extract_label(FakeElement("input", label, "text")), "")

    def test_collect_form_fields_uses_section_scope_when_present(self):
        section = FakeSection([
            FakeElement("textarea", "Do you have a working laptop and internet?", "textarea"),
            FakeElement("input", "How many months of experience do you have in Full Stack Development?", "number")
        ])

        page = FakePage()
        page._additional_questions_scope = section

        questions = _collect_form_fields(page)

        self.assertEqual([item["label"] for item in questions], [
            "Do you have a working laptop and internet?",
            "How many months of experience do you have in Full Stack Development?"
        ])

    def test_collect_form_fields_returns_structured_question_objects(self):
        page = FakePage()

        questions = _collect_form_fields(page)

        self.assertGreaterEqual(len(questions), 7)

        labels = {item["label"]: item for item in questions}

        self.assertIn("Why should we hire you?", labels)
        self.assertEqual(labels["Why should we hire you?"]["type"], "textarea")

        self.assertIn("Current city", labels)
        self.assertEqual(labels["Current city"]["type"], "text")

        self.assertIn("Graduation year", labels)
        self.assertEqual(labels["Graduation year"]["type"], "number")

        self.assertIn("Portfolio URL", labels)
        self.assertEqual(labels["Portfolio URL"]["type"], "url")

        self.assertIn("Email address", labels)
        self.assertEqual(labels["Email address"]["type"], "email")

        self.assertIn("Preferred mode", labels)
        self.assertEqual(labels["Preferred mode"]["type"], "select")
        self.assertEqual(labels["Preferred mode"]["options"], ["Online", "Offline"])

        self.assertIn("Availability", labels)
        self.assertEqual(labels["Availability"]["type"], "radio")

        self.assertIn("Accept terms", labels)
        self.assertEqual(labels["Accept terms"]["type"], "checkbox")

    def test_collect_form_fields_ignores_internal_internshala_fields(self):
        page = FakePage()
        page._elements["textarea"].append(FakeElement("textarea", "confirm_availability", "textarea"))
        page._elements["textarea"].append(FakeElement("textarea", "notice_period", "textarea"))
        page._elements["textarea"].append(FakeElement("textarea", "last_working_date", "textarea"))

        questions = _collect_form_fields(page)
        labels = {item["label"] for item in questions}

        self.assertNotIn("confirm_availability", labels)
        self.assertNotIn("notice_period", labels)
        self.assertNotIn("last_working_date", labels)

    def test_submit_application_uses_fresh_session(self):
        class FakePlaywright:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            class Chromium:
                def launch_persistent_context(self, **kwargs):
                    return FakeContext()

            chromium = Chromium()

        class FakeContext:
            pages = []

            def close(self):
                return None

            def new_page(self):
                return FakePage()

        class FakePage:
            url = "https://internshala.com/application"

            def goto(self, *args, **kwargs):
                return None

            def wait_for_timeout(self, _):
                return None

            def locator(self, selector):
                return FakeLocator([])

            def get_by_text(self, _):
                return FakeLocator([])

        class FakeLocator:
            def __init__(self, elements):
                self._elements = list(elements)

            def count(self):
                return 0

            def first(self):
                return None

            def inner_text(self):
                return ""

        with patch("backend.auto_apply.sync_playwright", return_value=FakePlaywright()):
            result = submit_application("https://internshala.com/application", "resume.pdf")

        self.assertEqual(result["status"], "submit_failed")


if __name__ == "__main__":
    unittest.main()
