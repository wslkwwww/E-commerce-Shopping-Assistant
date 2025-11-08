# Intelligent E-commerce Shopping Assistant (Dianshan Agent)

This project is an intelligent e-commerce information query Agent system built on Large Language Models (LLM) and the LangChain framework. The system integrates **RAG (Retrieval-Augmented Generation)** technology, utilizing a **FAISS** vector database and the **BGE (BAAI General Embedding)** embedding model to achieve high-quality semantic product search. The backend uses a **MySQL** database and a **Flask** API service, making it a robust, intelligent, and commercially viable solution.

The system can deeply understand users' natural language questions and intelligently perform semantic searches, query product information, and order details.

## Main Features

- **Intelligent Semantic Search**: Users can search for products using vague, conversational descriptions (e.g., "cool tops for summer"), and the system can understand their true intent and return the most relevant products.
- **Order Inquiry**: Users can query the status, amount, logistics, and other details of an order using the order number.
- **Complex Question Understanding**: The system can handle complex questions that combine product and order information (e.g., "What's the current promotion for the headphones in order 12345?").

## Tech Stack

- **Backend Framework**: Flask
- **Database**: MySQL
- **Core Agent Framework**: LangChain
- **RAG Engine**:
  - **Vector Database**: FAISS (Facebook AI Similarity Search)
  - **Embedding Model**: BGE (BAAI General Embedding)
- **Large Language Model (LLM)**: Configurable via the `.env` file, compatible with any model service that follows the OpenAI API format (e.g., LM Studio, Zeabur).
- **Python Libraries**: `mysql-connector-python`, `langchain`, `faiss-cpu`, `sentence-transformers`, etc.

## File Structure

```
.
├── ecommerce_agent/
│   ├── agents/
│   │   ├── access_agent.py   # Access Agent, responsible for understanding and dispatching tasks
│   │   ├── order_agent.py    # Order query tool
│   │   └── product_agent.py  # Product RAG search tool
│   ├── app.py                # Main Flask application file
│   ├── config.py             # Project configuration file
│   ├── mysql_db.py           # MySQL database operations module
│   └── qian.html             # A simple frontend interaction page
├── faiss_index/              # Auto-generated vector index directory
├── download_models.py        # Automated model download and vector index creation script
├── import_csv.py             # Script for batch importing product data
├── new_products.csv          # Sample product data file
├── requirements.txt          # Project dependencies
└── README.md                 # This documentation file
```

---

## Quick Start

### 1. Environment Setup

- **Install MySQL**: Ensure you have a running MySQL database service.
- **Create Database**: Create a new database (e.g., `ecommerce_db`) for this project.
- **Install Python Dependencies**: Open a terminal in the project root directory and run the following command to install all required libraries:
  ```bash
  pip install -r requirements.txt
  ```

### 2. Project Configuration

- **Create Configuration File**: Make a copy of `.env.example` and rename it to `.env`.
- **Edit Configuration File**: Open the newly created `.env` file and fill in the following configurations according to your environment:

  - **Large Language Model (LLM) Configuration**:
    - `BASE_URL`: Your LLM service endpoint.
    - `OPENAI_API_KEY`: Your API key.

  - **MySQL Database Configuration**:
    - `MYSQL_HOST`: Database host address (usually `localhost`).
    - `MYSQL_PORT`: Database port number (default is `3306`).
    - `MYSQL_USER`: Database username.
    - `MYSQL_PASSWORD`: Your database password.
    - `MYSQL_DB`: The name of the database you created for the project.

### 3. Import Product Data

This project provides a script to batch import product data from a CSV file.

- **Prepare Data**: You can use the provided `new_products.csv` as a template.
- **Execute Import**: Run the following command in the terminal:
  ```bash
  python import_csv.py new_products.csv
  ```
  This command will import all product data from `new_products.csv` into your MySQL database.

### 4. Download Models and Create Vector Index

This is the **most critical** step. Run the provided automation script to handle all model downloading and data processing.

In the project root directory, run:
```bash
python download_models.py
```
This script will automatically:
1.  Download the `bge-large-zh-v1.5` embedding model.
2.  Read all product information from your MySQL database.
3.  Vectorize the product information and create a FAISS index, saving it in the `faiss_index` directory.

### 5. Start the Backend Service

Once everything is set up, run the following command to start the Flask backend application:

```bash
python -m ecommerce_agent.app
```

When you see the output `Running on http://0.0.0.0:5000` in your terminal, the backend service has started successfully.

### 6. Make a Query

You can interact with the intelligent assistant in several ways:

- **Using `curl` (Recommended)**: Open a new terminal and use the `curl` command to simulate an API request.
  - **Semantic Search**:
    ```bash
    curl -X POST -H "Content-Type: application/json" -d "{\"question\": \"Are there any cool tops for summer?\"}" http://localhost:5000/api/query
    ```
  - **Order Inquiry**:
    ```bash
    curl -X POST -H "Content-Type: application/json" -d "{\"question\": \"Check order 12345\"}" http://localhost:5000/api/query
    ```

- **Using the Frontend Page**: Open the `ecommerce_agent/qian.html` file directly in your browser, enter your question in the input box, and submit.

---