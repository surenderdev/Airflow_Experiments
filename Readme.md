# Airflow_Experiments
# Machine Learning Books Data Pipeline

This is a good starting point for learning to orchestrate data pipelines with Airflow. 
(fetch real data from a e-commerce websites; store it in db and update the db at scheduled intervals)

Intension is to fetch "Machine Learning Books" details from Flipkart and store them in a PostgreSQL database. 
This same template can be generalised for wider applications.

## Purpose
DAG performs the following tasks:
1. Fetches details of machine learning books (Title, Price, Author) from Flipkart.
2. Creates a table in a PostgreSQL database.
3. Inserts the fetched data into the database along with timestamp.

---

## Core Components

### **1. Python Functions**

#### `fetch_books(page)`
- Sends an HTTP GET request to Flipkart's search results page for machine learning books.
- Parses HTML content using `BeautifulSoup` to extract book details:
  - **Title**
  - **Price**
  - **Author**
- Returns a list of books for a given page.

#### `fetch_flipkart_books(num_books, ti)`
- Iteratively calls `fetch_books(page)` until the desired number of books is fetched or pages are exhausted.
- Pushes the collected data to Airflow's XCom for downstream tasks.

#### `insert_book_data(*args, **kwargs)`
- Retrieves book data from XCom.
- Generates SQL `INSERT` statements for the records.

---

### **2. Apache Airflow DAG**

- **Default Arguments:**
  - Owner: `airflow`
  - Retries: 1 (with an 8-minute delay)
  - Start Date: 5th March 2025
  - Schedule: Every 2 days

- **Tasks:**
  1. `fetch_book_data_task`: Uses the `PythonOperator` to fetch 50 books from Flipkart.
  2. `create_table_task`: SQL task to create a PostgreSQL table `mlbooks` (if not already present).
     - Includes columns for `title`, `price`, `author`, and `created_at` (formatted as `DD/MM/YYYY HH:MM`).
  3. `insert_book_data_task`: Inserts fetched book data into the `mlbooks` table.

---

## DAG Workflow

1. **Fetch Book Data:**
   - Fetches up to 50 machine learning books from Flipkart.

2. **Create PostgreSQL Table:**
   - Creates the `mlbooks` table with the following structure:
     - `id`: Auto-incrementing primary key.
     - `title`: Text (Non-NULL).
     - `price`: Text.
     - `author`: Text.
     - `created_at`: Timestamp (formatted `DD/MM/YYYY HH:MM`).

3. **Insert Book Data into PostgreSQL:**
   - Inserts the book details fetched from Flipkart into the `mlbooks` table.

---

## Technology Stack

- **Python Libraries:**
  - `requests` for HTTP requests
  - `BeautifulSoup` for HTML parsing
- **Apache Airflow:** Workflow orchestration and task scheduling.
- **PostgreSQL:** Database to store book details.

---

## Note

- Make sure the PostgreSQL connection ID `mlbooks_server` is configured in Airflow.
- The script is only meant to be a demonstration of Airflow data pipeline orchestration capability; 
- It is a humble request not to overuse and be respectful of Flipkart's data scraping policies.

