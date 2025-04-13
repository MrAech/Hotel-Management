-- Drop existing views, procedures, functions
DROP VIEW IF EXISTS active_doctors_view;

DROP VIEW IF EXISTS upcoming_appointments_view;

DROP VIEW IF EXISTS patient_medical_history_view;

DROP PROCEDURE IF EXISTS schedule_appointment;

DROP PROCEDURE IF EXISTS complete_appointment_with_billing;

DROP PROCEDURE IF EXISTS cancel_appointment;

DROP FUNCTION IF EXISTS calculate_age;

DROP FUNCTION IF EXISTS get_doctor_appointment_count;

-- Drop tables (reverse dependency order)
DROP TABLE IF EXISTS billing;

DROP TABLE IF EXISTS medical_record;

DROP TABLE IF EXISTS appointment;

DROP TABLE IF EXISTS doctor;

DROP TABLE IF EXISTS department;

DROP TABLE IF EXISTS patient;

-- Patient table
CREATE TABLE patient (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    dob DATE NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    address TEXT,
    email VARCHAR(100) UNIQUE
);

-- Department table
CREATE TABLE department (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    doctor_count INT DEFAULT 0
);

-- Doctor table
CREATE TABLE doctor (
    doctor_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    department_id INT NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100) UNIQUE,
    FOREIGN KEY (department_id) REFERENCES department (department_id) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE INDEX idx_doctor_department ON doctor (department_id);

-- Appointment table
CREATE TABLE appointment (
    appointment_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    appointment_date DATETIME NOT NULL,
    status ENUM(
        'Scheduled',
        'Completed',
        'Canceled'
    ) DEFAULT 'Scheduled',
    reason TEXT,
    FOREIGN KEY (patient_id) REFERENCES patient (patient_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctor (doctor_id) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE INDEX idx_appointment_patient ON appointment (patient_id);

CREATE INDEX idx_appointment_doctor ON appointment (doctor_id);

CREATE INDEX idx_appointment_date ON appointment (appointment_date);

-- Medical Record table
CREATE TABLE medical_record (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    visit_date DATE NOT NULL,
    diagnosis TEXT,
    treatment TEXT,
    notes TEXT,
    FOREIGN KEY (patient_id) REFERENCES patient (patient_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctor (doctor_id) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE INDEX idx_medical_record_patient ON medical_record (patient_id);

CREATE INDEX idx_medical_record_doctor ON medical_record (doctor_id);

CREATE INDEX idx_medical_record_date ON medical_record (visit_date);

-- Billing table
CREATE TABLE billing (
    bill_id INT AUTO_INCREMENT PRIMARY KEY,
    appointment_id INT NOT NULL,
    patient_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL CHECK (amount >= 0),
    bill_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    paid_date DATETIME NULL,
    status ENUM('Paid', 'Unpaid') DEFAULT 'Unpaid',
    FOREIGN KEY (appointment_id) REFERENCES appointment (appointment_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES patient (patient_id) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE INDEX idx_billing_appointment ON billing (appointment_id);

CREATE INDEX idx_billing_patient ON billing (patient_id);

CREATE INDEX idx_billing_date ON billing (bill_date);

-- Initial Data

INSERT INTO
    department (name, description)
VALUES (
        'Cardiology',
        'Treatments related to the heart'
    ),
    (
        'Neurology',
        'Disorders of the brain and nerves'
    ),
    (
        'Orthopedics',
        'Bone and joint care'
    ),
    (
        'Pediatrics',
        'Healthcare for children'
    ),
    (
        'Dermatology',
        'Skin conditions and treatments'
    );

INSERT INTO
    doctor (
        name,
        specialization,
        department_id,
        phone,
        email
    )
VALUES (
        'Dr. Ramesh Iyer',
        'Cardiologist',
        1,
        '9876543210',
        'ramesh.iyer@clinic.in'
    ),
    (
        'Dr. Anjali Deshmukh',
        'Neurologist',
        2,
        '9876543211',
        'anjali.deshmukh@clinic.in'
    ),
    (
        'Dr. Manoj Sinha',
        'Orthopedic Surgeon',
        3,
        '9876543212',
        'manoj.sinha@clinic.in'
    ),
    (
        'Dr. Pooja Nair',
        'Pediatrician',
        4,
        '9876543213',
        'pooja.nair@clinic.in'
    ),
    (
        'Dr. Arvind Mehra',
        'Dermatologist',
        5,
        '9876543214',
        'arvind.mehra@clinic.in'
    );

INSERT INTO
    patient (
        name,
        dob,
        gender,
        address,
        email
    )
VALUES (
        'Amit Sharma',
        '1988-03-15',
        'Male',
        'Lajpat Nagar, New Delhi',
        'amit.sharma@gmail.com'
    ),
    (
        'Neha Gupta',
        '1992-08-25',
        'Female',
        'Hinjewadi, Pune',
        'neha.gupta@gmail.com'
    ),
    (
        'Rahul Joshi',
        '2001-12-10',
        'Male',
        'Banjara Hills, Hyderabad',
        'rahul.joshi@gmail.com'
    ),
    (
        'Kavya Reddy',
        '2012-06-20',
        'Female',
        'Anna Nagar, Chennai',
        'kavya.reddy@gmail.com'
    );

INSERT INTO
    appointment (
        patient_id,
        doctor_id,
        appointment_date,
        status,
        reason
    )
VALUES (
        1,
        1,
        '2025-04-15 10:00:00',
        'Scheduled',
        'Shortness of breath'
    ),
    (
        2,
        2,
        '2025-04-16 11:30:00',
        'Scheduled', 
        'Frequent headaches'
    ),
    (
        3,
        3,
        '2025-04-17 09:30:00',
        'Canceled',
        'Joint pain'
    ),
    (
        4,
        4,
        '2025-04-18 16:00:00',
        'Scheduled',
        'Vaccination follow-up'
    );

INSERT INTO
    medical_record (
        patient_id,
        doctor_id,
        visit_date,
        diagnosis,
        treatment,
        notes
    )
VALUES (
        1,
        1,
        '2025-03-10',
        'Hypertension',
        'Amlodipine and lifestyle changes',
        'Patient to monitor BP daily'
    );

INSERT INTO
    billing (
        appointment_id,
        patient_id,
        amount,
        bill_date,
        status
    )
VALUES (
        1,
        1,
        2000.00,
        '2025-03-10',
        'Unpaid'
    );

-- Views

CREATE VIEW active_doctors_view AS
SELECT
    d.doctor_id,
    d.name AS doctor_name,
    d.specialization,
    d.phone,
    d.email,
    dep.name AS department_name
FROM doctor d
    JOIN department dep ON d.department_id = dep.department_id;

CREATE VIEW upcoming_appointments_view AS
SELECT
    a.appointment_id,
    a.appointment_date,
    a.status,
    p.name AS patient_name,
    d.name AS doctor_name,
    dep.name AS department_name
FROM
    appointment a
    LEFT JOIN patient p ON a.patient_id = p.patient_id
    JOIN doctor d ON a.doctor_id = d.doctor_id
    JOIN department dep ON d.department_id = dep.department_id
WHERE
    a.status = 'Scheduled'
    AND a.appointment_date >= CURRENT_TIMESTAMP
    AND p.patient_id IS NOT NULL;

CREATE VIEW patient_medical_history_view AS
SELECT
    p.patient_id,
    p.name AS patient_name,
    mr.visit_date,
    d.name AS doctor_name,
    mr.diagnosis,
    mr.treatment,
    b.amount AS bill_amount,
    b.status AS payment_status
FROM
    patient p
    LEFT JOIN medical_record mr ON p.patient_id = mr.patient_id
    LEFT JOIN doctor d ON mr.doctor_id = d.doctor_id
    LEFT JOIN billing b ON p.patient_id = b.patient_id;

-- Functions

DELIMITER / /

CREATE FUNCTION calculate_age(dob DATE)
RETURNS INT DETERMINISTIC
BEGIN
    RETURN FLOOR(DATEDIFF(CURRENT_DATE, dob)/365.25);
END //

CREATE FUNCTION get_doctor_appointment_count(p_doctor_id INT, p_status VARCHAR(20))
RETURNS INT DETERMINISTIC
BEGIN
    DECLARE count_appointments INT;

    SELECT COUNT(*) INTO count_appointments
    FROM appointment
    WHERE doctor_id = p_doctor_id
    AND (status = p_status OR p_status IS NULL);

    RETURN count_appointments;
END //

-- Procedures

CREATE PROCEDURE schedule_appointment(
    IN p_patient_id INT,
    IN p_doctor_id INT,
    IN p_appointment_date DATETIME,
    IN p_reason TEXT
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;
    INSERT INTO appointment (patient_id, doctor_id, appointment_date, reason, status)
    VALUES (p_patient_id, p_doctor_id, p_appointment_date, p_reason, 'Scheduled');
    COMMIT;
END //

CREATE PROCEDURE complete_appointment_with_billing(
    IN p_appointment_id INT,
    IN p_diagnosis TEXT,
    IN p_treatment TEXT,
    IN p_amount DECIMAL(10,2)
)
BEGIN
    DECLARE p_patient_id INT;
    DECLARE p_doctor_id INT;
    DECLARE p_visit_date DATETIME;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    UPDATE appointment 
    SET status = 'Completed'
    WHERE appointment_id = p_appointment_id;

    SELECT patient_id, doctor_id, appointment_date 
    INTO p_patient_id, p_doctor_id, p_visit_date
    FROM appointment
    WHERE appointment_id = p_appointment_id;

    INSERT INTO medical_record (
        patient_id, doctor_id, visit_date, 
        diagnosis, treatment
    )
    VALUES (
        p_patient_id, p_doctor_id, p_visit_date,
        p_diagnosis, p_treatment
    );

    INSERT INTO billing (
        appointment_id, patient_id, amount,
        bill_date, status
    )
    VALUES (
        p_appointment_id, p_patient_id, p_amount,
        CURRENT_DATE, 'Unpaid'
    );

    COMMIT;
END //

CREATE PROCEDURE cancel_appointment(
    IN p_appointment_id INT
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;
    UPDATE appointment 
    SET status = 'Canceled'
    WHERE appointment_id = p_appointment_id;
    COMMIT;
END //

-- Triggers

CREATE TRIGGER prevent_double_booking
BEFORE INSERT ON appointment
FOR EACH ROW
BEGIN
    IF EXISTS (
        SELECT 1 FROM appointment
        WHERE doctor_id = NEW.doctor_id
        AND appointment_date BETWEEN 
            DATE_SUB(NEW.appointment_date, INTERVAL 30 MINUTE)
            AND DATE_ADD(NEW.appointment_date, INTERVAL 30 MINUTE)
        AND status != 'Canceled'
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Doctor is already booked at this time';
    END IF;
END //

CREATE TRIGGER update_department_doctor_count
AFTER INSERT ON doctor
FOR EACH ROW
BEGIN
    UPDATE department
    SET doctor_count = (
        SELECT COUNT(*) FROM doctor WHERE department_id = NEW.department_id
    )
    WHERE department_id = NEW.department_id;
END //

DELIMITER;