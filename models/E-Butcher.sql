
DROP TABLE IF EXISTS order_details CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS deliveries CASCADE;
DROP TABLE IF EXISTS districts CASCADE;
DROP TABLE IF EXISTS addresses CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS sellers CASCADE;
DROP TABLE IF EXISTS couriers CASCADE;
DROP TABLE IF EXISTS payment_methods CASCADE;
DROP TABLE IF EXISTS product_categories CASCADE;

CREATE TABLE product_categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(64)
);

CREATE TABLE payment_methods (
    method_id SERIAL PRIMARY KEY,
    method_name VARCHAR(64)
);

CREATE TABLE couriers (
    courier_id SERIAL PRIMARY KEY,
    courier_name VARCHAR(64),
    phone_num CHAR(12),
    username VARCHAR(64),
    password VARCHAR(64)
);

CREATE TABLE sellers (
    seller_id SERIAL PRIMARY KEY,
    seller_name VARCHAR(64),
    phone_num CHAR(12),
    username VARCHAR(64) UNIQUE,
    password VARCHAR(64)
);

CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(64),
    phone_num CHAR(12),
    username VARCHAR(64) UNIQUE,
    password VARCHAR(64)
);

CREATE TABLE addresses (
    address_id SERIAL PRIMARY KEY,
    seller_id INTEGER,
    customer_id INTEGER,
    street_name VARCHAR(64),
    FOREIGN KEY (seller_id) REFERENCES sellers(seller_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(64),
    product_stock INTEGER,
    price INTEGER,
    seller_id INTEGER,
    category_id INTEGER,
    FOREIGN KEY (seller_id) REFERENCES sellers(seller_id),
    FOREIGN KEY (category_id) REFERENCES product_categories(category_id)
);

CREATE TABLE deliveries (
    delivery_id SERIAL PRIMARY KEY,
    delivery_date DATE,
    courier_id INTEGER,
    FOREIGN KEY (courier_id) REFERENCES couriers(courier_id)
);

CREATE TABLE districts (
    district_id SERIAL PRIMARY KEY,
    district_name VARCHAR(64),
    address_id INTEGER,
    FOREIGN KEY (address_id) REFERENCES addresses(address_id)
);

CREATE TABLE payments (
    payment_id SERIAL PRIMARY KEY,
    payment_status CHAR(1),
    method_id INTEGER,
    FOREIGN KEY (method_id) REFERENCES payment_methods(method_id)
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    order_date DATE,
    order_status VARCHAR(64),
    payment_id INTEGER,
    customer_id INTEGER,
    delivery_id INTEGER,
    FOREIGN KEY (payment_id) REFERENCES payments(payment_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (delivery_id) REFERENCES deliveries(delivery_id)
);

CREATE TABLE order_details (
    detail_id SERIAL PRIMARY KEY,
    quantity INTEGER,
    discount INTEGER,
    product_id INTEGER,
    order_id INTEGER,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);
