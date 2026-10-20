# Event Ticket Booking and Seat Allocation System

An enterprise-grade, desktop-based Event Ticket Booking and Seat Allocation System engineered with **Python (Tkinter)** and **MySQL**. The system features relational database schema design, stored procedures, ACID transaction handling, automated triggers, role-based access control (RBAC), and dynamic seat reservation with tiered seating architectures.

---

## Key Features

### User & Customer Experience
- **Interactive Seat Selection Grid**: Dynamic visual matrix displaying real-time seat availability (`Available` vs `Booked`) with categorized tiers (**VIP**, **Premium**, and **Standard**).
- **Transactional Booking Flow**: Multi-stage reservation workflow (`Pending` reservation $\rightarrow$ Payment Checkout $\rightarrow$ `Booked` confirmation).
- **Payment Processing**: Integrated checkout supporting UPI and Card transactions with transaction logging.
- **Customer Dashboard & Loyalty Program**:
  - View upcoming and historical ticket reservations.
  - Spend tracking using stored database functions.
  - Dynamic loyalty tier assignment (e.g., **Gold Member** vs. **Standard Member**).
  - One-click ticket cancellation with state updates.

### Admin Control Center
- **Event Lifecycle Management**: Schedule events, link venues, and configure event timelines.
- **Automated Outdated Event Cleanup**: Batch purge functionality to clear expired events and synchronize schedules.
- **Venue & Dynamic Seat Provisioning**: Create venues with customized capacities; automatically seeds tiered seating layouts (`S1`, `S2`, ...).
- **Revenue Analytics**: Real-time revenue calculations per event computed directly via MySQL joins and aggregations.
- **Global Ticket Audit**: Comprehensive overview of all reservations across customers and venues.

---

## Database Architecture

The backend is built on **MySQL** with strong relational integrity, referential constraints, stored routines, and triggers.

![Entity Relationship Diagram](ER%20Diagram.png)

### Relational Schema Design
- **`USERS`**: Master entity storing user profiles, credentials, contact details, and DOB.
- **`ADMIN` / `CUSTOMER`**: Role specialization via primary-key to foreign-key inheritance (`ON DELETE CASCADE`).
- **`VENUE`**: Stores physical venues, geographical locations, and maximum audience capacities.
- **`EVENT`**: Associates schedules, start/end time validation (`CHECK (end_time > start_time)`), administrators, and assigned venues.
- **`SEAT`**: Granular seat records tied to venues with uniqueness constraints `UNIQUE(seat_number, venue_id)` and seat classification (`VIP`, `Premium`, `Standard`).
- **`TICKET`**: Core booking entity linking event, customer, and seat with unique constraint `UNIQUE(event_id, seat_id)` to prevent double booking.
- **`PAYMENT`**: Financial transaction ledger linked 1:1 with tickets (`payment_status IN ('Success', 'Failed', 'Pending')`).

### Advanced Database Objects
- **Stored Procedures**:
  - `BookTicket(p_event_id, p_customer_id, p_seat_id)`: Atomic procedure ensuring seat and event validity before generating reservations. Prevents race conditions and duplicate bookings.
  - `MakePayment(p_ticket_id, p_amount, p_method)`: Logs payment success and promotes ticket status to `Booked`.
- **Stored Functions**:
  - `CheckEventAvailability(p_ev_id)`: Computes available capacity dynamically (`VENUE.capacity - COUNT(TICKET)`).
  - `GetCustomerTotalSpend(p_cust_id)`: Calculates cumulative successful expenditures for loyalty metrics.
- **Triggers**:
  - `ValidateBookingDate`: `BEFORE INSERT ON TICKET` trigger preventing bookings on past dates (`SIGNAL SQLSTATE '45000'`).
  - `AutoConfirmTicket`: `AFTER UPDATE ON PAYMENT` trigger that sets ticket status to `Booked` when payment succeeds.

---

## Technology Stack

- **Language**: Python 3.8+
- **UI Framework**: Tkinter / `ttk` (Modern dark surface design system)
- **Database**: MySQL 8.0+
- **Driver**: `mysql-connector-python`

---

## Project Structure

```
Event-Ticket-Booking-and-Seat-Allocation-System/
├── app.py             # Desktop GUI application, routing, and controller logic
├── database.py        # Database access layer (DAL) and query interfaces
├── setup_db.py        # Database schema initialization, DDL, triggers, and seed data
├── requirements.txt   # Python project dependencies
└── README.md          # Project documentation
```

---

## Getting Started

### 1. Prerequisites
- Python 3.8 or higher installed.
- MySQL Server (v8.0 or newer) running locally on port `3306`.

### 2. Configure Database Credentials
Ensure your local MySQL credentials match the configuration in `database.py` and `setup_db.py`:
- **Host**: `localhost`
- **User**: `root`
- **Password**: `root123` *(update if your local password differs)*

### 3. Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/S-Vinay121/Event-Ticket-Booking-and-Seat-Allocation-System.git
   cd Event-Ticket-Booking-and-Seat-Allocation-System
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 4. Initialize Database
Run the setup script to drop/recreate `DBMSPROJECT`, configure tables, functions, procedures, triggers, and dummy data:
```bash
python setup_db.py
```

### 5. Launch the Application
Start the desktop application:
```bash
python app.py
```

---

## Default Credentials

| Role | Email | Password |
| :--- | :--- | :--- |
| **Admin** | `admin@mail.com` | `admin123` |
| **New Customer** | Create via the in-app **"Create an Account"** register view | *Custom* |

---

## License

This project is open-source and available under the [MIT License](LICENSE).
