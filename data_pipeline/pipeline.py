import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
import re
import os


print("Starting scrape...")

# Now We target 3 categories to ensure above 60 books
CATEGORIES = {
    "Sequential Art": "https://books.toscrape.com/catalogue/category/books/sequential-art_5/",
    "Mystery": "https://books.toscrape.com/catalogue/category/books/mystery_3/",
    "Historical Fiction": "https://books.toscrape.com/catalogue/category/books/historical-fiction_4/"
}

scraped_data = []

for cat_name, base_url in CATEGORIES.items():
    page_num = 1
    while True:
        # books.toscrape.com pagination logic: index.html then page-2.html
        page_url = f"{base_url}index.html" if page_num == 1 else f"{base_url}page-{page_num}.html"
        response = requests.get(page_url)
        
        if response.status_code != 200:
            break # Reached the end of the category pages
            
        soup = BeautifulSoup(response.text, 'html.parser')
        books = soup.find_all('article', class_='product_pod')
        
        if not books:
            break
            
        for book in books:
            title = book.find('h3').find('a')['title']
            price_text = book.find('p', class_='price_color').text
            star_rating_class = book.find('p', class_='star-rating')['class'][1]
            availability_text = book.find('p', class_='instock availability').text.strip()
            
            scraped_data.append({
                'title': title,
                'price': price_text,
                'star_rating': star_rating_class,
                'availability': availability_text,
                'category': cat_name
            })
        page_num += 1

print(f"Scraped {len(scraped_data)} books total.")

print("Cleaning the messy Data via using pandas")
df = pd.DataFrame(scraped_data)

# Now we Extract numeric price using regex and cast to float
df['price_gbp'] = df['price'].apply(lambda x: float(re.search(r'\d+\.\d+', x).group()) if pd.notnull(x) else None)

# Map text ratings into integers
rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
df['rating'] = df['star_rating'].map(rating_map)

# Parse availability to boolean (0 or 1)
df['in_stock'] = df['availability'].str.contains('In stock', case=False, na=False)

# Drop missing/messy rows 
df.dropna(subset=['price_gbp', 'rating', 'title'], inplace=True)

# Now we Convert GBP to INR using fixed project baseline
GBP_TO_INR_RATE = 105.50
df['price_inr'] = df['price_gbp'] * GBP_TO_INR_RATE

# Keep only the cleaned columns needed for DB
df_clean = df[['title', 'price_gbp', 'price_inr', 'rating', 'in_stock', 'category']].copy()
df_clean['rating'] = df_clean['rating'].astype(int)
df_clean['in_stock'] = df_clean['in_stock'].astype(int) 

print('-'*30)
print("Loading Data into DataBase\n")
db_name = 'books_catalog.db'
if os.path.exists(db_name):
    os.remove(db_name) # Start fresh

conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# Create normalized schema
cursor.executescript("""
CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT UNIQUE
);

CREATE TABLE books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    price_gbp REAL,
    price_inr REAL,
    rating INTEGER,
    in_stock INTEGER,
    category_id INTEGER REFERENCES categories(category_id)
);
""")

# Inserting the values categories
categories_df = pd.DataFrame(df_clean['category'].unique(), columns=['category_name'])
categories_df.to_sql('categories', conn, if_exists='append', index=False)
# Fetch mapped category_ids
cat_map_df = pd.read_sql("SELECT * FROM categories", conn)
category_to_id = dict(zip(cat_map_df.category_name, cat_map_df.category_id))
# Map category_id onto books df, drop text category, and insert
df_clean['category_id'] = df_clean['category'].map(category_to_id)
books_df_db = df_clean.drop(columns=['category'])
books_df_db.to_sql('books', conn, if_exists='append', index=False)

print("\nData loaded into normalized SQLite database.\n")

print("'-"*30)
print("SQL QUERIES & PANDAS EQUIVALENCE\n")


queries = {
    "1. SELECT/WHERE & LIMIT (Top 3 most expensive books)": 
        "SELECT title, price_gbp FROM books WHERE in_stock = 1 ORDER BY price_gbp DESC LIMIT 3;",
        
    "2. DISTINCT (Find distinct ratings available)": 
        "SELECT DISTINCT rating FROM books ORDER BY rating;",
        
    "3. IN (Books with top ratings)": 
        "SELECT title, rating FROM books WHERE rating IN (4, 5) LIMIT 3;",
        
    "4. BETWEEN (Books in specific INR price range)": 
        "SELECT title, price_inr FROM books WHERE price_inr BETWEEN 2000 AND 3000 LIMIT 3;",
        
    "5. JOIN (Books with their category names)": 
        """
        SELECT c.category_name, b.title, b.rating 
        FROM books b 
        JOIN categories c ON b.category_id = c.category_id 
        WHERE b.rating = 5 
        ORDER BY c.category_name 
        LIMIT 5;
        """
}

# Execute and print all SQL Queries
print("--- EXECUTING SQL QUERIES ---")
for desc, query in queries.items():
    print(f"\n{desc}")
    print(pd.read_sql(query, conn))

# Validate JOIN using Pandas
print("\n--- VALIDATING JOIN (PANDAS VS SQL) ---")
# 1. Read SQL result back into pandas (Requirement)
sql_join_result = pd.read_sql(queries["5. JOIN (Books with their category names)"], conn)

# 2. Perform same logic entirely in memory with Pandas merge (Requirement)
books_raw = pd.read_sql("SELECT * FROM books", conn)
categories_raw = pd.read_sql("SELECT * FROM categories", conn)

# pd.merge equivalent
merged = pd.merge(books_raw, categories_raw, on='category_id')
pandas_join_result = merged[merged['rating'] == 5][['category_name', 'title', 'rating']]
pandas_join_result = pandas_join_result.sort_values(by='category_name').head(5).reset_index(drop=True)

print("\nSQL Output:")
print(sql_join_result)
print("\nPandas pd.merge() Output:")
print(pandas_join_result)

conn.close()
print("\nPipeline execution complete.")