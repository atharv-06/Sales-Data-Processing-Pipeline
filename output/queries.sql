SELECT
    product,
    SUM(quantity) AS units_sold,
    ROUND(SUM(revenue), 2) AS total_revenue
FROM silver_sales
GROUP BY product
ORDER BY total_revenue DESC;

SELECT
    substr(order_date, 1, 7) AS sales_month,
    ROUND(SUM(revenue), 2) AS monthly_revenue
FROM silver_sales
GROUP BY substr(order_date, 1, 7)
ORDER BY sales_month;

SELECT *
FROM silver_sales
WHERE quantity <= 0
   OR unit_price < 0
   OR product IS NULL;