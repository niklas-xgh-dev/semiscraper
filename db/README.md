# Database Schema

```mermaid
erDiagram
    PRODUCTS ||--o{ PRODUCT_MARKETPLACE : has
    PRODUCT_MARKETPLACE ||--o{ PRODUCT_HISTORY : tracks

    PRODUCTS {
        int id PK
        string name
        string mpn UK
        string sku
        string description
        string manufacturer
        string package
        string packaging
    }

    PRODUCT_MARKETPLACE {
        int id PK
        int product_id FK
        string marketplace_name
        decimal price
        string currency
        string unit_pack
        string stock_status
        string lead_time
        timestamp last_updated
    }

    PRODUCT_HISTORY {
        int id PK
        int product_marketplace_id FK
        decimal price
        string currency
        string stock_status
        string lead_time
        timestamp recorded_at
    }