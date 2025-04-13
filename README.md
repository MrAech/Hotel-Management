# 🏨 Hotel Management System

The **Hotel Management System** is a comprehensive application designed to streamline hotel operations, including **booking management**, **customer service**, and **database operations**.

---

## 🚀 Features

- Room Booking & Availability Tracking
- Customer Management
- Payment and Invoice Handling
- MySQL Database Integration

---

## 📦 Prerequisites

- [Anaconda / Miniconda](https://www.anaconda.com/docs/getting-started/anaconda/install) installed
- Python 3.10+
- MySQL Server

---

## ⚙️ Setup Instructions

### 1️⃣ Create and Activate Conda Environment

```
conda create --name hotel_management python=3.10
conda activate hotel_management
```

or Use 
```
python -m venv .venv
```
---

### 2️⃣ Install Dependencies

```
pip install -r requirements.txt
```

---

### 3️⃣ Configure Database Connection

Create a file named `db_config.py` in the root directory with the following content:

```
from pymysql.cursors import DictCursor

db_config = {
    "host": "your_host",
    "user": "your_user",
    "password": "your_password",
    "database": "your_database_name",
    "port": your_port,
    "charset": "utf8mb4",
    "cursorclass": DictCursor,
}
```

> Replace the placeholder values with your actual MySQL database details.

---

### 4️⃣ Create the Database Schema

Run the SQL commands in the `schema.sql` file using a MySQL client or terminal:

---

### 5️⃣ Run the Application

```
python app.py
```


# Hospital Management System - ER Diagram

```mermaid
erDiagram
    %% Core Entity Relationships
    PATIENT ||--o{ APPOINTMENT : "schedules"
    PATIENT ||--o{ MEDICAL_RECORD : "has"
    DOCTOR ||--o{ APPOINTMENT : "conducts"
    DOCTOR }|--|| DEPARTMENT : "belongs to"
    APPOINTMENT ||--o| BILLING : "generates"
    MEDICAL_RECORD ||--o{ BILLING : "informs"

    %% Database Views
    active_doctors_view ||--|{ DOCTOR : "represents"
    upcoming_appointments_view ||--|{ APPOINTMENT : "shows future"
    patient_medical_history_view ||--|{ PATIENT : "shows history"

    %% Database Functions and Procedures
    calculate_age ||--|{ PATIENT : "computes for"
    get_doctor_appointment_count ||--|{ DOCTOR : "counts for"
    schedule_appointment ||--|{ APPOINTMENT : "creates"
    complete_appointment_with_billing ||--|| APPOINTMENT : "completes"

    calculate_age {
        DATE dob "Input"
        INT age "Output"
    }

    get_doctor_appointment_count {
        INT doctor_id "Input"
        VARCHAR status "Input (optional)"
        INT count "Output"
    }

    schedule_appointment {
        INT patient_id "Input"
        INT doctor_id "Input"
        DATETIME appointment_date "Input"
        TEXT reason "Input"
    }

    complete_appointment_with_billing {
        INT appointment_id "Input"
        TEXT diagnosis "Input"
        TEXT treatment "Input"
        DECIMAL amount "Input"
    }

    PATIENT {
        INT patient_id PK "Patient ID"
        VARCHAR name "Name"
        DATE dob "Date of Birth"
        VARCHAR gender "Gender"
        VARCHAR address "Address"
        VARCHAR email "Email"
    }

    DOCTOR {
        INT doctor_id PK "Doctor ID"
        VARCHAR name "Name"
        VARCHAR specialization "Specialization"
        INT department_id FK "Department ID"
        VARCHAR phone "Phone Number"
        VARCHAR email "Email"
    }

    DEPARTMENT {
        INT department_id PK "Department ID"
        VARCHAR name "Department Name"
        VARCHAR description "Description"
        INT doctor_count "Number of Doctors (auto-maintained)"
    }

    APPOINTMENT {
        INT appointment_id PK "Appointment ID"
        INT patient_id FK "Patient ID"
        INT doctor_id FK "Doctor ID"
        DATETIME appointment_date "Appointment Date & Time"
        VARCHAR status "Status (Scheduled, Completed, Canceled)"
        TEXT reason "Reason for Visit"
    }
    MEDICAL_RECORD {
        INT record_id PK "Record ID"
        INT patient_id FK "Patient ID"
        INT doctor_id FK "Doctor ID (Attending)"
        DATE visit_date "Visit Date"
        TEXT diagnosis "Diagnosis"
        TEXT treatment "Treatment Plan"
        TEXT notes "Notes"
    }    BILLING {
        INT bill_id PK "Bill ID"
        INT appointment_id FK "Appointment ID"
        INT patient_id FK "Patient ID"
        DECIMAL amount "Amount Due (non-negative)"
        DATETIME bill_date "Billing Date"
        DATETIME paid_date "Date of Payment (optional)"
        ENUM status "Status (Paid, Unpaid)"
    }

    %% Database Views
    active_doctors_view {
        INT doctor_id "Doctor ID"
        VARCHAR doctor_name "Doctor Name"
        VARCHAR specialization "Specialization"
        VARCHAR phone "Phone Number"
        VARCHAR email "Email"
        VARCHAR department_name "Department Name"
    }

    upcoming_appointments_view {
        INT appointment_id "Appointment ID"
        DATETIME appointment_date "Date & Time"
        VARCHAR status "Status"
        VARCHAR patient_name "Patient Name"
        VARCHAR doctor_name "Doctor Name"
        VARCHAR department_name "Department Name"
    }

    patient_medical_history_view {
        INT patient_id "Patient ID"
        VARCHAR patient_name "Patient Name"
        DATE visit_date "Visit Date"
        VARCHAR doctor_name "Doctor Name"
        TEXT diagnosis "Diagnosis"
        TEXT treatment "Treatment"
        DECIMAL bill_amount "Bill Amount"
        VARCHAR payment_status "Payment Status"
    }

```