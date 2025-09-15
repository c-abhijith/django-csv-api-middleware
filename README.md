

# CSV Upload API & Middleware — Django RESTful Project

This project covers **2 Tasks**:

1. Upload a CSV file, validate data, and store valid rows in the database with **detailed validation errors**.
2. Add middleware with **Redis‑based request** (block requests if >100 requests in 5 minutes) and return proper error messages.

---





## Folder Structure
    src                ----> Django project
    user               ----> Django app
    sample_data        ----> keep files to use for clientsgit remote add origin https://github.com/c-abhijith/django-csv-api-middleware.git

        




## 1) Quick Start

```bash
# Step 1: Create virtual environment
    python -m venv venv

# Step 2: Activate environment
    # Linux/Mac:
                source venv/bin/activate
    # Windows:
                venv\Scripts\activate

# Step 3: Install dependencies
    pip install -r requirements.txt

# Step 4: Run migrations
    python manage.py makemigrations
    python manage.py migrate

# Step 5: Start Redis
    # Linux/Mac:
        redis-server
    # Windows:
        # 1. Open WSL
        redis-server

# Step 6: Start Django
    python manage.py runserver


```

> **File upload:** open `http://127.0.0.1:8000/api/upload-csv/` and send a **POST** request with a CSV file {field name **file**}.

---

## 2) Tech Stack

* **Django 5 / DRF** — REST API
* **SQLite** — Database (easy for development)
* **Redis** — Middleware cache (rate limiting)

---

## 3) Data Model (minimal)

**User** (custom):

* `id`
* `name`(non empty)
* `email` (unique)
* `age` (0–120)

### Validation Rules

* `email`: required, valid format, must be unique
* `name`: required, max length 50 , non empty
* `age`: must be between 0–120

---

## 4) API Response Example


```json
{
  "Detailed_validation": {
    "rows_with_empty_string": {
      "rows": [
        {"name": null, "age": -1.0, "email": "afd@gmail.com"},
        {"name": null, "age": 20.0, "email": "sam@gmail.com"},
        {"name": "sam", "age": null, "email": null}
      ]
    },
    "duplicate_emails": {
      "rows": [
        {"name": "abhi", "age": 13.0, "email": "abhi@gmail.com"},
        {"name": "abhi", "age": 10.0, "email": "abhi@gmail.com"}
      ]
    },
    "invalid_age_rows": {
      "rows": [
        {"name": null, "age": -1.0, "email": "afd@gmail.com"},
        {"name": "ben", "age": -2.0, "email": "ben@gmai.com"},
        {"name": "Fathima", "age": -10.0, "email": "fathima@gmail.com"}
      ]
    },
    "invalid_email_rows": {
      "rows": [
        {"name": "bibin", "age": 78, "email": "bibin@g.com"},
        {"name": "chandini", "age": 18, "email": "chandini.com"},
        {"name": "diya", "age": 90, "email": "diya.gmail.com"},
        {"name": "emmy", "age": 12, "email": "emmy@gmail.in"}
      ]
    },
    "already_existing_emails_in_db": {
      "rows": [
        {"name": "abhi", "age": 13, "email": "abhi@gmail.com"},
        {"name": "Gayathi", "age": 45, "email": "gayathri@gmail.com"},
        {"name": "abhi", "age": 10, "email": "abhi@gmail.com"},
        {"name": "zoo", "age": 23, "email": "zoo@gmail.com"}
      ]
    }
  },
  "total_records": 13,
  "success_data": 0,
  "failure_data": 13
}
```


---

## Middleware (Task 2)

**Request Rate Limiter (Redis):**

   * Max 100 requests per 5 minutes and Returns `429 Too Many Requests` if exceeded.



---


---

## Postman Link

   * URL: `http://127.0.0.1:8000/api/upload-csv/`


---

##  Test Case

```bash
python manage.py test
```

---

##  Sample_data(Folder)
    It just keep csv file ,json response file  and test case result image

