INSERT INTO product_categories (category_name) VALUES
('Электроника'),
('Одежда'),
('Мебель'),
('Книги'),
('Спорттовары'),
('Красота'),
('Игрушки'),
('Продукты');

INSERT INTO sellers (seller_id, name, description, photo_url, phone_number, email) VALUES
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'TechGadgets', 'Официальный магазин электроники', 'https://example.com/sellers/techgadgets.jpg', '+79161234567', 'tech@example.com'),
('b1eebc99-9c0b-4ef8-bb6d-6bb9bd380a12', 'FashionStore', 'Модная одежда и аксессуары', 'https://example.com/sellers/fashionstore.jpg', '+79162345678', 'fashion@example.com'),
('c2eebc99-9c0b-4ef8-bb6d-6bb9bd380a13', 'HomeDecor', 'Мебель и предметы интерьера', 'https://example.com/sellers/homedecor.jpg', '+79163456789', 'home@example.com');

INSERT INTO users (user_id, name, surname, photo_url, phone_number, email, hashed_password_base64) VALUES
('d3eebc99-9c0b-4ef8-bb6d-6bb9bd380a14', 'Иван', 'Иванов', 'https://example.com/users/ivan.jpg', '+79164567890', 'ivan@example.com', 'aGVsbG8='),
('e4eebc99-9c0b-4ef8-bb6d-6bb9bd380a15', 'Мария', 'Петрова', 'https://example.com/users/maria.jpg', '+79165678901', 'maria@example.com', 'd29ybGQ='),
('f5eebc99-9c0b-4ef8-bb6d-6bb9bd380a16', 'Алексей', 'Сидоров', 'https://example.com/users/alex.jpg', '+79166789012', 'alex@example.com', 'cGFzc3dvcmQ=');

INSERT INTO user_addresses (address_id, user_id, country, settlement, street, house_number, apartment_number, extra_info) VALUES
('a6eebc99-9c0b-4ef8-bb6d-6bb9bd380a17', 'd3eebc99-9c0b-4ef8-bb6d-6bb9bd380a14', 'Россия', 'Москва', 'Ленина', '10', '25', 'Код домофона: 123'),
('b7eebc99-9c0b-4ef8-bb6d-6bb9bd380a18', 'e4eebc99-9c0b-4ef8-bb6d-6bb9bd380a15', 'Россия', 'Санкт-Петербург', 'Невский проспект', '5', '12', ''),
('c8eebc99-9c0b-4ef8-bb6d-6bb9bd380a19', 'f5eebc99-9c0b-4ef8-bb6d-6bb9bd380a16', 'Россия', 'Казань', 'Пушкина', '3', '7', '3 этаж');

INSERT INTO products (product_id, name, description, seller_id, category, photo_url, creation_time, price_rub, price_last_updated) VALUES
('d9eebc99-9c0b-4ef8-bb6d-6bb9bd380a20', 'Смартфон X', 'Новый флагман с камерой 108 МП', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'Электроника', 'https://example.com/products/phonex.jpg', '2023-01-15 10:00:00', 79990, '2023-01-15 10:00:00'),
('e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21', 'Джинсы Slim Fit', 'Классические джинсы, синие', 'b1eebc99-9c0b-4ef8-bb6d-6bb9bd380a12', 'Одежда', 'https://example.com/products/jeans.jpg', '2023-02-20 14:30:00', 4990, '2023-02-20 14:30:00'),
('f1eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'Диван угловой', 'Мягкий угловой диван, цвет серый', 'c2eebc99-9c0b-4ef8-bb6d-6bb9bd380a13', 'Мебель', 'https://example.com/products/sofa.jpg', '2023-03-10 09:15:00', 45990, '2023-03-10 09:15:00');

INSERT INTO product_prices_history (entry_id, product_id, price_rub, valid_from, valid_to) VALUES
(1, 'd9eebc99-9c0b-4ef8-bb6d-6bb9bd380a20', 84990, '2023-01-01 00:00:00', '2023-01-14 23:59:59'),
(2, 'd9eebc99-9c0b-4ef8-bb6d-6bb9bd380a20', 79990, '2023-01-15 00:00:00', '2023-12-31 23:59:59'),
(3, 'e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21', 5490, '2023-02-01 00:00:00', '2023-02-19 23:59:59'),
(4, 'e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21', 4990, '2023-02-20 00:00:00', '2023-12-31 23:59:59');

INSERT INTO comments (comment_id, product_id, user_id, content, rating, time) VALUES
(1, 'd9eebc99-9c0b-4ef8-bb6d-6bb9bd380a20', 'd3eebc99-9c0b-4ef8-bb6d-6bb9bd380a14', 'Отличный телефон, быстрый и удобный!', 5, '2023-01-20 18:30:00'),
(2, 'e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21', 'e4eebc99-9c0b-4ef8-bb6d-6bb9bd380a15', 'Джинсы сели хорошо, но ткань жестковата.', 4, '2023-02-25 12:45:00');

INSERT INTO shopping_cart_entries (entry_id, product_id, user_id, quantity) VALUES
(1, 'd9eebc99-9c0b-4ef8-bb6d-6bb9bd380a20', 'd3eebc99-9c0b-4ef8-bb6d-6bb9bd380a14', 1),
(2, 'e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21', 'e4eebc99-9c0b-4ef8-bb6d-6bb9bd380a15', 2);

INSERT INTO orders (order_id, user_id, address_id, status, order_date, shipped_date, total_cost_rub) VALUES
('a1eebc99-9c0b-4ef8-bb6d-6bb9bd380a23', 'd3eebc99-9c0b-4ef8-bb6d-6bb9bd380a14', 'a6eebc99-9c0b-4ef8-bb6d-6bb9bd380a17', 'Доставлен', '2023-01-25 15:30:00', '2023-01-28 10:00:00', 79990),
('b2eebc99-9c0b-4ef8-bb6d-6bb9bd380a24', 'e4eebc99-9c0b-4ef8-bb6d-6bb9bd380a15', 'b7eebc99-9c0b-4ef8-bb6d-6bb9bd380a18', 'В обработке', '2023-03-01 11:20:00', NULL, 9980);

INSERT INTO order_entries (entry_id, order_id, product_id, quantity, product_name, product_price_rub, product_seller_id, product_seller_name) VALUES
(1, 'a1eebc99-9c0b-4ef8-bb6d-6bb9bd380a23', 'd9eebc99-9c0b-4ef8-bb6d-6bb9bd380a20', 1, 'Смартфон X', 79990, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'TechGadgets'),
(2, 'b2eebc99-9c0b-4ef8-bb6d-6bb9bd380a24', 'e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21', 2, 'Джинсы Slim Fit', 4990, 'b1eebc99-9c0b-4ef8-bb6d-6bb9bd380a12', 'FashionStore');