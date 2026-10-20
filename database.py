import mysql.connector
from datetime import datetime

class Database:
    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.password = "root123"
        self.database = "DBMSPROJECT"

    def connect(self):
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )

    def login(self, email, password):
        conn = self.connect()
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM USERS WHERE email = %s AND password = %s"
            cursor.execute(query, (email, password))
            user = cursor.fetchone()
            
            if user:
                # Check if admin
                a_query = "SELECT * FROM ADMIN WHERE admin_id = %s"
                cursor.execute(a_query, (user['user_id'],))
                if cursor.fetchone():
                    user['role'] = 'admin'
                else:
                    user['role'] = 'customer'
                return user
            return None
        finally:
            cursor.close()
            conn.close()

    def register(self, name, email, phone, password, dob):
        conn = self.connect()
        cursor = conn.cursor()
        try:
            # Insert into USERS
            query = "INSERT INTO USERS (user_name, email, phone_number, password, date_of_birth) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, (name, email, phone, password, dob))
            user_id = cursor.lastrowid
            
            # Auto-register as CUSTOMER
            c_query = "INSERT INTO CUSTOMER (customer_id) VALUES (%s)"
            cursor.execute(c_query, (user_id,))
            
            conn.commit()
            return True, "Registration successful"
        except mysql.connector.Error as err:
            return False, str(err)
        finally:
            cursor.close()
            conn.close()

    def get_events(self, city=None):
        conn = self.connect()
        cursor = conn.cursor(dictionary=True)
        try:
            if city:
                query = """
                SELECT E.*, V.venue_name, V.city, V.state 
                FROM EVENT E JOIN VENUE V ON E.venue_id = V.venue_id 
                WHERE V.city = %s AND E.event_date >= CURRENT_DATE
                ORDER BY E.event_date ASC
                """
                cursor.execute(query, (city,))
            else:
                query = """
                SELECT E.*, V.venue_name, V.city, V.state 
                FROM EVENT E JOIN VENUE V ON E.venue_id = V.venue_id 
                WHERE E.event_date >= CURRENT_DATE
                ORDER BY E.event_date ASC
                """
                cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def get_seats(self, event_id, venue_id):
        conn = self.connect()
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
            SELECT S.*, 
            CASE WHEN T.ticket_id IS NOT NULL THEN 'Booked' ELSE 'Available' END AS status
            FROM SEAT S
            LEFT JOIN TICKET T ON S.seat_id = T.seat_id AND T.event_id = %s AND T.booking_status != 'Cancelled'
            WHERE S.venue_id = %s
            """
            cursor.execute(query, (event_id, venue_id))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def get_event_availability(self, event_id):
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT CheckEventAvailability(%s)", (event_id,))
            result = cursor.fetchone()
            return result[0] if result else 0
        finally:
            cursor.close()
            conn.close()

    def get_total_spend(self, customer_id):
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT GetCustomerTotalSpend(%s)", (customer_id,))
            result = cursor.fetchone()
            return result[0] if result else 0.00
        finally:
            cursor.close()
            conn.close()

    def book_ticket(self, event_id, customer_id, seat_id):
        conn = self.connect()
        try:
            cursor = conn.cursor()
            args = (event_id, customer_id, seat_id)
            cursor.callproc('BookTicket', args)
            conn.commit()
            
            # Since Proc succeeded, get the ticket_id
            cursor.execute("SELECT ticket_id FROM TICKET WHERE event_id = %s AND seat_id = %s AND customer_id = %s AND booking_status = 'Pending'", (event_id, seat_id, customer_id))
            ticket = cursor.fetchone()
            cursor.close()
            return True, ticket[0] if ticket else None
        except mysql.connector.Error as err:
            return False, str(err)
        finally:
            conn.close()

    def make_payment(self, ticket_id, amount, method):
        conn = self.connect()
        try:
            cursor = conn.cursor()
            args = (ticket_id, amount, method)
            cursor.callproc('MakePayment', args)
            conn.commit()
            cursor.close()
            return True, "Payment Successful"
        except mysql.connector.Error as err:
            return False, str(err)
        finally:
            conn.close()

    def cancel_ticket(self, ticket_id):
        conn = self.connect()
        try:
            cursor = conn.cursor()
            query = "UPDATE TICKET SET booking_status = 'Cancelled' WHERE ticket_id = %s"
            cursor.execute(query, (ticket_id,))
            conn.commit()
            return True
        except mysql.connector.Error as err:
            return False
        finally:
            cursor.close()
            conn.close()

    def get_user_tickets(self, customer_id):
        conn = self.connect()
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
            SELECT T.*, E.event_name, E.event_date, E.start_time, S.seat_number, S.seat_type, V.venue_name
            FROM TICKET T
            JOIN EVENT E ON T.event_id = E.event_id
            JOIN SEAT S ON T.seat_id = S.seat_id
            JOIN VENUE V ON S.venue_id = V.venue_id
            WHERE T.customer_id = %s
            ORDER BY E.event_date DESC
            """
            cursor.execute(query, (customer_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def get_failed_payments(self):
        conn = self.connect()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM PAYMENT WHERE payment_status = 'Failed'")
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def get_all_events(self):
        conn = self.connect()
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
            SELECT E.*, V.venue_name, V.city 
            FROM EVENT E JOIN VENUE V ON E.venue_id = V.venue_id 
            ORDER BY E.event_date ASC
            """
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
            
    def get_event_revenue(self, event_id):
        conn = self.connect()
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
            SELECT SUM(payment_amount) AS Total_Revenue 
            FROM PAYMENT P JOIN TICKET T ON P.ticket_id = T.ticket_id 
            WHERE T.event_id = %s AND P.payment_status = 'Success'
            """
            cursor.execute(query, (event_id,))
            res = cursor.fetchone()
            return res['Total_Revenue'] if res and res['Total_Revenue'] else 0.00
        finally:
            cursor.close()
            conn.close()
            
    def delete_outdated_events(self):
        conn = self.connect()
        cursor = conn.cursor()
        try:
            # Modified to use current date
            cursor.execute("DELETE FROM EVENT WHERE event_date < CURRENT_DATE")
            deleted = cursor.rowcount
            conn.commit()
            return deleted
        finally:
            cursor.close()
            conn.close()

    def get_vip_customers(self):
        conn = self.connect()
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
            SELECT DISTINCT U.user_name, U.phone_number 
            FROM USERS U JOIN TICKET T ON U.user_id = T.customer_id 
            JOIN SEAT S ON T.seat_id = S.seat_id 
            WHERE S.seat_type = 'VIP'
            """
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def get_venues(self):
        conn = self.connect()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM VENUE")
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def update_venue_capacity(self, venue_id, new_capacity):
        conn = self.connect()
        cursor = conn.cursor()
        try:
            query = "UPDATE VENUE SET capacity = %s WHERE venue_id = %s"
            cursor.execute(query, (new_capacity, venue_id))
            conn.commit()
            return True
        except mysql.connector.Error:
            return False
        finally:
            cursor.close()
            conn.close()

    def add_event(self, event_name, event_type, event_date, start_time, end_time, admin_id, venue_id):
        conn = self.connect()
        cursor = conn.cursor()
        try:
            query = "INSERT INTO EVENT (event_name, event_type, event_date, start_time, end_time, admin_id, venue_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (event_name, event_type, event_date, start_time, end_time, admin_id, venue_id))
            conn.commit()
            return True, "Event Added"
        except Exception as err:
            return False, str(err)
        finally:
            cursor.close()
            conn.close()

    def delete_event(self, event_id):
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM EVENT WHERE event_id = %s", (event_id,))
            conn.commit()
            return True
        except Exception:
            return False
        finally:
            cursor.close()
            conn.close()

    def get_all_booked_tickets(self):
        conn = self.connect()
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT T.booking_status, T.ticket_id, E.event_name, S.seat_number, S.seat_type, U.user_name, U.email FROM TICKET T JOIN EVENT E ON T.event_id = E.event_id JOIN SEAT S ON T.seat_id = S.seat_id JOIN USERS U ON T.customer_id = U.user_id ORDER BY E.event_date DESC, S.seat_number ASC"
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def add_venue(self, name, city, state, country, capacity):
        conn = self.connect()
        cursor = conn.cursor()
        try:
            query = "INSERT INTO VENUE (venue_name, city, state, country, capacity) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, (name, city, state, country, capacity))
            venue_id = cursor.lastrowid
            # Also generate seats for this venue
            for i in range(1, int(capacity) + 1):
                seat_type = 'VIP' if i <= 5 else ('Premium' if i <= 15 else 'Standard')
                cursor.execute("INSERT INTO SEAT (seat_number, seat_type, venue_id) VALUES (%s, %s, %s)", (f"S{i}", seat_type, venue_id))
            conn.commit()
            return True, "Venue added"
        except mysql.connector.Error as err:
            return False, str(err)
        finally:
            cursor.close()
            conn.close()

    def delete_venue(self, venue_id):
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM VENUE WHERE venue_id = %s", (venue_id,))
            conn.commit()
            return True
        except mysql.connector.Error:
            return False
        finally:
            cursor.close()
            conn.close()
