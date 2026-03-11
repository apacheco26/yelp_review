from fetcher import fetch_all
from db import create_table, save_reviews
from dotenv import load_dotenv
load_dotenv()
import os, sys

print("Starting main.py")
print("API key present?", os.getenv("YELP_API_KEY") is not None, file=sys.stderr)

def main():
    print("Starting data fetching process...")

    # Check API key before doing anything
    api_key = os.getenv("YELP_API_KEY")
    if not api_key:
        print("ERROR: YELP_API_KEY not found!", file=sys.stderr)
        return
    print("YELP_API_KEY found", file=sys.stderr)

    # Create DB table
    create_table()
    print("Database table ready")

    # This prevents long jobs failing silently 
    # feedback in the terminal is crucial for debugging and monitoring.
    try:
        reviews = fetch_all()
        print(f"Fetched {len(reviews)} reviews")
    except Exception as e:
        print("Error fetching reviews:", e, file=sys.stderr)
        return

    save_reviews(reviews)
    print("Job completed successfully!")


# means that this code will only run if this file is executed directly, 
# and not when it is imported as a module in another file.
if __name__ == "__main__":
    main()

# Other wordsif someone ever imports something from main.py into another file, 
# it won't accidentally trigger the entire fetch job just from being imported.