import tkinter as tk
from tkinter import ttk, messagebox
from database import Database

# --- Styles and Colors ---
BG_COLOR = "#0D1117"  # Dark UI
CARD_COLOR = "#161B22"
TEXT_COLOR = "#C9D1D9"
ACCENT_COLOR = "#F83F3F"
HEADER_COLOR = "#FFFFFF"

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("EventTicketing")
        self.geometry("1000x700")
        self.configure(bg=BG_COLOR)
        self.db = Database()
        self.current_user = None

        # Setup Styling
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure custom styles
        self.style.configure("TFrame", background=BG_COLOR)
        self.style.configure("Card.TFrame", background=CARD_COLOR)
        self.style.configure("TLabel", background=BG_COLOR, foreground=TEXT_COLOR, font=("Helvetica", 12))
        self.style.configure("Header.TLabel", background=BG_COLOR, foreground=HEADER_COLOR, font=("Helvetica", 20, "bold"))
        self.style.configure("CardLabel.TLabel", background=CARD_COLOR, foreground=TEXT_COLOR, font=("Helvetica", 12))
        
        self.style.configure("TButton", 
                             background=ACCENT_COLOR, 
                             foreground=HEADER_COLOR, 
                             font=("Helvetica", 12, "bold"),
                             borderwidth=0, 
                             padding=10)
        self.style.map("TButton", background=[("active", "#D73030")])
        
        self.frames = {}
        self.create_frames()
        self.show_frame("LoginView")

    def create_frames(self):
        for F in (LoginView, RegisterView, EventBrowserView, SeatSelectionView, PaymentView, DashboardView, AdminDashboardView, AdminVenuesView, AdminTicketsView):
            page_name = F.__name__
            frame = F(parent=self, controller=self)
            self.frames[page_name] = frame
            # put all of the pages in the same location; 
            # the one on the top of the stacking order will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")
            
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def show_frame(self, page_name, **kwargs):
        frame = self.frames[page_name]
        # Allow passing context to frames when they are loaded
        if hasattr(frame, 'on_show'):
            frame.on_show(**kwargs)
        frame.tkraise()

    def logout(self):
        self.current_user = None
        self.show_frame("LoginView")

class LoginView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Center content
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)

        card = ttk.Frame(self, style="Card.TFrame", padding=30)
        card.grid(row=1, column=1)

        lbl_title = ttk.Label(card, text="Welcome Back", style="Header.TLabel", background=CARD_COLOR)
        lbl_title.pack(pady=(0, 20))

        ttk.Label(card, text="Email", background=CARD_COLOR).pack(anchor="w")
        self.entry_email = ttk.Entry(card, width=30, font=("Helvetica", 12))
        self.entry_email.pack(pady=(0, 15), ipady=5)

        ttk.Label(card, text="Password", background=CARD_COLOR).pack(anchor="w")
        self.entry_pass = ttk.Entry(card, show="*", width=30, font=("Helvetica", 12))
        self.entry_pass.pack(pady=(0, 20), ipady=5)

        btn_login = ttk.Button(card, text="Log In", command=self.login)
        btn_login.pack(fill="x", pady=(0, 10))

        btn_reg = ttk.Button(card, text="Create an Account", command=lambda: controller.show_frame("RegisterView"))
        btn_reg.pack(fill="x")

    def login(self):
        email = self.entry_email.get()
        pwd = self.entry_pass.get()
        user = self.controller.db.login(email, pwd)
        if user:
            self.controller.current_user = user
            if user.get('role') == 'admin':
                self.controller.show_frame("AdminDashboardView")
            else:
                self.controller.show_frame("EventBrowserView")
        else:
            messagebox.showerror("Error", "Invalid credentials")

class RegisterView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)

        card = ttk.Frame(self, style="Card.TFrame", padding=30)
        card.grid(row=1, column=1)

        ttk.Label(card, text="Register", style="Header.TLabel", background=CARD_COLOR).grid(row=0, column=0, columnspan=2, pady=(0, 20))

        fields = ["Name", "Email", "Phone", "Password", "DOB (YYYY-MM-DD)"]
        self.entries = {}
        for i, field in enumerate(fields):
            ttk.Label(card, text=field, background=CARD_COLOR).grid(row=i+1, column=0, sticky="w", pady=5)
            ent = ttk.Entry(card, width=25, show="*" if "Password" in field else "")
            ent.grid(row=i+1, column=1, pady=5)
            self.entries[field] = ent

        btn_reg = ttk.Button(card, text="Sign Up", command=self.register)
        btn_reg.grid(row=10, column=0, columnspan=2, pady=(20, 10), sticky="ew")

        btn_back = ttk.Button(card, text="Back to Login", command=lambda: controller.show_frame("LoginView"))
        btn_back.grid(row=11, column=0, columnspan=2, sticky="ew")

    def register(self):
        name = self.entries["Name"].get()
        email = self.entries["Email"].get()
        phone = self.entries["Phone"].get()
        pwd = self.entries["Password"].get()
        dob = self.entries["DOB (YYYY-MM-DD)"].get()
        
        success, msg = self.controller.db.register(name, email, phone, pwd, dob)
        if success:
            messagebox.showinfo("Success", "Account created successfully!")
            self.controller.show_frame("LoginView")
        else:
            messagebox.showerror("Error", msg)

class Navbar(ttk.Frame):
    def __init__(self, parent, controller, title="Events"):
        super().__init__(parent, style="Card.TFrame", padding=10)
        
        ttk.Label(self, text="EventTicketing", style="Header.TLabel", background=CARD_COLOR, foreground=ACCENT_COLOR).pack(side="left", padx=10)
        
        lbl_title = ttk.Label(self, text=title, font=("Helvetica", 14, "bold"), background=CARD_COLOR)
        lbl_title.pack(side="left", padx=30)
        
        ttk.Button(self, text="Logout", command=controller.logout).pack(side="right", padx=5)
        
        if controller.current_user and controller.current_user.get('role') == 'admin':
            ttk.Button(self, text="Tickets", command=lambda: controller.show_frame("AdminTicketsView")).pack(side="right", padx=5)
            ttk.Button(self, text="Venues", command=lambda: controller.show_frame("AdminVenuesView")).pack(side="right", padx=5)
            ttk.Button(self, text="Admin Home", command=lambda: controller.show_frame("AdminDashboardView")).pack(side="right", padx=5)
        else:
            ttk.Button(self, text="Dashboard", command=lambda: controller.show_frame("DashboardView")).pack(side="right", padx=5)
            ttk.Button(self, text="Events", command=lambda: controller.show_frame("EventBrowserView")).pack(side="right", padx=5)

class EventBrowserView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
    def on_show(self, **kwargs):
        for widget in self.winfo_children():
            widget.destroy()

        Navbar(self, self.controller, title="Browse Events").pack(fill="x")
        
        content = ttk.Frame(self, padding=20)
        content.pack(fill="both", expand=True)
        
        events = self.controller.db.get_events()
        
        if not events:
            ttk.Label(content, text="No upcoming events available.").pack(pady=40)
            return

        # Simple List display
        canvas = tk.Canvas(content, bg=BG_COLOR, highlightthickness=0)
        scrollbar = ttk.Scrollbar(content, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style="TFrame")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def on_canvas_configure(event):
            canvas.itemconfig(window_id, width=event.width)
        canvas.bind("<Configure>", on_canvas_configure)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Center container
        container = ttk.Frame(scrollable_frame)
        container.pack(fill="y", expand=False, anchor="n")
        
        for e in events:
            card = ttk.Frame(container, style="Card.TFrame", padding=15)
            card.pack(fill="x", pady=10, padx=10)
            
            ttk.Label(card, text=e['event_name'], style="Header.TLabel", background=CARD_COLOR).pack(anchor="w")
            info = f"{e['event_date']} | {e['start_time']} to {e['end_time']} | {e['venue_name']}, {e['city']}"
            ttk.Label(card, text=info, style="CardLabel.TLabel").pack(anchor="w", pady=5)
            
            # Use dynamic function for availability
            avail = self.controller.db.get_event_availability(e['event_id'])
            ttk.Label(card, text=f"Available Seats: {avail}", foreground="#4ADE80", background=CARD_COLOR).pack(anchor="w")
            
            btn = ttk.Button(card, text="Book Tickets", 
                             command=lambda ev=e: self.controller.show_frame("SeatSelectionView", event=ev))
            btn.pack(anchor="e")

class SeatSelectionView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.event_context = None

    def on_show(self, **kwargs):
        self.event_context = kwargs.get('event')
        for widget in self.winfo_children():
            widget.destroy()
            
        Navbar(self, self.controller, title=f"Select Seats - {self.event_context['event_name']}").pack(fill="x")
        
        canvas = tk.Canvas(self, bg=BG_COLOR, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style="TFrame")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def on_canvas_configure(event):
            canvas.itemconfig(window_id, width=event.width)
        canvas.bind("<Configure>", on_canvas_configure)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        container = ttk.Frame(scrollable_frame)
        container.pack(fill="y", expand=False, anchor="n")
        
        content = ttk.Frame(container, padding=20)
        content.pack(fill="both", expand=True)

        seats = self.controller.db.get_seats(self.event_context['event_id'], self.event_context['venue_id'])
        
        grid_frame = ttk.Frame(content, style="TFrame")
        grid_frame.pack(pady=20)
        
        row, col = 0, 0
        for s in seats:
            color = "#1F2937" # Grey for available
            state = tk.NORMAL
            if s['status'] == 'Booked':
                color = "#4B5563"
                state = tk.DISABLED
            
            # Simple button coloring setup
            btn = tk.Button(grid_frame, text=f"{s['seat_number']}\n{s['seat_type']}", 
                            bg=color, fg=TEXT_COLOR, width=10, height=3, state=state,
                            command=lambda seat=s: self.proceed_to_payment(seat))
            btn.grid(row=row, column=col, padx=5, pady=5)
            col += 1
            if col > 5:
                col = 0
                row += 1

    def proceed_to_payment(self, seat):
        # Book the ticket using pending state
        success, ticket_id = self.controller.db.book_ticket(self.event_context['event_id'], self.controller.current_user['user_id'], seat['seat_id'])
        if success and ticket_id:
            self.controller.show_frame("PaymentView", ticket_id=ticket_id, event=self.event_context, seat=seat)
        else:
            messagebox.showerror("Error", f"Failed to reserve seat: {ticket_id}")

class PaymentView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

    def on_show(self, **kwargs):
        self.ticket_id = kwargs.get('ticket_id')
        self.event = kwargs.get('event')
        self.seat = kwargs.get('seat')
        
        for widget in self.winfo_children():
            widget.destroy()
            
        Navbar(self, self.controller, title="Checkout").pack(fill="x")
        content = ttk.Frame(self, padding=20)
        content.pack(fill="both", expand=True)

        card = ttk.Frame(content, style="Card.TFrame", padding=30)
        card.pack(pady=40)

        price = 1000 if self.seat['seat_type'] == 'VIP' else (500 if self.seat['seat_type'] == 'Premium' else 250)

        ttk.Label(card, text="Order Summary", style="Header.TLabel", background=CARD_COLOR).pack(anchor="w", pady=(0,20))
        ttk.Label(card, text=f"Event: {self.event['event_name']}", background=CARD_COLOR).pack(anchor="w")
        ttk.Label(card, text=f"Seat: {self.seat['seat_number']} ({self.seat['seat_type']})", background=CARD_COLOR).pack(anchor="w", pady=5)
        ttk.Label(card, text=f"Amount to Pay: INR {price}", font=("Helvetica", 14, "bold"), background=CARD_COLOR, foreground="#4ADE80").pack(anchor="w", pady=15)

        ttk.Button(card, text="Complete Payment via UPI", command=lambda: self.pay(price, "UPI")).pack(fill="x", pady=5)
        ttk.Button(card, text="Complete Payment via Card", command=lambda: self.pay(price, "Card")).pack(fill="x")

    def pay(self, amount, method):
        success, msg = self.controller.db.make_payment(self.ticket_id, amount, method)
        if success:
            messagebox.showinfo("Success", "Payment confirmed! Ticket booked.")
            self.controller.show_frame("DashboardView")
        else:
            messagebox.showerror("Error", msg)

class DashboardView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

    def on_show(self, **kwargs):
        for widget in self.winfo_children():
            widget.destroy()
            
        Navbar(self, self.controller, title="My Dashboard").pack(fill="x")
        
        canvas = tk.Canvas(self, bg=BG_COLOR, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style="TFrame")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def on_canvas_configure(event):
            canvas.itemconfig(window_id, width=event.width)
        canvas.bind("<Configure>", on_canvas_configure)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        container = ttk.Frame(scrollable_frame)
        container.pack(fill="y", expand=False, anchor="n")
        
        content = ttk.Frame(container, padding=20)
        content.pack(fill="both", expand=True)
        
        user_id = self.controller.current_user['user_id']
        name = self.controller.current_user['user_name']
        total_spend = self.controller.db.get_total_spend(user_id)
        
        info_frame = ttk.Frame(content, style="Card.TFrame", padding=15)
        info_frame.pack(fill="x", pady=10)
        
        ttk.Label(info_frame, text=f"Hello, {name}!", style="Header.TLabel", background=CARD_COLOR).pack(anchor="w")
        
        status = "Gold Member 🌟" if total_spend > 2000 else "Standard Member"
        ttk.Label(info_frame, text=f"Total Spend: INR {total_spend}  |  Status: {status}", background=CARD_COLOR, font=("Helvetica", 12, "bold")).pack(anchor="w", pady=5)
        
        ttk.Label(content, text="My Tickets", style="Header.TLabel").pack(anchor="w", pady=(20, 10))
        
        tickets = self.controller.db.get_user_tickets(user_id)
        if not tickets:
            ttk.Label(content, text="You have no tickets yet.").pack(anchor="w")
        else:
            for t in tickets:
                card = ttk.Frame(content, style="Card.TFrame", padding=10)
                card.pack(fill="x", pady=5)
                
                info = f"{t['event_name']} | {t['event_date']} {t['start_time']} | Seat: {t['seat_number']} | Venue: {t['venue_name']}"
                ttk.Label(card, text=info, background=CARD_COLOR).pack(side="left")
                
                status_color = "#4ADE80" if t['booking_status'] == 'Booked' else ("#F83F3F" if t['booking_status'] == 'Cancelled' else "#FBBF24")
                ttk.Label(card, text=f"Status: {t['booking_status']}", foreground=status_color, background=CARD_COLOR).pack(side="right")
                
                if t['booking_status'] == 'Pending':
                    ttk.Button(card, text="Pay Now", command=lambda ticket=t: self.controller.show_frame(
                        "PaymentView", 
                        ticket_id=ticket['ticket_id'],
                        event={"event_name": ticket['event_name']},
                        seat={"seat_number": ticket['seat_number'], "seat_type": ticket['seat_type']}
                    )).pack(side="right", padx=10)
                    ttk.Button(card, text="Cancel", command=lambda tid=t['ticket_id']: self.cancel_ticket(tid)).pack(side="right", padx=10)
                elif t['booking_status'] == 'Booked':
                    ttk.Button(card, text="Cancel Ticket", command=lambda tid=t['ticket_id']: self.cancel_ticket(tid)).pack(side="right", padx=10)

    def cancel_ticket(self, ticket_id):
        if messagebox.askyesno("Confirm", "Are you sure you want to cancel this ticket?"):
            if self.controller.db.cancel_ticket(ticket_id):
                messagebox.showinfo("Success", "Ticket Cancelled")
                self.on_show() # refresh


class AdminDashboardView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

    def on_show(self, **kwargs):
        for widget in self.winfo_children():
            widget.destroy()
            
        Navbar(self, self.controller, title="Admin Control Center").pack(fill="x")
        
        canvas = tk.Canvas(self, bg=BG_COLOR, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style="TFrame")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Ensure scrollable frame matches canvas width to center content properly
        def on_canvas_configure(event):
            canvas.itemconfig(window_id, width=event.width)
        canvas.bind("<Configure>", on_canvas_configure)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Container layout inside the scrollable frame
        container = ttk.Frame(scrollable_frame)
        container.pack(fill="both", expand=True)
        
        content = ttk.Frame(container, padding=20)
        content.pack(fill="both", expand=True)
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)
        
        # --- LEFT PANE (Manage Events) ---
        left_pane = ttk.Frame(content)
        left_pane.grid(row=0, column=0, sticky="nsew", padx=20)
        
        ttk.Label(left_pane, text="Manage Events", style="Header.TLabel").pack(anchor="w", pady=(0,10))
        
        btn_del = ttk.Button(left_pane, text="Delete Outdated Events (Batch)", command=self.delete_outdated)
        btn_del.pack(anchor="w", pady=(0, 20))
        
        events = self.controller.db.get_all_events()
        for e in events:
            rev = self.controller.db.get_event_revenue(e['event_id'])
            card = ttk.Frame(left_pane, style="Card.TFrame", padding=10)
            card.pack(fill="x", pady=5)
            
            info = f"{e['event_name']} | {e['event_date']}"
            ttk.Label(card, text=info, font=("Helvetica", 12, "bold"), background=CARD_COLOR).pack(anchor="w")
            ttk.Label(card, text=f"Total Revenue Generated: INR {rev}", foreground="#4ADE80", background=CARD_COLOR).pack(anchor="w")
            ttk.Button(card, text="Delete Event", command=lambda eid=e['event_id']: self.delete_single_event(eid)).pack(anchor="e")

        # --- RIGHT PANE (Add New Event) ---
        right_pane = ttk.Frame(content)
        right_pane.grid(row=0, column=1, sticky="nsew", padx=20)

        ttk.Label(right_pane, text="Add New Event", style="Header.TLabel").pack(anchor="w", pady=(0,10))
        add_frame = ttk.Frame(right_pane, style="Card.TFrame", padding=20)
        add_frame.pack(fill="x")
        
        fields = ["Name", "Type (e.g. Music)", "Date (YYYY-MM-DD)", "Start Time (HH:MM)", "End Time (HH:MM)"]
        self.ev_entries = {}
        for i, field in enumerate(fields):
            ttk.Label(add_frame, text=field, background=CARD_COLOR).grid(row=i, column=0, sticky="w", pady=5)
            ent = ttk.Entry(add_frame, width=30)
            ent.grid(row=i, column=1, pady=5, padx=10)
            self.ev_entries[field] = ent
            
        ttk.Label(add_frame, text="Venue", background=CARD_COLOR).grid(row=len(fields), column=0, sticky="w", pady=5)
        
        venues = self.controller.db.get_venues()
        self.venue_combobox = ttk.Combobox(add_frame, width=28, state="readonly")
        if venues:
            self.venue_combobox['values'] = [f"{v['venue_id']} - {v['venue_name']}" for v in venues]
            self.venue_combobox.current(0)
        self.venue_combobox.grid(row=len(fields), column=1, pady=5, padx=10)
            
        ttk.Button(add_frame, text="Create Event", command=self.add_event).grid(row=len(fields)+1, column=0, columnspan=2, pady=(20,0))


    def delete_single_event(self, event_id):
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this event?"):
            if self.controller.db.delete_event(event_id):
                messagebox.showinfo("Success", "Event deleted.")
                self.on_show()

    def add_event(self):
        try:
            name = self.ev_entries["Name"].get()
            t = self.ev_entries["Type (e.g. Music)"].get()
            d = self.ev_entries["Date (YYYY-MM-DD)"].get()
            st = self.ev_entries["Start Time (HH:MM)"].get()
            et = self.ev_entries["End Time (HH:MM)"].get()
            
            venue_sel = self.venue_combobox.get()
            if not venue_sel:
                messagebox.showerror("Error", "Select a venue.")
                return
            vid = int(venue_sel.split(" - ")[0])
            
            success, msg = self.controller.db.add_event(name, t, d, st, et, 1, vid)
            if success:
                messagebox.showinfo("Success", "Event created!")
                self.on_show()
            else:
                messagebox.showerror("Error", msg)
        except Exception as e:
            messagebox.showerror("Error", "Check your inputs")

    def delete_outdated(self):
        count = self.controller.db.delete_outdated_events()
        messagebox.showinfo("Cleanup", f"Successfully deleted {count} outdated events.")
        self.on_show()


class AdminVenuesView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

    def on_show(self, **kwargs):
        for widget in self.winfo_children():
            widget.destroy()
            
        Navbar(self, self.controller, title="Manage Venues").pack(fill="x")
        
        content = ttk.Frame(self, padding=20)
        content.pack(fill="both", expand=True)
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)
        
        # Left side: Venue List
        left_pane = ttk.Frame(content)
        left_pane.grid(row=0, column=0, sticky="nsew", padx=10)
        
        ttk.Label(left_pane, text="Current Venues", style="Header.TLabel").pack(anchor="w", pady=(0,10))
        
        venues = self.controller.db.get_venues()
        if venues:
            for v in venues:
                card = ttk.Frame(left_pane, style="Card.TFrame", padding=10)
                card.pack(fill="x", pady=5)
                
                ttk.Label(card, text=f"{v['venue_id']} - {v['venue_name']}", font=("Helvetica", 12, "bold"), background=CARD_COLOR).pack(anchor="w")
                ttk.Label(card, text=f"{v['city']}, {v['state']} ({v['country']}) | Capacity: {v['capacity']}", background=CARD_COLOR).pack(anchor="w")
                ttk.Button(card, text="Delete Venue", command=lambda vid=v['venue_id']: self.delete_venue(vid)).pack(anchor="e", pady=(5,0))
        else:
            ttk.Label(left_pane, text="No venues found.").pack(anchor="w")

        # Right side: Add Venue Form
        right_pane = ttk.Frame(content)
        right_pane.grid(row=0, column=1, sticky="nsew", padx=10)

        ttk.Label(right_pane, text="Add New Venue", style="Header.TLabel").pack(anchor="w", pady=(0,10))
        add_frame = ttk.Frame(right_pane, style="Card.TFrame", padding=20)
        add_frame.pack(fill="x")
        
        fields = ["Name", "City", "State", "Country", "Capacity"]
        self.v_entries = {}
        for i, field in enumerate(fields):
            ttk.Label(add_frame, text=field, background=CARD_COLOR).grid(row=i, column=0, sticky="w", pady=5)
            ent = ttk.Entry(add_frame, width=30)
            ent.grid(row=i, column=1, pady=5, padx=10)
            self.v_entries[field] = ent
            
        ttk.Button(add_frame, text="Create Venue", command=self.add_venue).grid(row=len(fields), column=0, columnspan=2, pady=(20,0))
        
    def add_venue(self):
        try:
            name = self.v_entries["Name"].get()
            city = self.v_entries["City"].get()
            state = self.v_entries["State"].get()
            country = self.v_entries["Country"].get()
            cap = int(self.v_entries["Capacity"].get())
            
            success, msg = self.controller.db.add_venue(name, city, state, country, cap)
            if success:
                messagebox.showinfo("Success", "Venue created, generating seats...")
                self.on_show()
            else:
                messagebox.showerror("Error", msg)
        except Exception as e:
            messagebox.showerror("Error", "Invalid inputs")
            
    def delete_venue(self, venue_id):
        if messagebox.askyesno("Confirm", "Deleting venue may fail if there are dependent events. Proceed?"):
            if self.controller.db.delete_venue(venue_id):
                messagebox.showinfo("Success", "Venue deleted.")
                self.on_show()
            else:
                messagebox.showerror("Error", "Cannot delete venue. Events may be mapped to it.")


class AdminTicketsView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

    def on_show(self, **kwargs):
        for widget in self.winfo_children():
            widget.destroy()
            
        Navbar(self, self.controller, title="All Booked Tickets").pack(fill="x")
        
        canvas = tk.Canvas(self, bg=BG_COLOR, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style="TFrame")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y", anchor="e")
        
        content = ttk.Frame(scrollable_frame, padding=20)
        content.pack(fill="both", expand=True)
        
        all_tix = self.controller.db.get_all_booked_tickets()
        if not all_tix:
            ttk.Label(content, text="No booked tickets found.").pack(anchor="w")
        else:
            for t in all_tix:
                card = ttk.Frame(content, style="Card.TFrame", padding=15)
                card.pack(fill="x", pady=5)
                
                status_color = "#4ADE80" if t['booking_status'] == 'Booked' else ("#F83F3F" if t['booking_status'] == 'Cancelled' else "#FBBF24")
                
                info = f"{t['user_name']} ({t['email']}) -> {t['event_name']} | Seat {t['seat_number']} [{t['seat_type']}]"
                ttk.Label(card, text=info, font=("Helvetica", 11), background=CARD_COLOR).pack(anchor="w")
                ttk.Label(card, text=f"Ticket ID: {t['ticket_id']}   |   Status: {t['booking_status']}", foreground=status_color, background=CARD_COLOR, font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(5, 0))

if __name__ == "__main__":
    app = App()
    app.mainloop()
