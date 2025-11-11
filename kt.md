# Smart Scheduling Assistant - Knowledge Transfer Guide

**Developer:** Manda | **Date:** Nov 11, 2025  
**Stack:** Python Flask + JavaScript | **Platform:** Dataiku

---

## 📊 COMPLETE API REFERENCE (20 Endpoints)

| #                           | Endpoint                                     | Method | Purpose                               | Dataset Used                            | Code Location   |
| --------------------------- | -------------------------------------------- | ------ | ------------------------------------- | --------------------------------------- | --------------- |
| **AUTHENTICATION**          |
| 1                           | `/send_otp`                                  | POST   | Send OTP to user email                | `UserEmailMapping`                      | backend.py:550  |
| 2                           | `/verify_otp`                                | POST   | Verify OTP and login                  | `audit_map`                             | backend.py:614  |
| **AUDIT MANAGEMENT**        |
| 3                           | `/audits`                                    | GET    | Get audits for logged-in user         | `audit_map`                             | backend.py:648  |
| 4                           | `/audit_details/<audit_number>`              | GET    | Get audit metadata                    | `input_new`                             | backend.py:667  |
| 5                           | `/employees/<audit_number>`                  | GET    | Get auditors for audit + auto-book    | `input_new`                             | backend.py:697  |
| **BOOKING OPERATIONS**      |
| 6                           | `/bookings`                                  | GET    | Get all bookings                      | `bookings`                              | backend.py:798  |
| 7                           | `/bookings/<audit_number>`                   | GET    | Get audit-specific bookings           | `bookings`                              | backend.py:803  |
| 8                           | `/api/manual_book`                           | POST   | Create manual booking                 | `bookings`, `availability`              | backend.py:939  |
| 9                           | `/api/delete_booking_range`                  | POST   | Delete booking date range             | `bookings`                              | backend.py:1261 |
| 10                          | `/bookings/delete`                           | POST   | Delete specific booking               | `bookings`                              | backend.py:1232 |
| 11                          | `/api/auditor_booking_status/<audit_number>` | GET    | Get booked/non-booked auditors        | `input_new`, `bookings`, `availability` | backend.py:535  |
| 12                          | `/api/bookings_for_calendar/<audit_number>`  | GET    | Get bookings for calendar view        | `bookings`                              | backend.py:1323 |
| **CALENDAR & AVAILABILITY** |
| 13                          | `/api/calendar_colors/<audit_number>`        | GET    | Get availability colors for audit     | `input_new`, `bookings`                 | backend.py:1363 |
| 14                          | `/api/calendar_colors/<audit_number>/<psid>` | GET    | Get employee-specific calendar colors | `bookings`, `availability`              | backend.py:1407 |
| 15                          | `/api/user_audit_calendar`                   | GET    | Get complete user calendar            | `bookings`, `availability`              | backend.py:1501 |
| 16                          | `/api/audit_availability/<audit_number>`     | GET    | Get audit date ranges                 | `input_new`                             | backend.py:1345 |
| 17                          | `/api/leave_data/<audit_number>`             | GET    | Get leave data for employees          | `availability`                          | backend.py:1283 |
| 18                          | `/api/auditors_for_calendar/<audit_number>`  | GET    | Get auditors list for calendar        | `input_new`                             | backend.py:1268 |
| **DOWNLOAD & EXPORT**       |
| 19                          | `/download_all_bookings`                     | GET    | Download all bookings CSV             | `bookings`                              | backend.py:808  |
| 20                          | `/download_selected_bookings`                | POST   | Download selected bookings CSV        | Request body                            | backend.py:820  |
| 21                          | `/api/download_calendar_excel`               | GET    | Download calendar as Excel            | `bookings`, `availability`              | backend.py:1633 |

---

## 🔥 CODE WALKTHROUGH - API CONNECTIONS

### **1. OTP-BASED LOGIN FLOW**

#### **Step 1: Send OTP**

**Purpose:** Generate and send 6-character OTP to user's email  
**Dataset:** `UserEmailMapping` - Maps PSID to email addresses

**📱 Frontend - script.js (Line 73-93)**

```javascript
psidForm.addEventListener("submit", function (event) {
  event.preventDefault();
  const psid = document.getElementById("psid").value;

  // API CALL: Send OTP
  fetch(dataiku.getWebAppBackendUrl("/send_otp"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ psid: psid }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        document.getElementById("otpSection").style.display = "block";
        document.getElementById("message").innerText =
          "OTP sent to your email! Scenario status: " + data.scenario_status;
      }
    });
});
```

**🐍 Backend - backend.py (Line 550-612)**

```python
@app.route('/send_otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    psid = data.get('psid')

    # STEP 1: Get email from UserEmailMapping dataset
    email = get_email_by_psid(psid)  # Reads UserEmailMapping dataset

    # STEP 2: Generate 6-character alphanumeric OTP
    otp = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    otp_store[psid] = otp  # Store in memory

    # STEP 3: Set Dataiku project variables for email scenario
    client = dataiku.api_client()
    project = client.get_project(PROJECT_KEY)
    vars = project.get_variables()
    vars["standard"]["email"] = email
    vars["standard"]["otp"] = otp
    project.set_variables(vars)

    # STEP 4: Trigger email scenario to send OTP
    scenario = project.get_scenario(SCENARIO_ID)
    run = scenario.run_and_wait()

    return jsonify({"success": True, "scenario_status": status})
```

**📦 JSON Response:**

```json
{
  "success": true,
  "email": "user@example.com",
  "scenario_status": "SUCCESS"
}
```

---

#### **Step 2: Verify OTP**

**Purpose:** Validate OTP and authenticate user  
**Dataset:** `audit_map` - Gets scheduler name for the user

**📱 Frontend - script.js (Line 97-121)**

```javascript
otpForm.addEventListener("submit", function (event) {
  event.preventDefault();
  const psid = document.getElementById("psid").value;
  const otp = document.getElementById("otp").value;

  // API CALL: Verify OTP
  fetch(dataiku.getWebAppBackendUrl("/verify_otp"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ psid: psid, otp: otp }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        // Store session data
        sessionStorage.setItem("psid", data.psid);
        sessionStorage.setItem("scheduler_name", data.scheduler_name);
        loadAudits(); // Load user's audits
      }
    });
});
```

**🐍 Backend - backend.py (Line 614-645)**

```python
@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    psid = data.get('psid')
    user_otp = data.get('otp')

    # STEP 1: Verify OTP from memory store
    if psid in otp_store and user_otp == otp_store[psid]:
        # STEP 2: Get scheduler name from audit_map dataset
        scheduler_name = None
        if not audit_map_df.empty:
            scheduler_row = audit_map_df[audit_map_df['PSID'] == int(psid)]
            if not scheduler_row.empty:
                scheduler_name = scheduler_row.iloc[0]['Scheduler']

        # STEP 3: Clear OTP after successful verification
        del otp_store[psid]

        return jsonify({
            "success": True,
            "psid": int(psid),
            "scheduler_name": scheduler_name
        })
```

**📦 JSON Response:**

```json
{
  "success": true,
  "psid": 1600922,
  "scheduler_name": "John Doe"
}
```

---

### **2. LOAD USER'S AUDITS**

**Purpose:** Fetch list of audits assigned to logged-in user  
**Dataset:** `audit_map` - Maps PSID to Audit IDs

**📱 Frontend - script.js (Line 141-159)**

```javascript
function loadAudits() {
  const psid = sessionStorage.getItem("psid");

  // API CALL: Get audits
  fetch(dataiku.getWebAppBackendUrl(`/audits?psid=${psid}`))
    .then((response) => response.json())
    .then((data) => {
      audits = (data.audit_numbers || []).map((audit_number) => ({
        audit_number: audit_number,
        audit_title: audit_number,
      }));
      populateAuditDropdown(audits); // Populate dropdown
    });
}
```

**🐍 Backend - backend.py (Line 648-665)**

```python
@app.route('/audits', methods=['GET'])
def get_audits():
    username = request.args.get('username')
    user_info = USERS.get(username)
    psid = user_info["psid"]

    # Read audit_map dataset and filter by PSID
    mapped_audits = audit_map_df[audit_map_df['PSID'] == int(psid)]
    audit_numbers = mapped_audits['Audit_ID'].astype(str).unique().tolist()

    return jsonify({"audit_numbers": audit_numbers})
```

**📦 JSON Response:**

```json
{
  "audit_numbers": ["2025-US-001", "2025-UK-002", "2025-IN-003"]
}
```

---

### **3. GET AUDIT DETAILS**

**Purpose:** Fetch audit metadata (dates, risk types, teams)  
**Dataset:** `input_new` - Contains audit details

**📱 Frontend - script.js (Line 185)**

```javascript
fetch(dataiku.getWebAppBackendUrl(`/audit_details/${auditNumber}`))
  .then((res) => res.json())
  .then(renderAuditDetails);
```

**🐍 Backend - backend.py (Line 667-695)**

```python
@app.route('/audit_details/<audit_number>', methods=['GET'])
def get_audit_details(audit_number):
    # Read input_new dataset
    df = load_input_new()
    audit_details_df = df[df['audit_issue_number'].astype(str) == str(audit_number)]

    first_row = audit_details_df.iloc[0]
    audit_details = {
        'audit_number': first_row['audit_issue_number'],
        'audit_plan_year': first_row['sch_start_date'].split('-')[0],
        'audit_principal_risk_types': first_row['skillkeyword_1st'],
        'audit_risk_radar_themes': first_row['skillkeyword_2nd'],
        'primary_gia_audit_owner_team': first_row['cssg_2nd'],
        'planned_planning_start_date': first_row['sch_start_date'],
        'planned_fieldwork_start_date': first_row['sch_start_date'],
        'planned_report_issuance_date': first_row['sch_end_date']
    }
    return jsonify(audit_details)
```

---

### **4. GET AUDITORS FOR AUDIT**

**Purpose:** Load auditors list + auto-book rank 1 auditors  
**Dataset:** `input_new` - Contains auditor details with ranks

**📱 Frontend - script.js (Line 192-198)**

```javascript
fetch(dataiku.getWebAppBackendUrl(`/employees/${auditNumber}?psid=${psid}`))
  .then((res) => res.json())
  .then((employeesList) => {
    renderAuditorsTable(employeesList);
  });
```

**🐍 Backend - backend.py (Line 697-758)**

```python
@app.route('/employees/<audit_number>', methods=['GET'])
def get_employees(audit_number):
    # STEP 1: Read input_new dataset
    df = load_input_new()
    employees_df = df[df['audit_issue_number'].astype(str) == str(audit_number)]

    # STEP 2: Clean and process data
    employees_df['psid'] = pd.to_numeric(employees_df['psid'], errors='coerce')
    employees_df = employees_df.dropna(subset=['psid'])
    employees_df['psid'] = employees_df['psid'].astype(int)

    # STEP 3: Rename columns for frontend
    employees_df_renamed = employees_df.rename(columns={
        'psid': 'PSID',
        'name': 'FullName',
        'auditor_role': 'JobTitle',
        'auditor_country': 'CountryName',
        'matching_score': 'WeightedSimilarityScore',
        'global_rank': 'Rank'
    })

    employees_list = employees_df_renamed.to_dict('records')

    # STEP 4: Auto-book rank 1 auditors (background process)
    scheduler_psid = request.args.get('psid')
    if scheduler_psid:
        auto_book_rank_1_auditors(audit_number, scheduler_psid)

    return jsonify(employees_list)
```

**📦 JSON Response:**

```json
[
  {
    "PSID": 1600922,
    "FullName": "John Doe",
    "JobTitle": "Senior Auditor",
    "CountryName": "USA",
    "Rank": 1,
    "WeightedSimilarityScore": "85%",
    "auditor_team_name": "Risk Team A",
    "auditor_city": "New York"
  }
]
```

---

### **5. MANUAL BOOKING (MOST COMPLEX)**

**Purpose:** Book auditor for selected dates with validation  
**Datasets:** `bookings` (write), `availability` (read)

**📱 Frontend - script.js (Line 473-512)**

```javascript
bookSelectedDatesBtn.addEventListener("click", async function () {
  const psid = checkbox.dataset.psid;
  const flatpickrInstance = flatpickrInstances[sanitizeId(psid)];
  const selectedDates = flatpickrInstance.selectedDates.map((d) =>
    formatLocalDateToYYYYMMDD(d)
  );
  // selectedDates = ['2025-11-15', '2025-11-16', '2025-11-17']

  const bookingData = {
    audit_number: auditNumber,
    psid: psid,
    full_name: auditor.FullName,
    role: auditor.auditor_role,
    dates_to_book_list: selectedDates,
    scheduler_psid: schedulerPsid,
  };

  // API CALL: Manual Book
  const response = await fetch(
    dataiku.getWebAppBackendUrl("/api/manual_book"),
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(bookingData),
    }
  );
});
```

**🐍 Backend - backend.py (Line 939-1023)**

```python
@app.route('/api/manual_book', methods=['POST'])
def add_manual_booking():
    data = request.get_json()
    psid = int(data['psid'])
    dates_to_book_list = data['dates_to_book_list']

    # STEP 1: Convert individual dates to continuous blocks
    # ['2025-11-15', '2025-11-16', '2025-11-17']
    # → [{'BookedFrom': '2025-11-15', 'BookedTo': '2025-11-17'}]
    date_blocks = convert_dates_to_blocks(dates_to_book_list)

    # STEP 2: Read datasets
    bookings_df = load_bookings()          # Read bookings dataset
    availability_df = load_availability()  # Read availability dataset
    new_bookings_to_add = []

    for block in date_blocks:
        start_date = pd.to_datetime(block['BookedFrom']).date()
        end_date = pd.to_datetime(block['BookedTo']).date()

        # STEP 3: Check for date clashes with existing bookings
        is_ok, clash_audit = check_date_clash(psid, start_date, end_date)
        if not is_ok:
            return jsonify({
                "success": False,
                "message": f"Date clash with audit {clash_audit}"
            }), 400

        # STEP 4: Calculate booking metrics (splits by week if needed)
        booking_rows = calculate_booking_metrics(
            psid, start_date, end_date, availability_df
        )

        # STEP 5: Prepare booking records
        for booking_row in booking_rows:
            booking_row.update({
                'audit_number': audit_number,
                'PSID': psid,
                'FullName': data['full_name'],
                'Role': data['role'],
                'Phase': "Planning",
                'Timestamp': datetime.now().isoformat(),
                'bookedby': scheduler_psid
            })
            new_bookings_to_add.append(booking_row)

    # STEP 6: Write to bookings dataset
    if new_bookings_to_add:
        updated_bookings = pd.concat(
            [bookings_df, pd.DataFrame(new_bookings_to_add)],
            ignore_index=True
        )
        write_bookings_df(updated_bookings)  # ← Writes to Dataiku dataset

        return jsonify({"success": True, "message": "Bookings added successfully."})
```

**📤 Request Payload:**

```json
{
  "audit_number": "2025-US-001",
  "psid": 1600922,
  "full_name": "John Doe",
  "role": "Senior Auditor",
  "dates_to_book_list": ["2025-11-15", "2025-11-16", "2025-11-17"],
  "scheduler_psid": 2024059
}
```

---

### **6. GET CALENDAR COLORS**

**Purpose:** Color-code calendar dates based on availability/bookings  
**Datasets:** `bookings` (read), `availability` (read)

**📱 Frontend - script.js (Line 338-348)**

```javascript
fetch(
  dataiku.getWebAppBackendUrl(`/api/calendar_colors/${auditNumber}/${psid}`)
)
  .then((res) => res.json())
  .then((data) => {
    const auditorCalendarColors = data.calendar_colors || {};
    // {'2025-11-15': 'green', '2025-11-16': 'red', ...}
    initializeFlatpickr(sanitizedPsid, auditor, auditorCalendarColors);
  });
```

**🐍 Backend - backend.py (Line 1407-1499)**

```python
@app.route('/api/calendar_colors/<audit_number>/<int:psid>', methods=['GET'])
def get_calendar_colors_for_employee(audit_number, psid):
    # STEP 1: Get audit window from input_new dataset
    df_input = load_input_new()
    audit_window_df = df_input[
        df_input['audit_issue_number'].astype(str) == str(audit_number)
    ]
    audit_start_date = pd.to_datetime(audit_window_df.iloc[0]['sch_start_date']).date()
    audit_end_date = pd.to_datetime(audit_window_df.iloc[0]['sch_end_date']).date()

    # STEP 2: Get booked dates from bookings dataset
    bookings = load_bookings()
    emp_bookings = bookings[bookings['PSID'].astype(int) == int(psid)]
    booked_dates = set()
    for _, row in emp_bookings.iterrows():
        booked_start = pd.to_datetime(row['BookedFrom']).date()
        booked_end = pd.to_datetime(row['BookedTo']).date()
        current_date = booked_start
        while current_date <= booked_end:
            booked_dates.add(current_date.strftime('%Y-%m-%d'))
            current_date += pd.Timedelta(days=1)

    # STEP 3: Get availability from availability dataset
    availability_df = load_availability()
    emp_availability = availability_df[availability_df['psid'].astype(int) == int(psid)]
    availability_map = emp_availability.set_index('date')['daily_available_hours'].to_dict()

    # STEP 4: Build color map
    calendar_colors = {}
    current_date = audit_start_date - pd.Timedelta(days=30)
    max_date = audit_end_date + pd.Timedelta(days=30)

    while current_date <= max_date:
        date_str = current_date.strftime('%Y-%m-%d')

        if date_str in booked_dates:
            calendar_colors[date_str] = 'red'  # Booked
        elif current_date.weekday() >= 5:
            calendar_colors[date_str] = 'light-blue'  # Weekend
        else:
            available_hours = availability_map.get(date_str, 0)
            if available_hours == 8:
                calendar_colors[date_str] = 'green'  # Fully available
            elif 0 < available_hours < 8:
                calendar_colors[date_str] = 'yellow'  # Partially available
            elif available_hours == 0:
                calendar_colors[date_str] = 'orange'  # Leave

        current_date += pd.Timedelta(days=1)

    return jsonify({"calendar_colors": calendar_colors})
```

**📦 JSON Response:**

```json
{
  "calendar_colors": {
    "2025-11-15": "green",
    "2025-11-16": "red",
    "2025-11-17": "green",
    "2025-11-18": "yellow",
    "2025-11-19": "orange",
    "2025-11-20": "light-blue"
  }
}
```

---

## 📂 KEY DATASETS

| Dataset Name       | Purpose                   | Columns Used                                                                                            | Read/Write |
| ------------------ | ------------------------- | ------------------------------------------------------------------------------------------------------- | ---------- |
| `UserEmailMapping` | Map PSID to email for OTP | psid, email                                                                                             | Read       |
| `audit_map`        | Map users to audits       | PSID, Audit_ID, Scheduler                                                                               | Read       |
| `input_new`        | Audit details & auditors  | audit_issue_number, psid, name, auditor_role, matching_score, global_rank, sch_start_date, sch_end_date | Read       |
| `availability`     | Daily availability hours  | psid, date, daily_available_hours, week_start, week_end                                                 | Read       |
| `bookings`         | Booking records           | audit_number, PSID, FullName, Role, BookedFrom, BookedTo, bookedby                                      | Read/Write |

---

## 🔄 COMPLETE USER FLOW

```
1. 📱 User enters PSID → script.js:73
   ↓
2. 📱 fetch('/send_otp') → backend.py:550
   ↓
3. 🐍 Read UserEmailMapping dataset → backend.py:91
   ↓
4. 🐍 Generate OTP, trigger email scenario → backend.py:573-602
   ↓
5. 📱 User enters OTP → script.js:97
   ↓
6. 📱 fetch('/verify_otp') → backend.py:614
   ↓
7. 🐍 Verify OTP, read audit_map → backend.py:622-627
   ↓
8. 📱 loadAudits() → script.js:141
   ↓
9. 📱 fetch('/audits') → backend.py:648
   ↓
10. 🐍 Read audit_map, filter by PSID → backend.py:658
   ↓
11. 📱 Populate dropdown, user selects audit → script.js:185
   ↓
12. 📱 fetch('/employees/'+audit) → backend.py:697
   ↓
13. 🐍 Read input_new dataset → backend.py:699
   ↓
14. 🐍 Auto-book rank 1 auditors → backend.py:744
   ↓
15. 📱 Render auditors table → script.js:292
   ↓
16. 📱 fetch('/api/calendar_colors/'+audit+'/'+psid) → backend.py:1407
   ↓
17. 🐍 Read bookings + availability → backend.py:1423-1445
   ↓
18. 📱 Initialize Flatpickr with colors → script.js:359
   ↓
19. 📱 User selects dates, clicks "Book" → script.js:473
   ↓
20. 📱 fetch('/api/manual_book') → backend.py:939
   ↓
21. 🐍 convert_dates_to_blocks() → backend.py:1032
   ↓
22. 🐍 check_date_clash() → backend.py:263
   ↓
23. 🐍 calculate_booking_metrics() → backend.py:297
   ↓
24. 🐍 write_bookings_df() → backend.py:64 (Dataiku write)
   ↓
25. 📱 Refresh UI → script.js:511
```

---

## 🛠️ KEY PYTHON FUNCTIONS

### **Dataiku Dataset Operations**

```python
# backend.py:41-64
def get_input_new_df():
    return dataiku.Dataset("input_new").get_dataframe()

def get_availability_df():
    return dataiku.Dataset("availability").get_dataframe()

def get_bookings_df():
    return dataiku.Dataset("bookings").get_dataframe()

def write_bookings_df(df):
    bookings_dataset = dataiku.Dataset("bookings")
    bookings_dataset.write_with_schema(df)  # ← Writes to CSV
```

### **Date Conflict Detection**

```python
# backend.py:263-276
def check_date_clash(psid, start_date, end_date):
    """Check if booking overlaps with existing bookings"""
    bookings = load_bookings()
    emp_bookings = bookings[bookings['PSID'] == psid]

    for _, row in emp_bookings.iterrows():
        booked_start = pd.to_datetime(row['BookedFrom'])
        booked_end = pd.to_datetime(row['BookedTo'])

        # Check overlap: NOT (end before start OR start after end)
        if not (end_date < booked_start or start_date > booked_end):
            return False, row['audit_number']  # ← Clash detected

    return True, None  # ← No clash
```

### **Convert Dates to Continuous Blocks**

```python
# backend.py:1032-1069
def convert_dates_to_blocks(dates_list):
    """
    Converts: ['2025-11-15', '2025-11-16', '2025-11-18']
    Into: [
        {'BookedFrom': '2025-11-15', 'BookedTo': '2025-11-16'},
        {'BookedFrom': '2025-11-18', 'BookedTo': '2025-11-18'}
    ]
    """
    parsed_dates = sorted(set([pd.to_datetime(str(d)).date() for d in dates_list]))
    date_blocks = []
    current_block_start = parsed_dates[0]
    current_block_end = parsed_dates[0]

    for i in range(1, len(parsed_dates)):
        if parsed_dates[i] == current_block_end + timedelta(days=1):
            current_block_end = parsed_dates[i]  # Extend block
        else:
            date_blocks.append({
                'BookedFrom': current_block_start.strftime('%Y-%m-%d'),
                'BookedTo': current_block_end.strftime('%Y-%m-%d')
            })
            current_block_start = parsed_dates[i]
            current_block_end = parsed_dates[i]

    date_blocks.append({
        'BookedFrom': current_block_start.strftime('%Y-%m-%d'),
        'BookedTo': current_block_end.strftime('%Y-%m-%d')
    })
    return date_blocks
```

---

## 🎨 CSS COLOR CODING

**File:** style.css

```css
.date-green {
  background-color: #28a745 !important;
} /* 8 hours available */
.date-red {
  background-color: #dc3545 !important;
} /* Already booked */
.date-yellow {
  background-color: #ffc107 !important;
} /* 1-7 hours available */
.date-orange {
  background-color: #fd7e14 !important;
} /* 0 hours = Leave */
.date-light-blue {
  background-color: #add8e6 !important;
} /* Weekend */
.date-grey {
  background-color: #808080 !important;
} /* Outside audit window */
```

---

## 🚀 SUMMARY FOR MANAGER

**Technology Stack:**

- Backend: Python Flask (20 API endpoints)
- Frontend: JavaScript (Fetch API)
- Database: Dataiku Datasets (5 CSV-based datasets)
- UI: HTML + Bootstrap + Flatpickr calendar

**Authentication:**

- OTP-based login via email
- 6-character alphanumeric OTP
- Dataiku scenario triggers email

**Core Functionality:**

1. **Login:** OTP sent to email → User verifies → Session created
2. **Load Audits:** Fetch audits from `audit_map` dataset
3. **View Auditors:** Read `input_new` dataset → Auto-book rank 1
4. **Manual Booking:** Select dates → Check conflicts → Write to `bookings`
5. **Calendar View:** Color-code dates based on `availability` + `bookings`

**Data Flow:**

- JavaScript → Fetch API → Flask Route → Dataiku Dataset → Response JSON → UI Update

---

**END OF KNOWLEDGE TRANSFER**
