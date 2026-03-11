import requests
import os
import time

# request is used to make the HTTP calls to the API
# os reads the yelp API key from the environment variable

# key will be saved in a seperate file
# best to keep sensitive information like API keys in a .
YELP_SEARCH_URL = "https://api.yelp.com/v3/businesses/search"
YELP_REVIEWS_URL = "https://api.yelp.com/v3/businesses/{id}/reviews"


key = "YDNundaUGsFjeUktTPSOXmGp0PNDrb8g_ZFLYC-CaCbaN6V9_QDPJO7ZtnztUUimRWXv7fy3kmEuNDf2CVU3O73t5Ml4F81Xz7NryeDlS8rs0V03KS0pUD2zyTCmaXYx"
cities = ["Seattle, WA", "San Francisco, CA", "Portland, OR"]

# per city, since you have limit of 400 calls
search_limit = 50


def search_businesses(city):
    
    headers = {"Authorization": f"Bearer {key}"}

    # url reequest combining all the parameters
    params = {
        "location": city,
        "categories": "restaurants",
        "limit": search_limit
        }
    
    # send the request to the Yelp API with the specified parameters and headers
    # importnat functions here requests.get() 
    # to make the GET request to the API, passing in the URL, headers, and parameters
    response = requests.get(YELP_SEARCH_URL, headers=headers, params=params)

    # its alaways good to check the status code with a print statement.
    print(f"Searching businesses in {city} — Status: {response.status_code}")
    print(f"Rate limit remaining: {response.headers.get('RateLimit-Remaining', 'N/A')}")
    
    # 200 means good connection. Universal code
    if response.status_code != 200:
        # connection will timeout so if so get the error message and print it out
        print(f"Error fetching businesses for {city}: {response.text}")
        return []


    # parse the JSON response to extract the list of businesses. 
    # The .get() method is used to safely access the "businesses" key, 
    # providing an empty list as a default value if the key is not present in the response.
    businesses = response.json().get("businesses", [])
    print(f"Found {len(businesses)} businesses in {city}")

    return businesses


# this function will fetch the reviews for a given business ID.
def fetch_reviews(business_id):
    headers = {"Authorization": f"Bearer {key}"}

    # format the reviews URL with the business ID
    url = YELP_REVIEWS_URL.format(id=business_id)
    
    # send the request to the Yelp API to fetch reviews for the specified business ID
    response = requests.get(url, headers=headers)

    print(f"Fetching reviews for business ID {business_id} — Status: {response.status_code}")
    print(f"Rate limit remaining: {response.headers.get('RateLimit-Remaining', 'N/A')}")
    
    if response.status_code != 200:
        print(f"Error fetching reviews for business ID {business_id}: {response.text}")
        return []
    
    # parse the JSON response to extract the list of reviews. 
    # providing an empty list as a default value if the key is not present in the response.
    reviews = response.json().get("reviews", [])
    print(f"Found {len(reviews)} reviews for business ID {business_id}")
    return reviews

def fetch_all():
    all_businesses = []

    for city in cities:
        # again make print statements to check the progress of the code and to debug if needed.
        print(f"Processing city: {city}")
        
        # call the search_businesses function to get the list of businesses for the current city
        businesses = search_businesses(city)
        
        for business in businesses:
            business_id = business["id"]
            # fetch the reviews for the current business ID by calling the fetch_reviews function
        # Only fetch reviews if the business has reviews
            if business.get("review_count", 0) > 0:
                reviews = fetch_reviews(business_id)
            else:
                reviews = []
                print(f"No reviews available for business ID {business_id}, skipping fetch_reviews.")

            print(f"Storing data for business ID {business_id} with {len(reviews)} reviews")

            for review in reviews:
                all_businesses.append({
                    "review_id": review["id"],
                    "business_id": business["id"],
                    "business_name": business["name"],
                    "cuisine": business["categories"][0]["title"] if business.get("categories") else None,
                    "all_categories": [cat["title"] for cat in business.get("categories", [])],
                    "price": business.get("price"),
                    "transactions": business.get("transactions", []),
                    "address": business["location"].get("address1"),
                    "city": business["location"].get("city"),
                    "state": business["location"].get("state"),
                    "zip_code": business["location"].get("zip_code"),
                    "country": business["location"].get("country"),
                    "display_address": ", ".join(business["location"].get("display_address", [])),
                    "latitude": business["coordinates"].get("latitude"),
                    "longitude": business["coordinates"].get("longitude"),
                    "phone": business.get("phone"),
                    "is_closed": business.get("is_closed"),
                    "location": city,
                    "business_rating": business.get("rating"),
                    "review_rating": review.get("rating"),
                    "review_text": review.get("text"),
                    "review_count": business.get("review_count"),
                    "time_created": review.get("time_created"),
                    "url": review.get("url")
                })

            # delay between API calls
            time.sleep(0.5)

    return all_businesses

if __name__ == "__main__":
    # TESTING ONLY
    test_cities = ["Portland, OR"]
    test_business_limit = 2
    test_review_limit = 1

    all_businesses = []

    for city in test_cities:
        print(f"Testing city: {city}")
        businesses = search_businesses(city)[:test_business_limit]

        for business in businesses:
            business_id = business["id"]

            if business.get("review_count", 0) > 0:
                reviews = fetch_reviews(business_id)[:test_review_limit]
            else:
                reviews = []
                print(f"No reviews available for business {business['name']}")

            for review in reviews:
                all_businesses.append({
                    "review_id": review["id"],
                    "business_id": business["id"],
                    "business_name": business["name"],
                    "review_rating": review.get("rating"),
                    "review_text": review.get("text")
                })

            print(f"Stored {len(reviews)} reviews for {business['name']}")

    print(f"\nTest complete! Total businesses processed: {len(all_businesses)}")
    print(all_businesses)