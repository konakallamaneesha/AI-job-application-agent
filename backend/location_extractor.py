def extract_location(text):

    cities = [

        "hyderabad",
        "bangalore",
        "bengaluru",
        "chennai",
        "pune",
        "mumbai",
        "delhi",
        "noida",
        "gurgaon",
        "gurugram",
        "kolkata"

    ]

    text = text.lower()

    for city in cities:

        if city in text:
            return city.title()

    return ""