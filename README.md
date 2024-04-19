# Southwest Airlines Generative AI Agent

A Generative AI Agent that is able to obtain Southwest Airlines flight information. This was built using [Erik-Debye@](https://github.com/Erik-Debye)'s [SWA-Scraper GitHub Repository](https://github.com/Erik-Debye/SWA-Scraper) as inspiration.

## Product Demo

TODO

## How it Works

It is powered by Streamlit (UI), Amazon Bedrock - Claude 3 Sonnet (Cloud), pyppeteer (Web Scraping), Flask (Web API) and LangChain (LLM Framework). When you ask the Southwest Airlines Generative AI Agent a question like `Hello can you please find me flights from San Diego to Dallas on April 22nd, 2024 for 1 adult passenger?` it will perform the following steps:

1. It will process the input text and identify the correct `Tool` to use (in this case the Search Southwest Flights Tool).
2. It will use the `Tool` by formatting the input parameters to the tool and then invoking it. In this case the input format is a JSON encoded string and the `Tool` is an API request to a Flask Backend server.
3. The Flask API is executed and the Southwest Airlines Flight page is scraped, parsed and the results are returned as a JSON-encoded string.
4. The Agent then processes this returned JSON-encoded string and formulates a response.

## How to Run the Program

```bash
# Set up the virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run the Streamlit App to run the UI
streamlit run southwest_agent.py

# Run the Flask App Server
python app.py
```

## Testing

```bash
# Curl command to test the Flask API
curl -H 'Content-Type: application/json' \
      -d '{"departure_date": "2024-04-22", "origination": "SAN", "destination": "DAL", "passenger_count": 1, "adult_count": 1}' \
      -X POST \
      http://127.0.0.1
```

## Bugs

1. Sometimes the scraping process fails as the script is detected as a bot. There isn't an easy workaround for this right now.
2. Implement this with OpenAI as Claude is not available to non-enterprise users.

## Product Vision

1. Integrate with Southwest's APIs rather than scraping their webpage.
2. Allow the Agent to book flights on behalf of you.

## WARNING & DISCLAIMER:

DO NOT USE THE DATA YOUR SCRAPE FOR COMMERCIAL PURPOSES OR TO MAKE MONEY IN ANY WAY. THE DEVELOPER DOES NOT ATTAIN ANY RESPONSIBILTY FOR YOUR USE OF THE PROGRAM.
