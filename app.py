from flask import Flask, request, jsonify
from flask_cors import CORS
from scrape import main, FlightsEncoder
import logging
import json

# Set DEBUG Flag
DEBUG = True

# Initial setup
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s: %(message)s')

@app.route('/', methods=['POST'])
def index():
    """
    Search for Flights.
    """
    # Only accept POST Methods
    if request.method != 'POST':
        return f'{request.method} not allowed', 405

    # Read the POST data
    app.logger.info('POST request to /')
    data = request.get_json()
    app.logger.info(f'POST Data: {json.dumps(data)}')

    # Search for the Flights
    app.logger.info(f'Searching for flights...')
    flights = main(data, debug=DEBUG)
    app.logger.info(f'Flights:\n\n{flights}')

    return jsonify(
        message=json.dumps(flights, cls=FlightsEncoder),
        status=200
    )

if __name__ == "__main__":
    app.run(debug=DEBUG, host='0.0.0.0', port=80)
