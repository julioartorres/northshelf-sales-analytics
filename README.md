# northshelf-sales-analytics 
## 🛒 E-Commerce Sales Analytics Pipeline
>End-to-end data analytics project using MySQL, Python (pandas), and Power BI to analyze retail transactions and surface business insights through an interactive dashboard.
### 📊 Dashboard Preview

### 🗂 Table of Contents
- [Project Overview](###Project-Overview)
- [Business Questions](###BusinessQuestions)
- [Tech Stack](###TechStack)
- [Project Structure](###ProjectStructure)
- [Data Set](###DataSet)
- [How to Run](###HowtoRun)
- [Key Findings](###KeyFindings)
- [Dashboard Pages](###DashboardPages)
- [Skills Demonstrated](###SkillsDemonstrated)


### Project Overview
This project simulates a real-world retail analytics workflow for a fictional e-commerce company, NorthShelf Retail. 
Raw transactional data was generated, stored in a relational MySQL database, cleaned and transformed in Python, and visualized in a 3-page Power BI dashboard.

The pipeline covers every stage of the analytics process:
Raw CSV Data → MySQL Database → Python Cleaning → Power BI Dashboard

### Business Questions
The dashboard was built to answer three core questions:

1. Which product categories drive the most revenue, and how has that changed month-over-month?
2. Do higher loyalty tiers actually spend more — and by how much?
3. Which regions are underperforming relative to their order volume?

### Tech Stack
Tool Purpose MySQLRelational database, schema design, JOINs, VIEWsPython — pandasData cleaning, null handling, outlier capping, feature engineeringPower BIInteractive dashboard, DAX measures, slicers, drill-throughFaker + NumPySynthetic dataset generation

### Project Structure

northshelf-sales-analytics/
│
├── data/
│   ├── raw/                    # Original generated CSVs
│   │   ├── customers.csv
│   │   ├── products.csv
│   │   ├── orders.csv
│   │   └── order_items.csv
│   └── cleaned/                # Output of clean_data.py
│       ├── customers_clean.csv
│       ├── products_clean.csv
│       ├── orders_clean.csv
│       └── order_items_clean.csv
│
├── sql/
│   ├── create_tables.sql       # Schema: CREATE TABLE statements
│   └── analysis_queries.sql    # 3 key queries + CREATE VIEW statements
│
├── python/
│   ├── generate_data.py        # Generates synthetic dataset
│   ├── connect_mysql.py        # Connects pandas to MySQL
│   └── clean_data.py           # Full cleaning pipeline
│
├── assets/
│   └── dashboard_preview.png   # Screenshot of Power BI dashboard
│
├── NorthShelf_Dashboard.pbix   # Power BI dashboard file
└── README.md


### Dataset
Synthetic dataset generated using Python (faker, numpy, pandas).
TableRowsDescriptioncustomers1,000Customer profiles, regions, loyalty tiersproducts100Product catalog with prices and supplier costsorders5,000Order headers with dates, status, and regionorder_items~12,000Line items linking orders to products
Data was intentionally generated with null values, duplicate rows, and price outliers to simulate real-world messiness and demonstrate cleaning skills.


### How to Run
1. Generate the data
pip install faker pandas numpy
python python/generate_data.py
2. Set up MySQL
- Open MySQL Workbench
- Run sql/create_tables.sql to create the database and tables
- Import the 4 CSVs from data/raw/ using the Table Data Import Wizard
3. Run SQL analysis
- Run sql/analysis_queries.sql in MySQL Workbench
- This creates 3 VIEWs used by Power BI
4. Clean the data in Python
pip install mysql-connector-python sqlalchemy
Update DB_PASSWORD in clean_data.py
python python/clean_data.py
Cleaned CSVs are saved to data/cleaned/.
5. Open the Power BI dashboard
- Open NorthShelf_Dashboard.pbix in Power BI Desktop
- If prompted, update the data source path to your local data/cleaned/ folder


### Key Findings

- Electronics and Home & Garden accounted for the majority of revenue despite representing less than a third of total SKUs
- Platinum-tier customers showed higher average order values than Standard-tier customers, validating the loyalty program structure
- The Southeast region had high order volume but below-average revenue per order, suggesting potential discounting or returns issues worth investigating
- Monthly revenue showed consistent growth with a strong seasonal spike in December

### Dashboard Pages
- Page 1 — Executive Summary
KPI cards (Total Revenue, Average Order Value), revenue by category bar chart, monthly revenue trend line chart
- Page 2 — Customer Analysis
Customer count KPI, average LTV by loyalty tier, customer distribution by tier donut chart
- Page 3 — Region Performance
Total revenue by region, average revenue per order by region, full region metrics table with conditional formatting
All pages include a date slicer for filtering by time period.

DAX Measures
Total Revenue =
SUMX(
    order_items_clean,
    order_items_clean[quantity] * order_items_clean[unit_price]
) 

Average Order Value =
DIVIDE(
    [Total Revenue],
    DISTINCTCOUNT(orders_clean[order_id]),
    0
)

### Skills Demonstrated

- SQL — schema design, multi-table JOINs, GROUP BY aggregations, CTEs, CREATE VIEW
- Python — data cleaning with pandas (drop_duplicates, fillna, dropna, clip), connecting to MySQL via SQLAlchemy, feature engineering
- Power BI — data modeling, table relationships, DAX measures, interactive slicers, drill-through pages, conditional formatting

Author
Julio Torres

Linkedin - GitHub
