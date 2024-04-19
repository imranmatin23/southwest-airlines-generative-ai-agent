# Southwest Airlines Agent

A Generative AI Agent that is able to obtain Southwest Airlines flight information.


## Testing

```
curl -H 'Content-Type: application/json' \
      -d '{"departure_date": "2024-04-22", "origination": "SAN", "destination": "DAL", "passenger_count": 1, "adult_count": 1}' \
      -X POST \
      http://127.0.0.1
```