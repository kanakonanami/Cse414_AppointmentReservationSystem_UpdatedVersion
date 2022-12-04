CREATE TABLE Caregivers (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);


CREATE TABLE Availabilities (
    Time date,
    Username varchar(255) REFERENCES Caregivers(Username),
    PRIMARY KEY (Time, Username)
);


CREATE TABLE Vaccines (
    Name varchar(255),
    Doses int,
    PRIMARY KEY (Name)
);


# Edited
CREATE TABLE Patients (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);


# Edited
CREATE TABLE Appointments (
    Appointment_id int IDENTITY(414, 1),
    Appointment_time date,
    Patient_id varchar(255) REFERENCES Patients(Username), 
    Caregiver_id varchar(255) REFERENCES Caregivers(Username),
    Vaccine_name varchar(255) REFERENCES Vaccines(Name),
    PRIMARY KEY (Appointment_id)
);




/*

*/

