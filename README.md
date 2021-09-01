# Umami Scraper

Google Cloud Function that scrapes a recipe from a URL using Python

## Setup

1. Open Google Cloud Platform console
2. Create new Google Cloud Function
3. Provide function name and set region to `australia-southeast1`
4. Set the trigger to HTTP requiring authentication
5. Set runtime to `Python 3.9`
5. Copy `main.py` and `requirements.py`
6. Set entry point to `scrape`

## Triggering event

`{'url':'https://www.justonecookbook.com/chicken-teriyaki/'}`

## Output

- Uploads recipe data to Firestore under `recipes/{recipe_id}` (note: recipe_id is generated)
- Uploads recipe image to Google Cloud Storage under `images/recipes/{recipe_id}`
- Returns generated `recipe_id` via HTTP response
