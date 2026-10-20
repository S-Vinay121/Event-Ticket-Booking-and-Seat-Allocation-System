import mysql.connector

def setup_database():
    try:
        # Connect to MySQL server without specifying database to create it
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root123"
        )
        cursor = conn.cursor()

        # Database Setup
        print("Setting up database...")
        cursor.execute("DROP DATABASE IF EXISTS DBMSPROJECT;")
        cursor.execute("CREATE DATABASE DBMSPROJECT;")
        cursor.execute("USE DBMSPROJECT;")

        # Tables Setup
        print("Creating tables...")
        tables = [
            """
            CREATE TABLE USERS (
                user_id INT PRIMARY KEY AUTO_INCREMENT,
                user_name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                phone_number VARCHAR(15) UNIQUE,
                password VARCHAR(100) NOT NULL,
                date_of_birth DATE NOT NULL
            );
            """,
            """
            CREATE TABLE ADMIN (
                admin_id INT PRIMARY KEY,
                admin_role VARCHAR(50) NOT NULL,
                FOREIGN KEY (admin_id) REFERENCES USERS(user_id) ON DELETE CASCADE
            );
            """,
            """
            CREATE TABLE CUSTOMER (
                customer_id INT PRIMARY KEY,
                FOREIGN KEY (customer_id) REFERENCES USERS(user_id) ON DELETE CASCADE
            );
            """,
            """
            CREATE TABLE VENUE (
                venue_id INT PRIMARY KEY AUTO_INCREMENT,
                venue_name VARCHAR(100) NOT NULL,
                city VARCHAR(50),
                state VARCHAR(50),
                country VARCHAR(50),
                capacity INT CHECK (capacity > 0)
            );
            """,
            """
            CREATE TABLE EVENT (
                event_id INT PRIMARY KEY AUTO_INCREMENT,
                event_name VARCHAR(100) NOT NULL,
                event_type VARCHAR(50),
                event_date DATE NOT NULL,
                start_time TIME NOT NULL,
                end_time TIME NOT NULL,
                admin_id INT NOT NULL,
                venue_id INT NOT NULL,
                FOREIGN KEY (admin_id) REFERENCES ADMIN(admin_id) ON DELETE CASCADE,
                FOREIGN KEY (venue_id) REFERENCES VENUE(venue_id) ON DELETE CASCADE,
                CHECK (end_time > start_time)
            );
            """,
            """
            CREATE TABLE SEAT (
                seat_id INT PRIMARY KEY AUTO_INCREMENT,
                seat_number VARCHAR(10) NOT NULL,
                seat_type VARCHAR(20) CHECK (seat_type IN ('VIP', 'Premium', 'Standard')),
                venue_id INT NOT NULL,
                FOREIGN KEY (venue_id) REFERENCES VENUE(venue_id) ON DELETE CASCADE,
                UNIQUE (seat_number, venue_id)
            );
            """,
            """
            CREATE TABLE TICKET (
                ticket_id INT PRIMARY KEY AUTO_INCREMENT,
                booking_status VARCHAR(20) DEFAULT 'Pending' CHECK (booking_status IN ('Booked', 'Cancelled', 'Pending')),
                event_id INT NOT NULL,
                customer_id INT NOT NULL,
                seat_id INT NOT NULL,
                FOREIGN KEY (event_id) REFERENCES EVENT(event_id) ON DELETE CASCADE,
                FOREIGN KEY (customer_id) REFERENCES CUSTOMER(customer_id) ON DELETE CASCADE,
                FOREIGN KEY (seat_id) REFERENCES SEAT(seat_id) ON DELETE CASCADE,
                UNIQUE (event_id, seat_id)
            );
            """,
            """
            CREATE TABLE PAYMENT (
                payment_id INT PRIMARY KEY AUTO_INCREMENT,
                payment_date DATE NOT NULL,
                payment_method VARCHAR(50),
                payment_amount DECIMAL(10,2) CHECK (payment_amount > 0),
                payment_status VARCHAR(20) CHECK (payment_status IN ('Success', 'Failed', 'Pending')),
                ticket_id INT UNIQUE,
                FOREIGN KEY (ticket_id) REFERENCES TICKET(ticket_id) ON DELETE CASCADE
            );
            """
        ]
        
        for table_query in tables:
            cursor.execute(table_query)

        # Procedures
        print("Creating procedures...")
        cursor.execute("DROP PROCEDURE IF EXISTS BookTicket;")
        book_ticket_proc = """
        CREATE PROCEDURE BookTicket(
            IN p_event_id INT,
            IN p_customer_id INT,
            IN p_seat_id INT
        )
        BEGIN
            DECLARE seat_count INT;

            IF NOT EXISTS (SELECT 1 FROM EVENT WHERE event_id = p_event_id) THEN
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Event does not exist';
            END IF;

            IF NOT EXISTS (SELECT 1 FROM CUSTOMER WHERE customer_id = p_customer_id) THEN
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Customer does not exist';
            END IF;

            IF NOT EXISTS (SELECT 1 FROM SEAT WHERE seat_id = p_seat_id) THEN
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Seat does not exist';
            END IF;

            SELECT COUNT(*) INTO seat_count FROM TICKET
            WHERE event_id = p_event_id AND seat_id = p_seat_id;

            IF seat_count > 0 THEN
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Seat already booked for this event';
            END IF;

            INSERT INTO TICKET(booking_status, event_id, customer_id, seat_id)
            VALUES ('Pending', p_event_id, p_customer_id, p_seat_id);
        END
        """
        cursor.execute(book_ticket_proc)

        cursor.execute("DROP PROCEDURE IF EXISTS MakePayment;")
        make_payment_proc = """
        CREATE PROCEDURE MakePayment(
            IN p_ticket_id INT,
            IN p_amount DECIMAL(10,2),
            IN p_method VARCHAR(50)
        )
        BEGIN
            DECLARE ticket_exists INT;

            SELECT COUNT(*) INTO ticket_exists FROM TICKET
            WHERE ticket_id = p_ticket_id;

            IF ticket_exists = 0 THEN
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Ticket does not exist';
            END IF;

            INSERT INTO PAYMENT(payment_date, payment_method, payment_amount, payment_status, ticket_id)
            VALUES (CURRENT_DATE, p_method, p_amount, 'Success', p_ticket_id);

            UPDATE TICKET
            SET booking_status = 'Booked'
            WHERE ticket_id = p_ticket_id;
        END
        """
        cursor.execute(make_payment_proc)


        # Functions
        print("Creating functions...")
        cursor.execute("DROP FUNCTION IF EXISTS GetCustomerTotalSpend;")
        get_spend_func = """
        CREATE FUNCTION GetCustomerTotalSpend(p_cust_id INT) RETURNS DECIMAL(10,2) DETERMINISTIC
        BEGIN
            DECLARE total_sum DECIMAL(10,2);
            SELECT SUM(payment_amount) INTO total_sum FROM PAYMENT P 
            JOIN TICKET T ON P.ticket_id = T.ticket_id 
            WHERE T.customer_id = p_cust_id AND P.payment_status = 'Success';
            RETURN IFNULL(total_sum, 0.00);
        END
        """
        cursor.execute(get_spend_func)

        cursor.execute("DROP FUNCTION IF EXISTS CheckEventAvailability;")
        check_availability_func = """
        CREATE FUNCTION CheckEventAvailability(p_ev_id INT) RETURNS INT DETERMINISTIC
        BEGIN
            DECLARE total_cap INT;
            DECLARE booked_count INT;
            SELECT V.capacity INTO total_cap FROM VENUE V JOIN EVENT E ON V.venue_id = E.venue_id WHERE E.event_id = p_ev_id;
            SELECT COUNT(*) INTO booked_count FROM TICKET WHERE event_id = p_ev_id AND booking_status IN ('Booked', 'Pending');
            RETURN IFNULL(total_cap - booked_count, 0);
        END
        """
        cursor.execute(check_availability_func)


        # Triggers
        print("Creating triggers...")
        cursor.execute("DROP TRIGGER IF EXISTS AutoConfirmTicket;")
        auto_confirm_trigger = """
        CREATE TRIGGER AutoConfirmTicket
        AFTER UPDATE ON PAYMENT
        FOR EACH ROW
        BEGIN
            IF NEW.payment_status = 'Success' THEN
                UPDATE TICKET SET booking_status = 'Booked' WHERE ticket_id = NEW.ticket_id;
            END IF;
        END
        """
        cursor.execute(auto_confirm_trigger)

        cursor.execute("DROP TRIGGER IF EXISTS ValidateBookingDate;")
        validate_booking_trigger = """
        CREATE TRIGGER ValidateBookingDate
        BEFORE INSERT ON TICKET
        FOR EACH ROW
        BEGIN
            DECLARE e_date DATE;
            SELECT event_date INTO e_date FROM EVENT WHERE event_id = NEW.event_id;
            IF e_date < CURRENT_DATE THEN
                SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Booking Error: The event date has already passed.';
            END IF;
        END
        """
        cursor.execute(validate_booking_trigger)

        # Inserting dummy data
        print("Inserting dummy data...")
        dummy_data = [
            "INSERT INTO USERS (user_name, email, phone_number, password, date_of_birth) VALUES ('Admin User', 'admin@mail.com', '1234567890', 'admin123', '1990-01-01');",
            "INSERT INTO ADMIN (admin_id, admin_role) VALUES (1, 'Super Admin');",
            "INSERT INTO VENUE (venue_name, city, state, country, capacity) VALUES ('Pune Pavilion', 'Pune', 'Maharashtra', 'India', 30);",
            "INSERT INTO VENUE (venue_name, city, state, country, capacity) VALUES ('Mumbai Arena', 'Mumbai', 'Maharashtra', 'India', 30);",
            "INSERT INTO EVENT (event_name, event_type, event_date, start_time, end_time, admin_id, venue_id) VALUES ('Coldplay Concert', 'Music', '2027-12-01', '18:00:00', '22:00:00', 1, 2);",
            "INSERT INTO EVENT (event_name, event_type, event_date, start_time, end_time, admin_id, venue_id) VALUES ('Arijit Singh Live', 'Music', '2027-11-15', '19:00:00', '23:00:00', 1, 1);",
            "INSERT INTO EVENT (event_name, event_type, event_date, start_time, end_time, admin_id, venue_id) VALUES ('Standup Comedy: Zakir Khan', 'Comedy', '2026-10-10', '20:00:00', '22:00:00', 1, 1);",
        ]

        for query in dummy_data:
            cursor.execute(query)

        print("Generating dummy seats...")
        for j in range(1, 3): # Venues 1 and 2
            for i in range(1, 31):
                seat_type = 'VIP' if i <= 5 else ('Premium' if i <= 15 else 'Standard')
                cursor.execute(f"INSERT INTO SEAT (seat_number, seat_type, venue_id) VALUES ('S{i}', '{seat_type}', {j})")

        conn.commit()
        cursor.close()
        conn.close()
        print("Database setup complete!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

if __name__ == '__main__':
    setup_database()
