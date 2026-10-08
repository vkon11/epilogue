"""Map Simplify location strings to the regions the dashboard filters on."""

STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS",
    "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC",
    "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
}
MIDWEST = {"IL", "IN", "IA", "KS", "MI", "MN", "MO", "NE", "ND", "OH", "SD", "WI"}
# Simplify abbreviates a few big metros.
US_ALIASES = {"NYC", "SF", "LA", "South SF", "United States", "USA", "US"}
NYC = {"NYC", "New York", "Brooklyn", "Jersey City", "Hoboken", "Greenwich", "Stamford"}
BAY_AREA = {
    "SF", "South SF", "San Francisco", "San Jose", "Santa Clara", "Mountain View", "Palo Alto", "Sunnyvale",
    "Menlo Park", "Redwood City", "Cupertino", "San Mateo", "Oakland", "Fremont", "Milpitas", "Berkeley",
    "Foster City", "San Bruno", "Emeryville", "Los Gatos",
}
# Regions worth fetching descriptions for (screening costs requests and Firecrawl credits).
FOCUS = ["remote", "midwest", "nyc", "bay_area", "texas"]


def regions(locations):
    found = set()
    for loc in locations:
        parts = [p.strip() for p in loc.split(",")]
        city, state = parts[0], parts[-1]
        if "remote" in loc.lower():
            found.add("remote")
        if city in NYC:
            found.add("nyc")
        if city in BAY_AREA:
            found.add("bay_area")
        if state == "TX" or "Texas" in loc:
            found.add("texas")
        if state in MIDWEST:
            found.add("midwest")
        if state in STATES or city in US_ALIASES or "USA" in loc:
            found.add("us")
    return sorted(found)
