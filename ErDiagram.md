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
        DECIMAL amount "Amount Due"
        DATETIME bill_date "Billing Date"
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

**Entities:**

*   **PATIENT:** Stores information about patients.
*   **DOCTOR:** Stores information about doctors.
*   **DEPARTMENT:** Stores information about hospital departments.
*   **APPOINTMENT:** Manages appointment scheduling between patients and doctors.
*   **MEDICAL\_RECORD:** Keeps track of patient visit details, diagnoses, and treatments.
*   **BILLING:** Handles billing information related to appointments.

**Relationships:**

*   A PATIENT can schedule multiple APPOINTMENTS.
*   A PATIENT has multiple MEDICAL\_RECORDS.
*   A DOCTOR conducts multiple APPOINTMENTS.
*   A DOCTOR belongs to one DEPARTMENT.
*   A DEPARTMENT employs multiple DOCTORS.
*   An APPOINTMENT generates one BILLING record.
*   A MEDICAL\_RECORD can inform BILLING (e.g., for procedures performed).
