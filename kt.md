# Smart Scheduling Assistant - Knowledge Transfer Document

**Project:** ss_no_autobook  
**Developer:** Manda  
**Date:** November 11, 2025  
**Purpose:** Knowledge Transfer to Manager

---

## 📋 Executive Summary

The **Smart Scheduling Assistant** is a Flask-based web application that helps schedulers manage audit bookings efficiently. It integrates Python backend (Flask) with JavaScript frontend to provide a seamless booking experience with real-time availability tracking.

---

## 🏗️ Architecture Overview

### **Tech Stack**

- **Backend:** Python Flask (REST API)
- **Frontend:** HTML5, JavaScript (ES6), CSS3
- **UI Framework:** Bootstrap 4.5.2
- **Date Picker:** Flatpickr.js
- **Data Source:** Dataiku Datasets (CSV-based)
- **Authentication:** OTP-based login with SHA-256 hashing

### **Three-Tier Architecture**

```
┌─────────────────────┐
│   Frontend (HTML)   │ ← User Interface Layer
│   - index.html      │
│   - script.js       │
│   - style.css       │
└──────────┬──────────┘
           │ (AJAX/Fetch API Calls)
           ▼
┌─────────────────────┐
│  Backend (Python)   │ ← Application Logic Layer
│   - backend.py      │
│   - Flask Routes    │
└──────────┬──────────┘
           │ (Dataiku SDK)
           ▼
┌─────────────────────┐
│  Data Layer         │ ← Data Storage Layer
│  - Dataiku Datasets │
│  - CSV Files        │
└─────────────────────┘
```

---

## 🔌 API Architecture

### **Total Number of API Endpoints: 20**

#### **1. Authentication APIs (2)**

| Endpoint                                      | Method | Purpose             | Request Payload        | Response                          |
| --------------------------------------------- | ------ | ------------------- | ---------------------- | --------------------------------- |
| `/login`                                      | POST   | User authentication | `{username, password}` | `{success, psid, scheduler_name}` |
| _Note: OTP endpoints removed in this version_ |        |                     |                        |                                   |

#### **2. Audit Management APIs (3)**

| Endpoint                        | Method | Purpose                | Request Payload           | Response                               |
| ------------------------------- | ------ | ---------------------- | ------------------------- | -------------------------------------- |
| `/audits`                       | GET    | Fetch user's audits    | Query: `username`         | `{audit_numbers: []}`                  |
| `/audit_details/<audit_number>` | GET    | Get audit metadata     | URL param                 | `{audit_number, audit_plan_year, ...}` |
| `/employees/<audit_number>`     | GET    | Get auditors for audit | URL param + Query: `psid` | `[{PSID, FullName, ...}]`              |

#### **3. Booking Management APIs (7)**

| Endpoint                                     | Method | Purpose                        | Request Payload                                 | Response                                 |
| -------------------------------------------- | ------ | ------------------------------ | ----------------------------------------------- | ---------------------------------------- |
| `/bookings`                                  | GET    | Get all bookings               | -                                               | `[{audit_number, PSID, ...}]`            |
| `/bookings/<audit_number>`                   | GET    | Get audit-specific bookings    | URL param                                       | `[{booking details}]`                    |
| `/api/manual_book`                           | POST   | Create manual booking          | `{audit_number, psid, dates_to_book_list, ...}` | `{success, message}`                     |
| `/api/delete_booking_range`                  | POST   | Delete booking range           | `{psid, start_date, end_date, ...}`             | `{success, message}`                     |
| `/bookings/delete`                           | POST   | Delete specific booking        | `{audit_number, psid, scheduler_psid}`          | `{success, message}`                     |
| `/api/auditor_booking_status/<audit_number>` | GET    | Get booked/non-booked auditors | URL param                                       | `{non_booked_auditors, booked_auditors}` |
| `/api/bookings_for_calendar/<audit_number>`  | GET    | Get calendar bookings          | URL param + Query: `psid`                       | `{bookings: []}`                         |

#### **4. Calendar & Availability APIs (5)**

| Endpoint                                     | Method | Purpose                       | Request Payload | Response                             |
| -------------------------------------------- | ------ | ----------------------------- | --------------- | ------------------------------------ |
| `/api/calendar_colors/<audit_number>`        | GET    | Get audit availability colors | URL param       | `{calendar_colors: {date: color}}`   |
| `/api/calendar_colors/<audit_number>/<psid>` | GET    | Get employee-specific colors  | URL params      | `{calendar_colors: {date: color}}`   |
| `/api/user_audit_calendar`                   | GET    | Get user's complete calendar  | Query: `psid`   | `{employees: [{calendar: {}}]}`      |
| `/api/audit_availability/<audit_number>`     | GET    | Get audit date ranges         | URL param       | `{availability_dates: [{from, to}]}` |
| `/api/leave_data/<audit_number>`             | GET    | Get leave information         | URL param       | `{leave_data: {}}`                   |

#### **5. Download & Export APIs (3)**

| Endpoint                       | Method | Purpose                    | Request Payload  | Response   |
| ------------------------------ | ------ | -------------------------- | ---------------- | ---------- |
| `/download_all_bookings`       | GET    | Download all bookings CSV  | -                | CSV file   |
| `/download_selected_bookings`  | POST   | Download selected bookings | `{bookings: []}` | CSV file   |
| `/api/download_calendar_excel` | GET    | Download calendar Excel    | Query: `psid`    | Excel file |

---

## 🔄 Frontend-Backend Connection Flow

### **How JavaScript Connects to Python**

```javascript
// JavaScript (script.js) makes API calls using Fetch API
fetch(dataiku.getWebAppBackendUrl("/api/manual_book"), {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(bookingData),
})
  .then((response) => response.json())
  .then((data) => {
    /* Handle response */
  });
```

```python
# Python (backend.py) handles the request
@app.route('/api/manual_book', methods=['POST'])
def add_manual_booking():
    data = request.get_json()  # Receives JSON from frontend
    # Process booking logic
    return jsonify({"success": True, "message": "..."})  # Sends JSON back
```

### **Key Integration Points**

1. **Dataiku Backend URL:** `dataiku.getWebAppBackendUrl()` bridges frontend to backend
2. **JSON Communication:** All data exchanged via JSON format
3. **Session Management:** Uses `sessionStorage` to maintain user state (PSID, scheduler name)
4. **Real-time Updates:** Frontend refreshes data after each booking action

---

## 📊 Data Flow Diagram

```
User Action (Frontend)
        ↓
JavaScript Event Handler
        ↓
Fetch API Call (AJAX)
        ↓
Flask Route (@app.route)
        ↓
Business Logic (Python functions)
        ↓
Dataiku Dataset Read/Write
        ↓
Database (CSV Files)
        ↓
Response to Frontend (JSON)
        ↓
DOM Update (UI Refresh)
```

---

## 🎯 Key Features Implemented

### **1. Smart Booking System**

- Manual date selection via Flatpickr calendar
- Color-coded availability (Green=Available, Red=Booked, Yellow=Partial, Orange=Leave)
- Automatic conflict detection
- Split booking ranges by week

### **2. Auditor Management**

- Consolidated view (Booked vs Non-Booked sections)
- Rank-based auto-selection (Rank 1 auditors)
- Matching score calculation
- Real-time utilization tracking

### **3. Calendar Visualization**

- Employee-wise audit calendar
- Multi-color coding for different audit prefixes
- Excel export functionality
- Date range filtering

---

## 🔐 Security & Authentication

- **Password Hashing:** SHA-256 for password security
- **Session Management:** Server-side session with PSID tracking
- **User Authorization:** Users can only manage their own bookings
- **Data Validation:** Input sanitization and error handling

---

## 📁 File Structure

```
ss_no_autobook/
├── backend.py          # Flask application with all API routes
├── index.html          # Main UI structure
├── script.js           # Frontend logic and API integration
├── style.css           # Custom styling
├── ss_text.txt         # Configuration/documentation
├── CHANGES_SUMMARY.md  # Change history
└── DEBUG_GUIDE.md      # Troubleshooting guide
```

---

## 🛠️ Technical Highlights

### **Backend Capabilities**

- RESTful API design
- Pandas for data manipulation
- Openpyxl for Excel generation
- Date conflict resolution algorithms
- Automated booking split by week

### **Frontend Capabilities**

- Responsive Bootstrap UI
- Dynamic table rendering
- Modal-based delete operations
- Multi-select flatpickr calendars
- Real-time data refresh

### **Data Processing**

- Availability calculation from daily hours
- Booking metrics (allocated hours, days)
- Calendar color mapping algorithm
- Date block conversion logic

---

## 🚀 Common User Workflows

### **Workflow 1: Book an Auditor**

1. User selects audit from dropdown → `/audits` API
2. System loads auditors → `/employees/<audit_number>` API
3. User selects dates via flatpickr calendar
4. User clicks "Book Selected Dates" → `/api/manual_book` API
5. Backend validates availability → `check_date_clash()`
6. Booking saved to dataset → `write_bookings_df()`
7. UI refreshes with updated status

### **Workflow 2: View Audit Calendar**

1. User clicks "View Audit Calendar"
2. Frontend calls `/api/user_audit_calendar?psid=<psid>`
3. Backend aggregates all employee bookings
4. Returns day-wise color-coded calendar
5. Frontend renders interactive table
6. User can export to Excel

---

## 💡 Key Algorithms Explained

### **1. Date Conflict Detection**

```python
def check_date_clash(psid, start_date, end_date):
    # Checks if new booking overlaps with existing bookings
    # Returns: (is_ok: bool, clash_audit: str)
```

### **2. Booking Metrics Calculation**

```python
def calculate_booking_metrics(psid, start_date, end_date, availability_df):
    # Splits bookings by week
    # Calculates allocated hours and days
    # Returns: [{BookedFrom, BookedTo, allocated_hours, ...}]
```

### **3. Date Block Conversion**

```python
def convert_dates_to_blocks(dates_list):
    # Converts ['2025-11-24', '2025-11-25', '2025-11-27']
    # Into: [{BookedFrom: '2025-11-24', BookedTo: '2025-11-25'}, ...]
```

---

## 📈 Performance Considerations

- Minimal API calls using batch operations
- Client-side caching of audit data
- Efficient pandas operations on datasets
- Lazy loading of calendar data

---

## 🔍 Debugging & Monitoring

- Console logs for API responses
- Error alerts for user feedback
- Backend logging with Python `logging` module
- Debug mode comments in code

---

## 🎓 Knowledge Transfer Checklist

- ✅ Understand the 3-tier architecture
- ✅ Know all 20 API endpoints and their purposes
- ✅ Grasp the frontend-backend connection via Fetch API
- ✅ Comprehend data flow from UI to database
- ✅ Review key algorithms (conflict detection, booking metrics)
- ✅ Test common workflows (booking, calendar view, deletion)

---

## 📞 Quick Reference

**Main Components:**

- **backend.py:** All server-side logic (Flask routes)
- **script.js:** All client-side logic (API calls, UI updates)
- **index.html:** UI structure (Bootstrap layout)

**Critical Functions:**

- `add_manual_booking()` - Creates new bookings
- `check_date_clash()` - Prevents double bookings
- `get_auditor_booking_status()` - Splits booked/non-booked
- `renderAuditCalendar()` - Displays user's calendar

---

## 📝 Notes for Manager

This application demonstrates:

1. **Full-stack development** with Python (backend) and JavaScript (frontend)
2. **RESTful API design** with 20 well-structured endpoints
3. **Real-time data processing** using Dataiku datasets
4. **User-centric design** with intuitive booking workflows
5. **Scalable architecture** ready for future enhancements

The codebase is modular, well-documented, and follows industry best practices for web application development.

---

**End of Document**
