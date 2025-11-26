SELECT 
    o.order_id,
    o.order_date,
    c.customer_name,
    p.product_name,
	ca.category_name,
    od.quantity,
    od.price,
    od.discount,
	s.seller_name
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_details od ON o.order_id = od.order_id
JOIN products p ON od.product_id = p.product_id
JOIN product_categories ca ON p.category_id = ca.category_id
JOIN sellers s ON s.seller_id = p.seller_id
ORDER BY o.order_id;

SELECT 
    *
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_details od ON o.order_id = od.order_id
JOIN products p ON od.product_id = p.product_id
JOIn sellers s ON s.seller_id = p.seller_id
ORDER BY o.order_id;