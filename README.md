# Demand Sensing SaaS (Foreat)

A Django-based Demand Sensing application with ML forecasting.

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install django pandas scikit-learn numpy plotly
    ```

2.  **Initialize Database**:
    ```bash
    python manage.py migrate
    ```

3.  **Seed Data**:
    ```bash
    python manage.py import_ingredients
    python manage.py import_dummy_sales
    ```

4.  **Create Admin**:
    (Already created: `admin` / `password123`)
    ```bash
    python manage.py createsuperuser
    ```

5.  **Run Server**:
    ```bash
    python manage.py runserver
    ```

## Features

-   **Dashboard**: Overview of sales and system status.
-   **Upload**: Drag & drop CSV upload with dynamic column mapping.
-   **Training Hub**:
    -   Trigger ML training (Random Forest).
    -   View Forecast Charts (Plotly).
    -   View Ingredient Requirements (BOM Calculation).

## Credentials

-   **Username**: admin
-   **Password**: password123