import json
import random
from datetime import datetime, timedelta
import uuid

# Seed for reproducibility
random.seed(42)

# Common data for both stores (to enable comparisons)
authors = [
    "Stephen King", "J.K. Rowling", "George Orwell", "Agatha Christie", 
    "Ernest Hemingway", "Jane Austen", "Mark Twain", "Charles Dickens",
    "Virginia Woolf", "F. Scott Fitzgerald", "Harper Lee", "Toni Morrison",
    "Gabriel García Márquez", "Margaret Atwood", "Ray Bradbury", "Isaac Asimov",
    "Ursula K. Le Guin", "Philip K. Dick", "Arthur C. Clarke", "Douglas Adams",
    "Neil Gaiman", "Terry Pratchett", "Brandon Sanderson", "Patrick Rothfuss",
    "Andy Weir", "Liu Cixin", "Becky Chambers", "Martha Wells"
]

# Store A uses single genre, Store B uses multiple categories
genres_store_a = [
    "Fiction", "Science Fiction", "Fantasy", "Mystery", "Romance", 
    "Thriller", "Horror", "Biography", "History", "Philosophy",
    "Self-Help", "Business", "Technology", "Art", "Travel"
]

categories_store_b = [
    ["Fiction", "Literary Fiction"], ["Science Fiction", "Hard SF"],
    ["Fantasy", "Epic Fantasy"], ["Mystery", "Crime Fiction"],
    ["Romance", "Contemporary Romance"], ["Thriller", "Suspense"],
    ["Horror", "Supernatural"], ["Biography", "Memoir"],
    ["History", "World History"], ["Philosophy", "Ethics"],
    ["Self-Help", "Personal Development"], ["Business", "Entrepreneurship"],
    ["Technology", "Programming"], ["Art", "Visual Arts"], ["Travel", "Adventure"]
]

# Book titles and descriptions
books_data = [
    {
        "title": "The Martian",
        "author": "Andy Weir",
        "genre": "Science Fiction",
        "categories": ["Science Fiction", "Hard SF"],
        "description": "An astronaut becomes stranded on Mars and must figure out how to survive until rescue arrives.",
        "summary": "Stranded astronaut uses science and ingenuity to survive on Mars in this thrilling tale of human resilience.",
        "isbn": "978-0553418026",
        "publication_year": 2011,
        "publisher": "Crown Publishing"
    },
    {
        "title": "1984",
        "author": "George Orwell",
        "genre": "Fiction",
        "categories": ["Fiction", "Dystopian"],
        "description": "A dystopian social science fiction novel about totalitarian control and surveillance.",
        "summary": "Winston Smith navigates a totalitarian society where Big Brother watches everyone in this classic dystopian masterpiece.",
        "isbn": "978-0451524935",
        "publication_year": 1949,
        "publisher": "Signet Classics"
    },
    {
        "title": "Harry Potter and the Sorcerer's Stone",
        "author": "J.K. Rowling",
        "genre": "Fantasy",
        "categories": ["Fantasy", "Young Adult"],
        "description": "A young boy discovers he's a wizard and enters a magical world of spells and adventures.",
        "summary": "Eleven-year-old Harry Potter discovers his magical heritage and begins his journey at Hogwarts School.",
        "isbn": "978-0439708180",
        "publication_year": 1997,
        "publisher": "Scholastic"
    },
    {
        "title": "The Murder of Roger Ackroyd",
        "author": "Agatha Christie",
        "genre": "Mystery",
        "categories": ["Mystery", "Crime Fiction"],
        "description": "Hercule Poirot investigates the murder of a wealthy man in a small English village.",
        "summary": "Detective Hercule Poirot unravels a complex murder mystery with an unexpected twist ending.",
        "isbn": "978-0062073563",
        "publication_year": 1926,
        "publisher": "William Morrow"
    },
    {
        "title": "Pride and Prejudice",
        "author": "Jane Austen",
        "genre": "Romance",
        "categories": ["Romance", "Classic Literature"],
        "description": "A witty exploration of love, marriage, and social class in 19th-century England.",
        "summary": "Elizabeth Bennet navigates love and social expectations in this beloved romantic classic.",
        "isbn": "978-0141439518",
        "publication_year": 1813,
        "publisher": "Penguin Classics"
    },
    {
        "title": "The Shining",
        "author": "Stephen King",
        "genre": "Horror",
        "categories": ["Horror", "Supernatural"],
        "description": "A writer's descent into madness while caretaking an isolated hotel during winter.",
        "summary": "Jack Torrance's psychological breakdown at the haunted Overlook Hotel threatens his family.",
        "isbn": "978-0307743657",
        "publication_year": 1977,
        "publisher": "Doubleday"
    },
    {
        "title": "Dune",
        "author": "Frank Herbert",
        "genre": "Science Fiction",
        "categories": ["Science Fiction", "Space Opera"],
        "description": "Epic tale of politics, religion, and ecology on the desert planet Arrakis.",
        "summary": "Paul Atreides navigates political intrigue and mystical powers on the spice-rich planet Dune.",
        "isbn": "978-0441172719",
        "publication_year": 1965,
        "publisher": "Ace Books"
    },
    {
        "title": "The Hobbit",
        "author": "J.R.R. Tolkien",
        "genre": "Fantasy",
        "categories": ["Fantasy", "Adventure"],
        "description": "A hobbit's unexpected journey to help dwarves reclaim their mountain home.",
        "summary": "Bilbo Baggins embarks on an adventure with dwarves to reclaim the Lonely Mountain from a dragon.",
        "isbn": "978-0547928227",
        "publication_year": 1937,
        "publisher": "Houghton Mifflin"
    },
    {
        "title": "Atomic Habits",
        "author": "James Clear",
        "genre": "Self-Help",
        "categories": ["Self-Help", "Personal Development"],
        "description": "A practical guide to building good habits and breaking bad ones.",
        "summary": "Evidence-based strategies for forming habits that stick and achieving remarkable results.",
        "isbn": "978-0735211292",
        "publication_year": 2018,
        "publisher": "Avery"
    },
    {
        "title": "Sapiens",
        "author": "Yuval Noah Harari",
        "genre": "History",
        "categories": ["History", "Anthropology"],
        "description": "A brief history of humankind from the Stone Age to the present.",
        "summary": "Exploration of how Homo sapiens came to dominate Earth through cognitive, agricultural, and scientific revolutions.",
        "isbn": "978-0062316097",
        "publication_year": 2014,
        "publisher": "Harper"
    },
    {
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "genre": "Fiction",
        "categories": ["Fiction", "Classic Literature"],
        "description": "A critique of the American Dream set in the Jazz Age.",
        "summary": "Nick Carraway observes the tragic story of Jay Gatsby's pursuit of love and the American Dream.",
        "isbn": "978-0743273565",
        "publication_year": 1925,
        "publisher": "Scribner"
    },
    {
        "title": "To Kill a Mockingbird",
        "author": "Harper Lee",
        "genre": "Fiction",
        "categories": ["Fiction", "Social Issues"],
        "description": "A story of racial injustice and childhood innocence in the American South.",
        "summary": "Scout Finch learns about justice and morality when her father defends a Black man in 1930s Alabama.",
        "isbn": "978-0061120084",
        "publication_year": 1960,
        "publisher": "J.B. Lippincott"
    },
    {
        "title": "The Hitchhiker's Guide to the Galaxy",
        "author": "Douglas Adams",
        "genre": "Science Fiction",
        "categories": ["Science Fiction", "Comedy"],
        "description": "A comedic space adventure following Arthur Dent's journey through the galaxy.",
        "summary": "Arthur Dent's hilarious adventures across the universe after Earth's demolition for a hyperspace bypass.",
        "isbn": "978-0345391803",
        "publication_year": 1979,
        "publisher": "Del Rey"
    },
    {
        "title": "The Alchemist",
        "author": "Paulo Coelho",
        "genre": "Fiction",
        "categories": ["Fiction", "Philosophical"],
        "description": "A shepherd's journey to find treasure teaches him about following his dreams.",
        "summary": "Santiago's quest for treasure becomes a spiritual journey of self-discovery and personal legend.",
        "isbn": "978-0062315007",
        "publication_year": 1988,
        "publisher": "HarperOne"
    },
    {
        "title": "Educated",
        "author": "Tara Westover",
        "genre": "Biography",
        "categories": ["Biography", "Memoir"],
        "description": "A memoir about education as a means of escape from a survivalist family.",
        "summary": "Tara Westover's transformation from isolated childhood to Cambridge PhD through the power of education.",
        "isbn": "978-0399590504",
        "publication_year": 2018,
        "publisher": "Random House"
    },
    {
        "title": "The Power of Now",
        "author": "Eckhart Tolle",
        "genre": "Self-Help",
        "categories": ["Self-Help", "Spirituality"],
        "description": "A guide to spiritual enlightenment through present-moment awareness.",
        "summary": "Transform your life by learning to live fully in the present moment and transcend negative thinking.",
        "isbn": "978-1577314806",
        "publication_year": 1997,
        "publisher": "New World Library"
    },
    {
        "title": "Project Hail Mary",
        "author": "Andy Weir",
        "genre": "Science Fiction",
        "categories": ["Science Fiction", "Space Exploration"],
        "description": "A lone astronaut must save humanity from extinction.",
        "summary": "Ryland Grace awakens on a spaceship with no memory, discovering he's humanity's last hope against extinction.",
        "isbn": "978-0593135204",
        "publication_year": 2021,
        "publisher": "Ballantine Books"
    },
    {
        "title": "The Seven Husbands of Evelyn Hugo",
        "author": "Taylor Jenkins Reid",
        "genre": "Fiction",
        "categories": ["Fiction", "Historical Fiction"],
        "description": "A reclusive Hollywood icon finally tells her life story to a young journalist.",
        "summary": "Aging Hollywood star Evelyn Hugo reveals the truth about her glamorous and scandalous life.",
        "isbn": "978-1501139239",
        "publication_year": 2017,
        "publisher": "Atria Books"
    },
    {
        "title": "Klara and the Sun",
        "author": "Kazuo Ishiguro",
        "genre": "Science Fiction",
        "categories": ["Science Fiction", "Literary Fiction"],
        "description": "An artificial friend observes human nature with extraordinary insight.",
        "summary": "Klara, an artificial friend, watches the world from a store window and later serves a sick child.",
        "isbn": "978-0593318171",
        "publication_year": 2021,
        "publisher": "Knopf"
    },
    {
        "title": "Becoming",
        "author": "Michelle Obama",
        "genre": "Biography",
        "categories": ["Biography", "Politics"],
        "description": "The former First Lady's deeply personal memoir.",
        "summary": "Michelle Obama's journey from Chicago's South Side to the White House and beyond.",
        "isbn": "978-1524763138",
        "publication_year": 2018,
        "publisher": "Crown"
    }
]

def generate_store_a_data(num_books=50):
    """Generate Store A dataset"""
    store_a_books = []
    
    # Use all predefined books
    for i, book in enumerate(books_data):
        store_a_book = {
            "book_id": f"BKA_{1000 + i}",
            "title": book["title"],
            "author": book["author"],
            "genre": book["genre"],
            "price": round(random.uniform(8.99, 29.99), 2),
            "rating": round(random.uniform(3.0, 5.0), 1),
            "description": book["description"],
            "isbn": book["isbn"],
            "publication_year": book["publication_year"]
        }
        store_a_books.append(store_a_book)
    
    # Generate additional books to reach num_books
    for i in range(len(books_data), num_books):
        store_a_book = {
            "book_id": f"BKA_{1000 + i}",
            "title": f"Book Title {i + 1}",
            "author": random.choice(authors),
            "genre": random.choice(genres_store_a),
            "price": round(random.uniform(8.99, 29.99), 2),
            "rating": round(random.uniform(3.0, 5.0), 1),
            "description": f"An engaging {random.choice(genres_store_a).lower()} novel that explores themes of adventure, mystery, and human nature.",
            "isbn": f"978-{random.randint(1000000000, 9999999999)}",
            "publication_year": random.randint(1950, 2023)
        }
        store_a_books.append(store_a_book)
    
    return store_a_books

def generate_store_b_data(num_books=50):
    """Generate Store B dataset with some overlapping books but different schemas"""
    store_b_books = []
    
    # Use predefined books with some price variations and different field names
    for i, book in enumerate(books_data):
        # Add some price variation and occasionally higher/lower prices
        base_price = random.uniform(7.99, 31.99)
        if random.random() < 0.3:  # 30% chance of being cheaper than Store A
            price_multiplier = random.uniform(0.8, 0.95)
        elif random.random() < 0.2:  # 20% chance of being more expensive
            price_multiplier = random.uniform(1.05, 1.2)
        else:
            price_multiplier = random.uniform(0.95, 1.05)
        
        store_b_book = {
            "product_id": f"AMZN_{random.randint(100000000, 999999999)}",
            "book_name": book["title"],
            "writer": book["author"],
            "category": book["categories"],
            "cost": round(base_price * price_multiplier, 2),
            "reviews_count": random.randint(10, 5000),
            "summary": book["summary"],
            "publisher": book.get("publisher", "Unknown Publisher"),
            "stock": random.randint(0, 100)
        }
        store_b_books.append(store_b_book)
    
    # Generate additional books
    for i in range(len(books_data), num_books):
        genre_pair = random.choice(categories_store_b)
        store_b_book = {
            "product_id": f"AMZN_{random.randint(100000000, 999999999)}",
            "book_name": f"Book Title {i + 1}",
            "writer": random.choice(authors),
            "category": genre_pair,
            "cost": round(random.uniform(7.99, 31.99), 2),
            "reviews_count": random.randint(10, 5000),
            "summary": f"A compelling {genre_pair[0].lower()} story that captivates readers with its unique perspective and engaging narrative.",
            "publisher": random.choice(["Penguin", "Random House", "HarperCollins", "Simon & Schuster", "Macmillan"]),
            "stock": random.randint(0, 100)
        }
        store_b_books.append(store_b_book)
    
    return store_b_books

# Generate datasets
print("Generating Store A dataset...")
store_a_data = generate_store_a_data(50)

print("Generating Store B dataset...")
store_b_data = generate_store_b_data(50)

# Save datasets
with open('data/store_a_books.json', 'w', encoding='utf-8') as f:
    json.dump(store_a_data, f, indent=2, ensure_ascii=False)

with open('data/store_b_books.json', 'w', encoding='utf-8') as f:
    json.dump(store_b_data, f, indent=2, ensure_ascii=False)

print(f"\nDatasets generated successfully!")
print(f"Store A: {len(store_a_data)} books")
print(f"Store B: {len(store_b_data)} books")

# Display sample data
print("\n" + "="*50)
print("STORE A SAMPLE:")
print("="*50)
for i in range(3):
    book = store_a_data[i]
    print(f"Book ID: {book['book_id']}")
    print(f"Title: {book['title']}")
    print(f"Author: {book['author']}")
    print(f"Genre: {book['genre']}")
    print(f"Price: ${book['price']}")
    print(f"Rating: {book['rating']}/5.0")
    print(f"Description: {book['description'][:100]}...")
    print("-" * 30)

print("\n" + "="*50)
print("STORE B SAMPLE:")
print("="*50)
for i in range(3):
    book = store_b_data[i]
    print(f"Product ID: {book['product_id']}")
    print(f"Book Name: {book['book_name']}")
    print(f"Writer: {book['writer']}")
    print(f"Category: {book['category']}")
    print(f"Cost: ${book['cost']}")
    print(f"Reviews Count: {book['reviews_count']}")
    print(f"Summary: {book['summary'][:100]}...")
    print(f"Stock: {book['stock']}")
    print("-" * 30)

# Generate analysis for query demonstrations
print("\n" + "="*60)
print("DATASET ANALYSIS FOR QUERY DEMONSTRATIONS")
print("="*60)

# 1. Genre popularity analysis
store_a_genres = {}
for book in store_a_data:
    genre = book['genre']
    store_a_genres[genre] = store_a_genres.get(genre, 0) + 1

store_b_categories = {}
for book in store_b_data:
    for category in book['category']:
        store_b_categories[category] = store_b_categories.get(category, 0) + 1

print("\n1. GENRE POPULARITY:")
print("Store A - Top 5 Genres:")
for genre, count in sorted(store_a_genres.items(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"  {genre}: {count} books")

print("\nStore B - Top 5 Categories:")
for category, count in sorted(store_b_categories.items(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"  {category}: {count} books")

# 2. Price comparison
store_a_avg_price = sum(book['price'] for book in store_a_data) / len(store_a_data)
store_b_avg_price = sum(book['cost'] for book in store_b_data) / len(store_b_data)

print(f"\n2. PRICE COMPARISON:")
print(f"Store A average price: ${store_a_avg_price:.2f}")
print(f"Store B average price: ${store_b_avg_price:.2f}")
print(f"Price difference: ${abs(store_a_avg_price - store_b_avg_price):.2f}")

# 3. Common books for comparison
common_titles = set()
store_a_titles = {book['title']: book for book in store_a_data}
store_b_titles = {book['book_name']: book for book in store_b_data}

print(f"\n3. OVERLAPPING BOOKS FOR PRICE COMPARISON:")
print("Title | Store A Price | Store B Price | Difference")
print("-" * 60)
for title in store_a_titles:
    if title in store_b_titles:
        a_price = store_a_titles[title]['price']
        b_price = store_b_titles[title]['cost']
        diff = b_price - a_price
        print(f"{title[:25]:<25} | ${a_price:>6.2f} | ${b_price:>6.2f} | ${diff:>6.2f}")

# 4. Sample queries for demonstration
print(f"\n4. SAMPLE QUERIES TO DEMONSTRATE:")
print("="*40)
print("Query 1: 'Find me books about space exploration'")
print("  - Should match: The Martian, Project Hail Mary, Dune")
print("  - Tests: Semantic search across descriptions")

print("\nQuery 2: 'What are the most popular genres in each store?'")
print("  - Tests: Schema mapping (genre vs category) + aggregation")

print("\nQuery 3: 'Which store has better prices for science fiction books?'")
print("  - Tests: Cross-store comparison + genre filtering")

print("\nQuery 4: 'Find highly rated books under $15'")
print("  - Tests: Multi-criteria filtering across different schemas")

print("\nQuery 5: 'Compare Andy Weir book prices between stores'")
print("  - Tests: Author matching + price comparison")

print(f"\n5. SCHEMA MAPPING CHALLENGES:")
print("="*40)
print("- title (A) ↔ book_name (B)")
print("- author (A) ↔ writer (B)")
print("- genre (A) ↔ category (B) [single string vs array]")
print("- price (A) ↔ cost (B)")
print("- rating (A) ↔ reviews_count (B) [different rating systems]")
print("- description (A) ↔ summary (B)")

print("\nDatasets are ready for RAG system testing!")