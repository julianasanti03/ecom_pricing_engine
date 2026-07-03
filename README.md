# Multi-Marketplace E-commerce Pricing Engine

A data engineering project focused on centralizing, validating, and processing commercial pricing rules for multi-marketplace e-commerce operations.

The system was designed to replace a spreadsheet-based pricing workflow with a relational, auditable, and scalable architecture built on Python and PostgreSQL. It establishes a Single Source of Truth (SSOT) for supplier commercial rules while providing deterministic pricing calculations, execution traceability, and data quality enforcement.

---

## Business Context

The original operation relied on shared Google Sheets and Apps Script workflows to manage pricing calculations across:

* 30+ suppliers
* 3 marketplace environments
* 8 Amazon and Mercado Libre storefronts

As transaction volume and business complexity increased, the spreadsheet-based approach became increasingly difficult to maintain due to:

* Manual intervention requirements
* Lack of schema enforcement
* Limited auditability
* Business rule fragmentation
* Data quality inconsistencies
* Scaling constraints

To address these challenges, the pricing logic was migrated into a centralized Python and PostgreSQL architecture.

---

## Solution Architecture

The platform follows a layered architecture designed around data integrity, traceability, and operational reliability.

<img width="711" height="956" alt="Motor_1_semaforo" src="https://github.com/user-attachments/assets/022676c7-be0b-42d3-8e9d-175b9a99c92f" />



### Core Components

#### Supplier Rules Repository (`reglas_proveedores`)

Centralized configuration layer containing supplier-specific business rules, including:

* Commercial discounts
* Currency conversion settings
* SKU normalization rules
* Pricing behavior flags

Acts as the authoritative source for all supplier-level pricing logic.

#### Historical Cost Layer (`costos_proveedores_historico`)

Stores supplier pricing snapshots and historical cost information.

Features:

* Referential integrity enforcement
* Data quality validation
* Historical tracking
* Audit timestamps

#### Marketplace Configuration Layer (`canales_marketplace`)

Stores marketplace-specific operational parameters, including:

* Commission structures
* Storefront definitions
* Account-level configuration

Supports pricing calculations across multiple commercial channels.

#### Pipeline Execution Ledger (`historial_corridas`)

Operational logging component responsible for tracking:

* Pipeline execution timestamps
* Processing periods
* Execution status
* Failure events
* Operational metadata

Provides full execution traceability and auditability.

---

## Technical Features

### ETL/ELT Processing

* Automated ingestion workflows
* Data normalization pipelines
* Schema validation
* Data type enforcement
* Historical data persistence

### Pricing Calculation Engine

Python and SQL-based pricing engine capable of processing large-scale commercial datasets while dynamically evaluating:

* Target margins
* Marketplace commissions
* Shipping costs
* Tax structures
* Supplier-specific pricing rules

### Data Quality Controls

* SKU normalization
* Referential integrity constraints
* NOT NULL enforcement
* Numeric precision controls
* Validation checkpoints

### Data Governance

* Single Source of Truth (SSOT)
* Centralized business rules
* Audit logging
* Execution monitoring
* Historical traceability

---

## Technology Stack

### Languages

* Python
* SQL

### Database

* PostgreSQL

### Data Processing

* Pandas
* NumPy

### Data Modeling

* DBML
* Relational Database Design

### Orchestration (Current Migration)

* Apache Airflow

### Infrastructure

* Docker
* Git

---

## Repository Structure

```text
ecom_pricing_engine/
│
├── src/
│   ├── ingestion/
│   ├── pricing_engine/
│   ├── validation/
│   └── exports/
│
├── database/
│   ├── ddl/
│   ├── dbml/
│   └── seed_data/
│
├── airflow/
│   └── dags/
│
├── diagrams/
│   └── architecture/
│
├── docs/
│
└── README.md
```

---

## Business Impact

* Centralized pricing logic for 30+ suppliers.
* Eliminated manual pricing calculations and spreadsheet dependency.
* Established a relational Single Source of Truth (SSOT).
* Improved operational traceability through execution logging.
* Increased data consistency through schema enforcement and validation controls.
* Enabled the migration from spreadsheet-based operations to a scalable data architecture.

---

## Future Roadmap

* Airflow DAG orchestration
* Dockerized deployment
* API-based supplier ingestion
* Automated alerting and monitoring
* CI/CD integration
* Data quality reporting

---

## Author

**Juliana Santillan**

Data Engineer | Pricing & Revenue Systems | ETL & Automation

LinkedIn:
linkedin.com/in/juliana-santillan
