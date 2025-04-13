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

**Indexes:**

*   **Doctor:** idx_doctor_department (department_id)
*   **Appointment:** 
    * idx_appointment_patient (patient_id)
    * idx_appointment_doctor (doctor_id)
    * idx_appointment_date (appointment_date)
*   **Medical Record:**
    * idx_medical_record_patient (patient_id)
    * idx_medical_record_doctor (doctor_id)
    * idx_medical_record_date (visit_date)
*   **Billing:**
    * idx_billing_appointment (appointment_id)
    * idx_billing_patient (patient_id)
    * idx_billing_date (bill_date)
