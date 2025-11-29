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
DROP TABLE IF EXISTS delivery_status CASCADE;
DROP TABLE IF EXISTS order_status CASCADE;
DROP TABLE IF EXISTS product_categories CASCADE;

CREATE TABLE districts (
    district_id SERIAL PRIMARY KEY,
    district_name VARCHAR(64) NOT NULL
);

CREATE TABLE addresses (
    address_id SERIAL PRIMARY KEY,
    street_name VARCHAR(64) NOT NULL,
    district_id INTEGER NOT NULL,
    FOREIGN KEY (district_id) REFERENCES districts(district_id)
);

CREATE TABLE product_categories (
    category_id SERIAL PRIMARY KEY NOT NULL,
    category_name VARCHAR(64) NOT NULL
);

CREATE TABLE payment_methods (
    method_id SERIAL PRIMARY KEY NOT NULL,
    method_name VARCHAR(64) NOT NULL
);

CREATE TABLE couriers (
    courier_id SERIAL PRIMARY KEY NOT NULL,
    courier_name VARCHAR(64) NOT NULL,
    phone_num CHAR(12) NOT NULL,
    username VARCHAR(64) NOT NULL UNIQUE,
    password VARCHAR(64) NOT NULL,
	is_deleted BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE sellers (
    seller_id SERIAL PRIMARY KEY NOT NULL,
    seller_name VARCHAR(64) NOT NULL,
    phone_num CHAR(12) NOT NULL,
    username VARCHAR(64) NOT NULL UNIQUE,
    password VARCHAR(64) NOT NULL,
    address_id INTEGER NOT NULL UNIQUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (address_id) REFERENCES addresses(address_id)
);

CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY NOT NULL,
    customer_name VARCHAR(64) NOT NULL,
    phone_num CHAR(12) NOT NULL,
    username VARCHAR(64) NOT NULL UNIQUE,
    password VARCHAR(64) NOT NULL,
    address_id INTEGER NOT NULL UNIQUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (address_id) REFERENCES addresses(address_id)
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(64) NOT NULL,
    product_stock INTEGER NOT NULL,
    price INTEGER NOT NULL,
    seller_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (seller_id) REFERENCES sellers(seller_id),
    FOREIGN KEY (category_id) REFERENCES product_categories(category_id)
);

CREATE TABLE delivery_status(
    delivery_status_id SERIAL PRIMARY KEY,
    delivery_status VARCHAR(64) NOT NULL DEFAULT 'Pending'
);

CREATE TABLE order_status(
    order_status_id SERIAL PRIMARY KEY,
    order_status VARCHAR(64) NOT NULL DEFAULT 'Ready'
);

CREATE TABLE deliveries (
    delivery_id SERIAL PRIMARY KEY,
    delivery_date DATE NOT NULL,
    delivery_status_id INTEGER NOT NULL,
    courier_id INTEGER NOT NULL,
    FOREIGN KEY (delivery_status_id) REFERENCES delivery_status(delivery_status_id),
    FOREIGN KEY (courier_id) REFERENCES couriers(courier_id)
);

CREATE TABLE payments (
    payment_id SERIAL PRIMARY KEY,
    payment_status CHAR(1) NOT NULL,
    method_id INTEGER NOT NULL,
    FOREIGN KEY (method_id) REFERENCES payment_methods(method_id)
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    order_date DATE NOT NULL,
    order_status_id INTEGER NOT NULL,
    payment_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    delivery_id INTEGER NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (order_status_id) REFERENCES order_status(order_status_id),
    FOREIGN KEY (payment_id) REFERENCES payments(payment_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (delivery_id) REFERENCES deliveries(delivery_id)
);

CREATE TABLE order_details (
    detail_id SERIAL PRIMARY KEY,
    quantity INTEGER NOT NULL,
    discount INTEGER NOT NULL,
    price INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    order_id INTEGER NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);
