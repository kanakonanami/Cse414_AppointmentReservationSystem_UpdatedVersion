from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime
import re

'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None

"""
TODO: Part 1  (done)
"""
def create_patient(tokens):
    # check 1: the length for tokens need to be exactly 3
    #   to include all information (with the operation name)
    if len(tokens) != 3:
      print("Failed to create user. Tokens length needs to be 3")
      return

    # tokens[0] is the operation name
    username = tokens[1]
    password = tokens[2]

    # check 2: the username should not be taken already
    if username_exists_patient(username):
        print("Username taken, try again!")
        return

    # check 3: check the password whether is considered as safe
    # Extra Credit (done)
    if bool(check_password(password)) == False:
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the patient
    patient = Patient(username, salt=salt, hash=hash)

    # save to patient information to our database
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 
    #   to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user. Tokens length need to be 3.")
        return

    username = tokens[1]
    password = tokens[2]

    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return

    # check 3: check the password whether is considered as safe
    # Extra Credit (done)
    if bool(check_password(password)) == False:
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first 
        #    record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first 
        #    record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


"""
TODO: Part 1  (done)
"""
def login_patient(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    global current_caregiver
    if current_patient is not None or current_caregiver is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3
    #    to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed. Tokens need to have length of 3!")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if patient is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_patient = patient


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    global current_patient
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3
    #    to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed. The length for tokens need to be exactly 3!")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver

"""
TODO: Part 2 (done)
"""
# search_caregiver_schedule time
def search_caregiver_schedule(tokens):
    # check 1: the tokens length needs to be 2
    if len(tokens) != 2:
        print("Please try again!")
        return

    # login_caregiver <username> <password>
    # check 2: they need to log in first
    global current_caregiver
    global current_patient
    if current_caregiver is None and current_patient is None:
        print("Please login first.")
        return

    date = tokens[1]

    cm = ConnectionManager()
    conn = cm.create_connection()

    count_doses = "SELECT Username, Name, Doses FROM Availabilities, Vaccines WHERE Time = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(count_doses, date)

        print("Available Caregiver, Vaccine, Dose:")
        for row in cursor:
            caregiver_name = (row['Username'])
            vac_name = (row['Name'])
            vac_num = (row['Doses'])

            vaccine_info = caregiver_name + " " + vac_name + " " + str(vac_num)
            print(vaccine_info)

    except pymssql.Error as e:
        print("Please try again!")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Please try again!")
        print("Error:", e)
    finally:
        cm.close_connection()     


"""
TODO: Part 2 (done)
"""
def reserve(tokens):
    global current_patient
    global current_caregiver

    # check 1: must login first
    if current_patient is None and current_caregiver is None:
        print("Please login first!")
        return

    # check 2: must login as a patient
    if current_patient is None:
        print("Please login as a patient!")
        return

    # check 3: the length for tokens need to be exactly 4
    #     to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    date = tokens[1]
    vaccine_name = tokens[2]

    cm = ConnectionManager()
    conn = cm.create_connection()

    available_care = "SELECT Username FROM Availabilities WHERE Time = %s ORDER BY Username ASC"
    available_caregivers = ""

    available_dose = "SELECT Doses FROM Vaccines WHERE Name = %s"
    vaccine_num = None

    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(available_care, date)
        for row in cursor:
            caregiver_name = (row['Username'])
            available_caregivers += str(caregiver_name) + " "

        # check 4: ensure available caregiver
        if available_caregivers == "" or available_caregivers == " ":
            print("No Caregiver is available!")
            return

        # pick the first available caregiver username
        pick_caregiver = (available_caregivers.split(" "))[0]

        # check 5: ensure available doses
        cursor_get_doses = conn.cursor(as_dict=True)
        cursor_get_doses.execute(available_dose, vaccine_name)
        for row in cursor_get_doses:
            dose_num = (row['Doses'])
            vaccine_num = dose_num

        if vaccine_num is None or vaccine_num <= 0:
            print("No enough available doses!")
            return

        # Steps: Make Appointment: Insert Appointment_id, Appointment_time,
        #                          Patient_id, Caregiver_id, Vaccine_name name
        #        Remove Username from Availabilities on the given date
        #        Decrease doses from Vaccine
        #        Print “Appointment ID: {appointment_id}, Caregiver username: {username}”

        # Step 1: Make Appointments
        make_appointment = "INSERT INTO Appointments VALUES (%s, %s, %s, %s)"
        cursor_appoints = conn.cursor(as_dict = True)
        cursor_appoints.execute(make_appointment, (date, current_patient.get_username(), pick_caregiver, vaccine_name))
        conn.commit()

        # Step 2: Update Availabilities
        remove_caregiver = "DELETE FROM Availabilities WHERE Time = %s AND Username = %s"
        cursor_update_caregiver = conn.cursor(as_dict = True)
        cursor_update_caregiver.execute(remove_caregiver, (date, pick_caregiver))
        conn.commit()

        # Step 3: Decrease Vaccine doses
        vaccine = Vaccine(vaccine_name, vaccine_num).get()
        vaccine.decrease_available_doses(1)

        # Step 4: Print “Appointment ID: {appointment_id}, Caregiver username: {username}”
        get_app_id = "SELECT Appointment_id FROM Appointments WHERE Appointment_time = %s AND Caregiver_id = %s"
        cursor_app_id = conn.cursor(as_dict = True)
        cursor_app_id.execute(get_app_id, (date, pick_caregiver))
        appointment_id = ""
        for row in cursor_app_id:
            appointment_id = str(row['Appointment_id'])
        print("Your reservation has been made successfully!")
        message_string = "Appointment_id: " + appointment_id + ", Caregiver username: " + pick_caregiver
        print(message_string)

    except pymssql.Error as e:
        print("Please try again!")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Please try again!")
        print("Error:", e)
    finally:
        cm.close_connection()


def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2
    #     to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        current_caregiver.upload_availability(d)
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return
    print("Availability uploaded!")


def cancel(tokens):
    """
    TODO: Extra Credit
    """
    pass


"""
Extra Credit
"""
# a safe passwords must meet the following 4 requirements
def check_password(password):

    password = str(password)
    # check 1: at least 8 characters
    if len(password) < 8:
        print("Password needs at least 8 characters")
        return False
    
    # check 2: inclusion of at least one 
    #    special character, from “!”, “@”, “#”, “?”
    if not bool(("!" in password) or ("@" in password) or ("#" in password) or ("?" in password)):
        print("Please contains at least on special character from ! @ # ?")
        return False
    
    # check 3: contains letters both in uppercase and lowercase
    check_up = any(le.isupper() for le in password)
    check_low = any(letters.islower() for letters in password)
    up_mix_low = check_up and check_low
    if not bool(up_mix_low):
        print("Please include both lowercase and uppercase letters")
        return False

    # check 4: contains of both letters and numbers
    #  only letters can either pass isupper() or islower()
    num_mix_letter = any(l.isdigit() for l in password)
    if not bool(num_mix_letter):
        print("Please include both letters and numbers")
        return False
    
    return True


def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3
    #    to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Error occurred when adding doses")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when adding doses")
        print("Error:", e)
        return

    # if the vaccine is not found in the database, add a 
    #     new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    else:
        # if the vaccine is not null, meaning that the vaccine
        #     already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    print("Doses updated!")

'''
TODO: Part 2 
'''
def show_appointments(tokens):
    # check 1: login first
    global current_caregiver
    global current_patient

    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return

    try:
        cm = ConnectionManager()
        conn = cm.create_connection()

        # check 2: login as a caregiver
        if current_caregiver is not None:
            appoint_caregiver = "SELECT Appointment_id, Vaccine_name, Appointment_time, Patient_id FROM Appointments WHERE Caregiver_id = %s ORDER BY Appointment_id ASC"
            caregiver_name = current_caregiver.get_username()
            cursor_caregiver = conn.cursor(as_dict = True)
            cursor_caregiver.execute(appoint_caregiver, caregiver_name)
            for row in cursor_caregiver:
                appointment_id = str(row['Appointment_id'])
                vac_name = str(row['Vaccine_name'])
                appointment_time = str(row['Appointment_time'])
                patient_name = str(row['Patient_id'])
                print("Appointment id: ", appointment_id, " Vaccine: ", vac_name, " Date: ", appointment_time, " Patient: ", patient_name)

        # check 3: login as a patient
        if current_patient is not None:
            appoint_patient = "SELECT Appointment_id, Vaccine_name, Appointment_time, Caregiver_id FROM Appointments WHERE Patient_id = %s ORDER BY Appointment_id ASC"
            patient_name = current_patient.get_username()
            cursor_patient = conn.cursor(as_dict=True)
            cursor_patient.execute(appoint_patient, patient_name)
            for row in cursor_patient:
                appointment_id = str(row['Appointment_id'])
                vac_name = str(row['Vaccine_name'])
                appointment_time = str(row['Appointment_time'])
                caregiver_name = str(row['Caregiver_id'])
                message_string = "Appointment id: " + appointment_id + " Vaccine: " + vac_name + " Date: " + appointment_time + " Caregiver: " + caregiver_name
                print(message_string)

    except pymssql.Error as e:
        print("Please try again!")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Please try again!")
        print("Error:", e)
    finally:
        cm.close_connection()


"""
TODO: Part 2 (done)
"""
def logout(tokens):
    global current_caregiver
    global current_patient

    if (current_caregiver is None and current_patient is None):
        print("Please Login First!")
        return

    if (current_caregiver is not None):
        current_caregiver = None
    elif (current_patient is not None):
        current_patient = None
    else:
        print("Please try again!")
        return

    print("Successfully logged out!")


def start():
    stop = False
    print()
    print(" *** Please enter one of the following commands *** ")
    print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)
    print("> create_caregiver <username> <password>")
    print("> login_patient <username> <password>")  # // TODO: implement login_patient (Part 1)
    print("> login_caregiver <username> <password>")
    print("> search_caregiver_schedule <date>")  # // TODO: implement search_caregiver_schedule (Part 2)
    print("> reserve <date> <vaccine>")  # // TODO: implement reserve (Part 2)
    print("> upload_availability <date>")
    print("> cancel <appointment_id>")  # // TODO: implement cancel (extra credit)
    print("> add_doses <vaccine> <number>")
    print("> show_appointments")  # // TODO: implement show_appointments (Part 2)
    print("> logout")  # // TODO: implement logout (Part 2)
    print("> Quit")
    print()
    while not stop:
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break

        # response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == cancel:
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit" or operation == "Quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()
