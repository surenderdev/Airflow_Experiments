from datetime import datetime, timedelta
from airflow import DAG
import requests
from bs4 import BeautifulSoup
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.operators.python import PythonOperator, get_current_context

# Define headers to mimic a browser
HEADERS = {
    "Referer": "https://www.flipkart.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
}

# Function to fetch books from Flipkart
def fetch_books(page):
    url = f"https://www.flipkart.com/search?q=machine+learning+books&sid=bks&page={page}"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Error fetching URL:", e)
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    
    # Search for title, price, and author elements using Flipkart's class names
    title_elements = soup.find_all("a", class_="wjcEIp")
    price_elements = soup.find_all("div", class_="Nx9bqj")
    author_elements = soup.find_all("div", class_="NqpwHC")

    books = []
    if title_elements and price_elements and author_elements:
        for title, price, author in zip(title_elements, price_elements, author_elements):
            book = {
                "Title": title.get_text(strip=True),
                "Price": price.get_text(strip=True),
                "Author": author.get_text(strip=True)
            }
            books.append(book)
    
    return books

# Python function to fetch multiple pages of books
def fetch_flipkart_books(num_books, ti):
    all_books = []
    page = 1

    while len(all_books) < num_books:
        books = fetch_books(page)
        if not books:
            break
        all_books.extend(books)
        page += 1

    if len(all_books) < num_books:
        print(f"Only {len(all_books)} books found. Unable to fetch {num_books} books.")
    else:
        all_books = all_books[:num_books]

    print(f"Fetched a total of {len(all_books)} books.")
    ti.xcom_push(key='book_data', value=all_books)

# Python function to generate SQL statements and pass them to the SQL operator
def insert_book_data(*args, **kwargs):
    context = get_current_context()
    ti = context['ti']
    records = ti.xcom_pull(task_ids='fetch_mlbooks_data', key='book_data')
    
    if not records:
        print("No data to insert. Exiting task.")
        return []

    sql_statements = [
        f"""
        INSERT INTO mlbooks (title, price, author, created_at)
        VALUES (
            '{record["Title"].replace("'", "''")}', 
            '{record["Price"].replace("'", "''")}', 
            '{record["Author"].replace("'", "''")}',
            to_char(NOW(), 'DD/MM/YYYY HH24:MI')
        );
        """
        for record in records
    ]
    print(f"Generated {len(sql_statements)} SQL statements.")
    return sql_statements

# Default DAG arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 3, 5),
    'retries': 1,
    'retry_delay': timedelta(minutes=8),
}

# Define the DAG
dag = DAG(
    'mlbooksdb_flipkart',
    default_args=default_args,
    description='Fetch machine learning book data from Flipkart and store it in Postgres with fresh data on top',
    schedule_interval=timedelta(days=2),
)

# Task 1: Fetch Book Data
fetch_book_data_task = PythonOperator(
    task_id='fetch_mlbooks_data',
    python_callable=fetch_flipkart_books,
    op_args=[50],  # Number of books to fetch
    provide_context=True,
    dag=dag,
)

# Task 2: Create Table in Postgres
create_table_task = SQLExecuteQueryOperator(
    task_id='create_table',
    sql="""
    CREATE TABLE IF NOT EXISTS mlbooks (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        price TEXT,
        author TEXT,
        created_at TEXT DEFAULT to_char(CURRENT_TIMESTAMP, 'DD/MM/YYYY HH24:MI')
    );
    """,
    conn_id='mlbooks_server',
    dag=dag,
)

# Task 3: Insert Data into Postgres
insert_book_data_task = SQLExecuteQueryOperator(
    task_id='insert_book_data',
    sql=insert_book_data,
    conn_id='mlbooks_server',
    dag=dag,
)

# Set task dependencies
fetch_book_data_task >> create_table_task >> insert_book_data_task
