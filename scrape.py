"""
Tutorial: https://github.com/Erik-Debye/SWA-Scraper/blob/main/javascript%20modules/scraper.js

NOTE: Does not assume multiple pages of flights!
"""

import asyncio
from pyppeteer import launch
from pyppeteer_stealth import stealth
from pyppeteer import launch
from bs4 import BeautifulSoup
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

class Flights():
    """
    A collection of flights. This class is useful for aggregate data analysis.
    """
    def __init__(
        self, 
        departure_date,
        origination_airport,
        destination_airport,
        passenger_count,
        adult_count,
        flights=None
    ):
        self.departure_date = departure_date
        self.origination_airport = origination_airport
        self.destination_airport = destination_airport
        self.passenger_count = passenger_count
        self.adult_count = adult_count
        self.flights = flights

    def compute_cheapest_flight(self):
        """
        Compute the cheapest flight.
        """
        return min([min(flight.prices) for flight in self.flights])

    def __str__(self):
        """
        Print the flights.
        """
        output = ""

        output += f"Departure Date: {self.departure_date}\n"
        output += f"Origination Airport: {self.origination_airport}\n"
        output += f"Destination Airport: {self.origination_airport}\n"
        output += f"Passenger Count: {self.passenger_count}\n"
        output += f"Adult Count: {self.adult_count}\n"
        output += f"Total Flights Available: {len(self.flights)}\n"
        output += f"Cheapest Flight Price: {self.compute_cheapest_flight()}\n"
        output += f"\n\n"

        for flight in self.flights:
            output += str(flight)

        return output

class Flight():
    """
    A flight.
    """
    def __init__(
        self,
        departure_date,
        origination_airport,
        destination_airport,
        passenger_count,
        adult_count,
        html
    ):
        """
        Initialize the fields of a filght.
        """
        self.departure_date = departure_date
        self.origination_airport = origination_airport
        self.destination_airport = destination_airport
        self.passenger_count = passenger_count
        self.adult_count = adult_count
        self.flight_number = self.parse_flight_number(html)
        self.fastest = self.parse_fastest(html)
        self.number_of_stops = self.parse_number_of_stops(html)
        self.change_planes = self.parse_change_planes(html)
        self.departure_time = self.parse_departure_time(html)
        self.arrival_time = self.parse_arrival_time(html)
        self.duration = self.parse_duration(html)
        self.prices = self.parse_prices(html)
        self.seats_left = self.parse_seats_left(html)

    def parse_flight_number(self, html):
        """
        Parse the flight number.
        """
        return html.find_all("div")[0].find_all("span")[0].text
    
    def parse_fastest(self, html):
        """
        Parse if the flight is label as fastest.

        If the flight is label as fastest, it will have 3 spans, where the 3rd is the label.
        """
        return len(html.find_all("div")[0].find_all("span")) == 3
    
    def parse_number_of_stops(self, html):
        """
        Parse the number of stops.
        """
        return html.find('div', {'class': 'select-detail--number-of-stops'}).find('div', {'class': 'flight-stops-badge select-detail--flight-stops-badge'}).text
    
    def parse_change_planes(self, html):
        """
        Parse whether the flight changes planes.
        """
        if html.find('div', {'class': 'select-detail--number-of-stops'}).find('div', {'class': 'select-detail--change-planes'}) is not None:
            return html.find('div', {'class': 'select-detail--number-of-stops'}).find('div', {'class': 'select-detail--change-planes'}).text
        return "N/A"
    
    
    def parse_departure_time(self, html):
        """
        Parse the departure time.
        """
        return html.find_all("div")[3].find_all("span")[0].text

    def parse_arrival_time(self, html):
        """
        Parse the arrival time.
        """
        return html.find_all("div")[4].find_all("span")[0].text
    
    def parse_duration(self, html):
        """
        Parse the duration.
        """
        return html.find_all("div")[7].text
    
    def parse_prices(self, html):
        """
        Parse the prices.
        Array Indicies: [Business Select, Anytime, Wanna Get Away Plus, Wanna Get Away]
        """
        prices = []

        for data_test in ['fare-button--business-select', 'fare-button--anytime', 'fare-button--wanna-get-away-plus', 'fare-button--wanna-get-away']:
            if html.find('div', {'class': 'select-detail--fares'}).find('div', {"data-test": data_test}).find('span', {"class": "swa-g-screen-reader-only"}) is not None:
                prices.append("$" + html.find('div', {'class': 'select-detail--fares'}).find('div', {"data-test": data_test}).find('span', {"class": "swa-g-screen-reader-only"}).text)
            else:
                prices.append("Unavailable")

        return prices

    def parse_seats_left(self, html):
        """
        Parse the seats left.

        Array Indicies: [Business Select, Anytime, Wanna Get Away Plus, Wanna Get Away]
        """
        seats_left = []

        for data_test in ['fare-button--business-select', 'fare-button--anytime', 'fare-button--wanna-get-away-plus', 'fare-button--wanna-get-away']:
            if html.find('div', {'class': 'select-detail--fares'}).find('div', {"data-test": data_test}).find('span', {"class": "seats-left-indicator-text"}) is not None:
                seats_left.append("$" + html.find('div', {'class': 'select-detail--fares'}).find('div', {"data-test": data_test}).find('span', {"class": "seats-left-indicator-text"}).text)
            else:
                seats_left.append("N/A")

        return seats_left
    
    def __str__(self):
        """
        Print the flight.
        """
        output = ""

        output += (
            f"############### Flight Number: {self.flight_number} ############### \n" +
            f"Fastest: {self.fastest}\n" +
            f"Number of Stops: {self.number_of_stops}\n" +
            f"Change Planes: {self.change_planes}\n" +
            f"Departure Time: {self.departure_time}\n" +
            f"Arrival Time: {self.arrival_time}\n" +
            f"Duration: {self.duration}\n"
        )
            
        output += f"Prices:\n"
        for fare_type, price, seats_left in zip(["Business Select", "Anytime", "Wanna Get Away Plus", "Wanna Get Away"], self.prices, self.seats_left):
            output += (
                f"\t{fare_type}: {price} ({seats_left})\n"
            )
        output += f"\n\n"

        return output

def parse_html(flights, html):
    """
    Parse the HTML.
    """
    # Store a list of parsed flights
    parsed_flights = []

    # Initialize HTML parser
    soup = BeautifulSoup(html, "html.parser")

    # Parse each flight in the HTML
    flight_html_list = soup.find('ul', {"id": "air-search-results-matrix-0"}).find_all('li')
    for flight_html in flight_html_list:
        flight = Flight(
            flights.departure_date,
            flights.origination_airport,
            flights.destination_airport,
            flights.passenger_count,
            flights.adult_count,
            flight_html
            )
        parsed_flights.append(flight)

    # Store the parsed flights
    flights.flights = parsed_flights

async def extract_html(url):
    """
    Extract the HTML from the URL.
    """
    # Get Random User Agent String.
    software_names = [SoftwareName.CHROME.value]
    operating_systems = [OperatingSystem.MAC_OS_X.value, OperatingSystem.LINUX.value]       
    user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
    random_user_agent = user_agent_rotator.get_random_user_agent()

    # Launch the Browser    
    browser = await launch(
        headless=True,
        args=[
            '--start-maximized',
            f'--user-agent={random_user_agent}',
            '--disable-extensions'
        ]
    )

    # Open a new page
    page = await browser.newPage()

    # Add stealth plugin
    await stealth(page)

    # Go to the URL
    await page.goto(url)

    # Press the Search Button on the booking page
    if page.url != url:
        await page.waitForSelector('button[id="form-mixin--submit-button"]')
        link = await page.querySelector('button[id="form-mixin--submit-button"]')
        await link.click()

    # Extract the HTML
    html = await page.content()
    
    # Close the browser window
    await browser.close()

    # Write HTML for debugging
    with open("debug.html", "w") as f:
        f.write(html)

    return html

def construct_url(event):
    """
    Construct the Southwest URL to scrape.
    """
    departure_date = event['departure_date']
    origination = event['origination']
    destination = event['destination']
    passenger_count = event['passenger_count']
    adult_count = event['adult_count']
    url = f"https://www.southwest.com/air/booking/select-depart.html?adultPassengersCount={passenger_count}&adultsCount={adult_count}&departureDate={departure_date}&departureTimeOfDay=ALL_DAY&destinationAirportCode={destination}&fareType=USD&from={origination}&int=HOMEQBOMAIR&originationAirportCode={origination}&passengerType=ADULT&reset=true&returnDate=&returnTimeOfDay=ALL_DAY&to={destination}&tripType=oneway"
    return url

def main(event):
    # Initialize the flights object
    flights = Flights(
        event['departure_date'],
        event['origination'],
        event['destination'],
        event['passenger_count'],
        event['adult_count'],
    )

    # Construct the URL to parse
    url = construct_url(event)

    # Extract the HTML
    html = asyncio.get_event_loop().run_until_complete(extract_html(url))
    
    # Parse the HTML to extract the flight information
    parse_html(flights, html)
    
    # Return the flights
    print(flights)

if __name__ == '__main__':
    event = {
        "departure_date": "2024-04-22",
        "origination": "SAN",
        "destination": "DAL",
        "passenger_count": 1,
        "adult_count": 1
    }

    main(event)
