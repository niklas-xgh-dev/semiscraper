-- Products table
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    mpn VARCHAR(100) UNIQUE NOT NULL,
    sku VARCHAR(100),
    description TEXT,
    manufacturer VARCHAR(255)
);

-- Product_marketplace table
CREATE TABLE product_marketplace (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id),
    marketplace_name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2),
    currency VARCHAR(3),
    unit_pack VARCHAR(100),
    stock_status VARCHAR(100),
    lead_time VARCHAR(100),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (product_id, marketplace_name),
    package VARCHAR(100),
    packaging VARCHAR(100)
);

-- Product history table
CREATE TABLE product_history (
    id SERIAL PRIMARY KEY,
    product_marketplace_id INTEGER REFERENCES product_marketplace(id),
    price DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    stock_status VARCHAR(100) NOT NULL,
    lead_time VARCHAR(100),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for efficient querying
CREATE INDEX idx_product_marketplace_name ON product_marketplace(marketplace_name);
CREATE INDEX idx_product_history_product_marketplace ON product_history(product_marketplace_id);

-- View for product history
CREATE VIEW product_history_view AS
SELECT 
    ph.id AS history_id,
    p.id AS product_id,
    p.name AS product_name,
    p.mpn,
    pm.marketplace_name,
    ph.price,
    ph.currency,
    ph.stock_status,
    ph.lead_time,
    ph.recorded_at
FROM 
    product_history ph
JOIN 
    product_marketplace pm ON ph.product_marketplace_id = pm.id
JOIN 
    products p ON pm.product_id = p.id;