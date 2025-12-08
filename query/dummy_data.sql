------------------------------------------------------------
-- 1. DISTRICTS
------------------------------------------------------------
INSERT INTO districts (district_name) VALUES
('Kaliwates'),
('Sumbersari'),
('Patrang'),
('Tanggul'),
('Ambulu'),
('Wuluhan'),
('Puger'),
('Arjasa'),
('Tempurejo'),
('Ajung'),
('Jenggawah'),
('Kalisat');

------------------------------------------------------------
-- 2. ADDRESSES
------------------------------------------------------------
INSERT INTO addresses (street_name, district_id) VALUES
('Jl. Ahmad Yani', 1),
('Jl. Gajah Mada', 1),
('Jl. Imam Bonjol', 2),
('Jl. Mastrip', 2),
('Jl. Bengawan Solo', 3),
('Jl. Letjen Sutoyo', 3),
('Jl. Sultan Agung', 4),
('Jl. Hayam Wuruk', 5),
('Jl. Kartini', 6),
('Jl. Brawijaya', 7),
('Jl. Basuki Rahmat', 8),
('Jl. Kenanga', 9),
('Jl. Mawar', 10),
('Jl. Melati', 11),
('Jl. Teratai', 12),
('Jl. Wijaya Kusuma', 3),
('Jl. Kaliurang', 4),
('Jl. Jawa', 5),
('Jl. Sumatra', 6),
('Jl. Kalimantan', 7);

------------------------------------------------------------
-- 3. PRODUCT CATEGORIES
------------------------------------------------------------
INSERT INTO product_categories (category_name) VALUES
('Sapi'),
('Ayam'),
('Kambing'),
('Bebek'),
('Ikan');

------------------------------------------------------------
-- 4. PAYMENT METHODS
------------------------------------------------------------
INSERT INTO payment_methods (method_name) VALUES
('COD'),
('Transfer');

------------------------------------------------------------
-- 5. COURIERS
------------------------------------------------------------
INSERT INTO couriers (courier_name, phone_num, username, password) VALUES
('Kurir A', '081111111111', 'kurir1', 'pass1'),
('Kurir B', '081222222222', 'kurir2', 'pass2'),
('Kurir C', '081333333333', 'kurir3', 'pass3'),
('Kurir D', '081444444444', 'kurir4', 'pass4'),
('Kurir E', '081555555555', 'kurir5', 'pass5'),
('Kurir F', '081666666666', 'kurir6', 'pass6'),
('Kurir G', '081777777777', 'kurir7', 'pass7'),
('Kurir H', '081888888888', 'kurir8', 'pass8'),
('Kurir I', '081999999999', 'kurir9', 'pass9'),
('Kurir J', '082111111111', 'kurir10', 'pass10'),
('Kurir K', '082222222222', 'kurir11', 'pass11'),
('Kurir L', '082333333333', 'kurir12', 'pass12');

------------------------------------------------------------
-- 6. SELLERS
------------------------------------------------------------
INSERT INTO sellers (seller_name, phone_num, username, password, address_id) VALUES
('Seller A', '081111000001', 'seller1', 'pass1', 1);

------------------------------------------------------------
-- 7. CUSTOMERS
------------------------------------------------------------
INSERT INTO customers (customer_name, phone_num, username, password, address_id) VALUES
('Customer A', '082111000001', 'cust1', 'pass1', 11),
('Customer B', '082111000002', 'cust2', 'pass2', 12),
('Customer C', '082111000003', 'cust3', 'pass3', 13),
('Customer D', '082111000004', 'cust4', 'pass4', 14),
('Customer E', '082111000005', 'cust5', 'pass5', 15),
('Customer F', '082111000006', 'cust6', 'pass6', 16),
('Customer G', '082111000007', 'cust7', 'pass7', 17),
('Customer H', '082111000008', 'cust8', 'pass8', 18),
('Customer I', '082111000009', 'cust9', 'pass9', 19),
('Customer J', '082111000010', 'cust10', 'pass10', 20);

------------------------------------------------------------
-- 8. PRODUCTS (ONLY 10 ITEMS + GRAM)
------------------------------------------------------------
INSERT INTO products (product_name, product_stock, price, seller_id, category_id) VALUES
('Daging Sapi Paha Belakang 500 gram', 50, 120000, 1, 1),
('Daging Sapi Iga Pendek 500 gram', 35, 90000, 1, 1),
('Daging Sapi Giling Mentah 500 gram', 80, 70000, 1, 1),
('Daging Ayam Utuh Mentah 1000 gram', 100, 35000, 1, 2),
('Daging Ayam Paha Bawah 500 gram', 120, 28000, 1, 2),
('Daging Ayam Sayap Mentah 500 gram', 110, 26000, 1, 2),
('Daging Kambing Paha Depan 500 gram', 60, 85000, 1, 3),
('Daging Kambing Iga Panjang 500 gram', 45, 95000, 1, 3),
('Daging Bebek Dada Mentah 500 gram', 40, 55000, 1, 4),
('Ikan Lele Segar Utuh 1000 gram', 100, 25000, 1, 5);

------------------------------------------------------------
-- 9. DELIVERY STATUS
------------------------------------------------------------
INSERT INTO delivery_status (delivery_status) VALUES
('Ready'),
('Sending'),
('Received');

------------------------------------------------------------
-- 10. ORDER STATUS
------------------------------------------------------------
INSERT INTO order_status (order_status) VALUES
('Pending'),
('Rejected'),
('Accepted'),
('Cancelled');

------------------------------------------------------------
-- 11. DELIVERIES
------------------------------------------------------------
INSERT INTO deliveries (delivery_date, delivery_status_id, courier_id) VALUES
('2024-03-01', 1, 1),
('2024-03-02', 1, 2),
('2024-03-03', 1, 3),
('2024-03-04', 1, 4),
('2024-03-05', 1, 5),
('2024-03-06', 1, 6),
('2024-03-07', 1, 7),
('2024-03-08', 1, 8),
('2024-03-09', 1, 9),
('2024-03-10', 1, 10);

------------------------------------------------------------
-- 12. PAYMENTS
------------------------------------------------------------
INSERT INTO payments (payment_status, method_id) VALUES
('Y', 1),
('Y', 2),
('Y', 1),
('Y', 2),
('Y', 1),
('Y', 2),
('Y', 1),
('Y', 2),
('Y', 1),
('Y', 2);

------------------------------------------------------------
-- 13. ORDERS (10 ORDERS ONLY)
------------------------------------------------------------
INSERT INTO orders (order_date, order_status_id, payment_id, customer_id, delivery_id) VALUES
('2024-03-01', 1, 1, 1, 1),
('2024-03-02', 1, 2, 2, 2),
('2024-03-03', 1, 3, 3, 3),
('2024-03-04', 1, 4, 4, 4),
('2024-03-05', 1, 5, 5, 5),
('2024-03-06', 1, 6, 6, 6),
('2024-03-07', 1, 7, 7, 7),
('2024-03-08', 1, 8, 8, 8),
('2024-03-09', 1, 9, 9, 9),
('2024-03-10', 1, 10, 10, 10);

------------------------------------------------------------
-- 14. ORDER DETAILS (valid with 10 products only)
------------------------------------------------------------
INSERT INTO order_details (quantity, discount, price, product_id, order_id) VALUES
(2,0,120000,1,1), (1,0,35000,4,1),
(1,0,90000,2,2), (2,0,28000,5,2),
(1,0,70000,3,3), (1,0,26000,6,3),
(1,0,85000,7,4), (1,0,55000,9,4),
(2,0,95000,8,5), (1,0,25000,10,5),
(1,0,120000,1,6), (1,0,90000,2,6),
(2,0,70000,3,7), (1,0,35000,4,7),
(1,0,28000,5,8), (1,0,26000,6,8),
(1,0,85000,7,9), (1,0,95000,8,9),
(1,0,55000,9,10), (1,0,25000,10,10);
