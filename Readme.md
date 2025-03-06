# Machine Learning Books Data Pipeline with Airflow

This is a good starting point for learning to orchestrate data pipelines with Airflow. 
(fetch real data from a e-commerce websites; store it in db and update the db at scheduled intervals)

Intension is to fetch "Machine Learning Books" details from Flipkart and store them in a PostgreSQL database. 
This same template can be generalised for wider applications.

## Purpose
Airflow DAG performs the following tasks:
1. Fetches details of machine learning books (Title, Price, Author) from Flipkart.
2. Creates a table in a PostgreSQL database.
3. Inserts the fetched data into the database along with timestamp.

---

## Instructions

Follow these steps to set up the project on your local machine:

1. Clone this repository:
    ```bash
    git clone https://github.com/your-repo/project-name.git
    ```
2. Navigate to the project directory:
    ```bash
    cd project-name
    ```
3. Build and start the services using Docker Compose:
    ```bash
    docker-compose up
    ```

---

### Running the Project
1. Access the **Airflow Webserver** at: [http://localhost:8080](http://localhost:8080)  
   **Credentials**:
   - **Username**: `airflow`
   - **Password**: `airflow`

2. Access the **pgAdmin Webserver** at: [http://localhost:5050](http://localhost:5050)  
   **Credentials**:
   - **Username**: `admin@admin.com`
   - **Password**: `root`

### Inside pgAdmin
- Create a new server and configure it:
  - **Name**: `mlbooks_server`
  - **Hostname**: `172.18.0.3`  
    *(Get this from Docker container inspection: `docker container inspect <postgres-container>`)*
    *(you may as well use Docker Destop, check containers "flipkart_booksdb-postgres-1", 
      "postgres:13" served on port"5432:5432",  inspect tab and check for IP address)
  - **Port**: `5432`
  - **Database**: `postgres`
  - **Username**: `airflow`
  - **Password**: `airflow`

- Rightclick on mlbooks_server to Create a new database: `mlbooks`

---


### Configure Airflow to Connect to PostgreSQL:
1. In the Airflow Webserver, go to:
   **Admin > Connections > Add Connection**.
2. Fill in the following details:
   - **Connection ID**: `mlbooks_server`
   - **Connection Type**: `Postgres`
   - **Host**: `172.18.0.3`
   - **Database**: `mlbooks`
   - **Login**: `airflow`
   - **Password**: `airflow`
   - **Port**: `5432`
3. Save the connection.

### Run the DAG
1. Navigate to the **DAGs** page in Airflow.
2. Trigger the DAG: `mlbooksdb_flipkart`.
3. Monitor the tasks and ensure they execute successfully.

---

## Core Components of DAG [dags/buildmlbooks.py]

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

