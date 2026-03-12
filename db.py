from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

# sends the data fetched from api to Railway Postgres
# this is a blank template for connecting to the database
# and saving data to it.
engine = create_engine(os.environ["DATABASE_URL"])

# creates a session factory bound to our engine
# each session is a unit of work with the database
Session = sessionmaker(bind=engine)

# test connection with Postgres(the db)
try:
    # test the connection by executing a simple request
    # Note, the importance of with.
    # It closes the connection after the block is executed, preventing connection leaks.
    # also, rename to conn to be more descriptive.
    with engine.connect() as conn:
        # execute a simple query to test the connection
        # return the numner 1
        conn.execute(text("SELECT 1"))
    # if the query executes successfully.
    print("Database connected successful.")
# if there is an error during the connection or query execution
except Exception as e:
    print(f"Database connection failed; {e}")

def create_table():
    """Creates the yelp_reviews table if it doesn't already exist."""
    with engine.begin() as conn:
        conn.execute(text("""CREATE TABLE IF NOT EXISTS yelp_reviews (
               id SERIAL PRIMARY KEY,
               review_id VARCHAR UNIQUE,
               business_id VARCHAR,
               business_name VARCHAR,
               cuisine VARCHAR,
               all_categories TEXT[],
               price VARCHAR,
               transactions TEXT[],
               address VARCHAR,
               city VARCHAR,
               state VARCHAR,
               zip_code VARCHAR,
               country VARCHAR,
               display_address VARCHAR,
               latitude DECIMAL(9,6),
               longitude DECIMAL(9,6),
               phone VARCHAR,
               is_closed BOOLEAN,
               location VARCHAR,
               business_rating NUMERIC(2,1),
               review_rating NUMERIC(2,1),
               review_text VARCHAR,
               review_count INT,
               time_created TIMESTAMP,
               url VARCHAR,
               inserted_at TIMESTAMP DEFAULT NOW()
                          )"""
                          ))
        #save the changes to the database
        print("Table 'yelp_reviews' is ready.")

def save_reviews(reviews: list):
    if not reviews:
        print("No reviews to save.")
        return

    # counters to track saved or skipped reviews
    # might be helpful for debugging or logging purposes.
    saved = 0
    skipped = 0

    # create a session instead of engine.begin()
    # this allows us to rollback individual failed inserts
    # without breaking the entire transaction
    session = Session()

    try:
        for review in reviews:
            try:
                session.execute(text("""
                    INSERT INTO yelp_reviews (
                        review_id, business_id, business_name,
                        cuisine, all_categories, price, transactions,
                        address, city, state, zip_code, country, display_address,
                        latitude, longitude, phone, is_closed, location,
                        business_rating, review_rating, review_text,
                        review_count, time_created, url
                    ) VALUES (
                        :review_id, :business_id, :business_name,
                        :cuisine, :all_categories, :price, :transactions,
                        :address, :city, :state, :zip_code, :country, :display_address,
                        :latitude, :longitude, :phone, :is_closed, :location,
                        :business_rating, :review_rating, :review_text,
                        :review_count, :time_created, :url
                    ) ON CONFLICT (review_id) DO NOTHING
                """), review)
                # commit after each successful insert
                session.commit()
                saved += 1
            except Exception as e:
                # rollback the failed insert so the session can continue
                # without this, one failure breaks all subsequent inserts
                session.rollback()
                print(f"Failed to save review {review.get('review_id')}: {e}")
                skipped += 1
    finally:
        # always close the session to prevent connection leaks
        session.close()

    # commit the transaction after processing all reviews
    print(f"Saved {saved} reviews. Skipped {skipped} reviews due to errors.")