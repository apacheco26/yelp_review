from fetcher import fetch_all
from db import create_table, save_reviews
from dotenv import load_dotenv
load_dotenv()
import os, sys

print("Starting main.py")
print("API key present?", os.getenv("YELP_API_KEY") is not None, file=sys.stderr)

def main():
    print("Starting data fetching process...")

    # creeate the database tables if they don't exist
    create_table()

    reviews = fetch_all()
    
    save_reviews(reviews)

    print("job completed successfully!")

# means that this code will only run if this file is executed directly, 
# and not when it is imported as a module in another file.
if __name__ == "__main__":
    main()

# Other wordsif someone ever imports something from main.py into another file, 
# it won't accidentally trigger the entire fetch job just from being imported.