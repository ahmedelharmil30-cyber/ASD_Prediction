"""Static fallback data — mirrors frontend/lib/constants.ts exactly.

Used to render the form immediately, before/without a successful call to
GET /metadata. The backend's AQ10_ITEMS in app/core/model_loader.py stays
the single source of truth; this is just a fallback.
"""

AQ10_ITEMS_FALLBACK = [
    "I often notice small sounds when others do not.",
    "I usually concentrate more on the whole picture, rather than the small details.",
    "I find it easy to do more than one thing at once.",
    "If there is an interruption, I can switch back to what I was doing very quickly.",
    "I find it easy to 'read between the lines' when someone is talking to me.",
    "I know how to tell if someone listening to me is getting bored.",
    "When I'm reading a story, I find it difficult to work out the characters' intentions.",
    "I like to collect information about categories of things (e.g. types of car, bird, train).",
    "I find it easy to work out what someone is thinking or feeling just by looking at their face.",
    "I find it difficult to work out people's intentions.",
]

ETHNICITIES = [
    "White-European",
    "Asian",
    "Black",
    "Hispanic",
    "Latino",
    "Middle Eastern",
    "Pasifika",
    "South Asian",
    "Turkish",
    "Others",
]

RELATIONS = [
    "Self",
    "Parent",
    "Relative",
    "Health care professional",
    "Others",
]

COUNTRIES = [
    "Afghanistan", "Albania", "American Samoa", "Angola", "Anguilla", "Argentina", "Armenia", "Aruba",
    "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Belgium", "Bhutan",
    "Bolivia", "Brazil", "Bulgaria", "Burundi", "Canada", "Chile", "China", "Comoros", "Costa Rica",
    "Croatia", "Cyprus", "Czech Republic", "Ecuador", "Egypt", "Ethiopia", "Europe", "Finland", "France",
    "Georgia", "Germany", "Ghana", "Greenland", "Hong Kong", "Iceland", "India", "Indonesia", "Iran",
    "Iraq", "Ireland", "Isle of Man", "Italy", "Japan", "Jordan", "Kazakhstan", "Kuwait", "Latvia",
    "Lebanon", "Libya", "Malaysia", "Malta", "Mexico", "Nepal", "Netherlands", "New Zealand", "Nicaragua",
    "Niger", "Nigeria", "Norway", "Oman", "Others", "Pakistan", "Philippines", "Portugal", "Qatar",
    "Romania", "Russia", "Saudi Arabia", "Serbia", "Sierra Leone", "South Africa", "South Korea", "Spain",
    "Sri Lanka", "Sweden", "Syria", "Tonga", "Turkey", "U.S. Outlying Islands", "Ukraine",
    "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Vietnam",
]

HISTORY_SESSION_KEY = "asd_screening_history_v1"
