SQL scripts

-- ── 1. customers ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS customers (
    customer_id   INT            PRIMARY KEY,
    first_name    VARCHAR(50)    NOT NULL,
    last_name     VARCHAR(50)    NOT NULL,
    email         VARCHAR(100),                  -- nullable (nulls exist in our data)
    region        VARCHAR(50),
    loyalty_tier  VARCHAR(20),
    join_date     DATE
);
 
 
-- ── 2. products ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS products (
    product_id     INT             PRIMARY KEY,
    product_name   VARCHAR(200)    NOT NULL,
    category       VARCHAR(50),
    unit_price     DECIMAL(10, 2),
    supplier_cost  DECIMAL(10, 2)
);
 
 
-- ── 3. orders ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS orders (
    order_id     INT           PRIMARY KEY,
    customer_id  INT,
    order_date   DATE,
    status       VARCHAR(20),
    region       VARCHAR(50),                    -- nullable (nulls exist in our data)
 
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
 
 
-- ── 4. order_items ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS order_items (
    item_id     INT             PRIMARY KEY,
    order_id    INT,
    product_id  INT,
    quantity    INT,
    unit_price  DECIMAL(10, 2),
 
    FOREIGN KEY (order_id)   REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- QUERY 1: Monthly Revenue by Category
SELECT
    DATE_FORMAT(o.order_date, '%Y-%m')   AS month,
    p.category,
    COUNT(DISTINCT o.order_id)           AS total_orders,
    SUM(oi.quantity * oi.unit_price)     AS revenue
FROM orders o
JOIN order_items oi  ON o.order_id   = oi.order_id
JOIN products p      ON oi.product_id = p.product_id
WHERE o.status = 'completed'        
GROUP BY month, p.category
ORDER BY month ASC, revenue DESC;

CREATE OR REPLACE VIEW vw_monthly_revenue_by_category AS
SELECT
    DATE_FORMAT(o.order_date, '%Y-%m')   AS month,
    p.category,
    COUNT(DISTINCT o.order_id)           AS total_orders,
    SUM(oi.quantity * oi.unit_price)     AS revenue
FROM orders o
JOIN order_items oi  ON o.order_id    = oi.order_id
JOIN products p      ON oi.product_id = p.product_id
WHERE o.status = 'completed'
GROUP BY month, p.category
ORDER BY month ASC, revenue DESC;

SELECT * FROM vw_monthly_revenue_by_category;

-- QUERY 2: Customer Lifetime Value (LTV) by Loyalty Tier
SELECT
    c.loyalty_tier,
    COUNT(DISTINCT c.customer_id)               AS total_customers,
    ROUND(SUM(oi.quantity * oi.unit_price), 2)  AS total_revenue,
    ROUND(
        SUM(oi.quantity * oi.unit_price)
        / COUNT(DISTINCT c.customer_id), 2
    )                                           AS avg_ltv_per_customer
FROM customers c
JOIN orders o        ON c.customer_id = o.customer_id
JOIN order_items oi  ON o.order_id    = oi.order_id
WHERE o.status = 'completed'
GROUP BY c.loyalty_tier
ORDER BY avg_ltv_per_customer DESC;

CREATE OR REPLACE VIEW vw_ltv_by_loyalty_tier AS
SELECT
    c.loyalty_tier,
    COUNT(DISTINCT c.customer_id)               AS total_customers,
    ROUND(SUM(oi.quantity * oi.unit_price), 2)  AS total_revenue,
    ROUND(
        SUM(oi.quantity * oi.unit_price)
        / COUNT(DISTINCT c.customer_id), 2
    )                                           AS avg_ltv_per_customer
FROM customers c
JOIN orders o        ON c.customer_id = o.customer_id
JOIN order_items oi  ON o.order_id    = oi.order_id
WHERE o.status = 'completed'
GROUP BY c.loyalty_tier
ORDER BY avg_ltv_per_customer DESC;

SELECT * FROM vw_ltv_by_loyalty_tier;

-- QUERY 3: Region Performance Summary
SELECT
    o.region,
    COUNT(DISTINCT o.order_id)                  AS total_orders,
    COUNT(DISTINCT o.customer_id)               AS unique_customers,
    ROUND(SUM(oi.quantity * oi.unit_price), 2)  AS total_revenue,
    ROUND(
        SUM(oi.quantity * oi.unit_price)
        / COUNT(DISTINCT o.order_id), 2
    )                                           AS avg_revenue_per_order
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status  = 'completed'
  AND o.region IS NOT NULL           
GROUP BY o.region
ORDER BY total_revenue DESC;

CREATE OR REPLACE VIEW vw_region_performance AS
SELECT
    o.region,
    COUNT(DISTINCT o.order_id)                  AS total_orders,
    COUNT(DISTINCT o.customer_id)               AS unique_customers,
    ROUND(SUM(oi.quantity * oi.unit_price), 2)  AS total_revenue,
    ROUND(
        SUM(oi.quantity * oi.unit_price)
        / COUNT(DISTINCT o.order_id), 2
    )                                           AS avg_revenue_per_order
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status  = 'completed'
  AND o.region IS NOT NULL
GROUP BY o.region
ORDER BY total_revenue DESC;

SELECT * FROM vw_region_performance;

SHOW FULL TABLES WHERE Table_type = 'VIEW';
