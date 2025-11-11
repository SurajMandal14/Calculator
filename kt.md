# Smart Scheduling Assistant - CODE KNOWLEDGE TRANSFER

**Developer:** Mandal | **Date:** Nov 11, 2025 | **Stack:** Flask + JavaScript

---

## 📊 API INVENTORY: 20 ENDPOINTS

### Authentication (1 API)

- `/login` - POST

### Audit APIs (3 APIs)

- `/audits` - GET
- `/audit_details/<audit_number>` - GET
- `/employees/<audit_number>` - GET

### Booking APIs (7 APIs)

- `/bookings` - GET
- `/bookings/<audit_number>` - GET
- `/api/manual_book` - POST
- `/api/delete_booking_range` - POST
- `/bookings/delete` - POST
- `/api/auditor_booking_status/<audit_number>` - GET
- `/api/bookings_for_calendar/<audit_number>` - GET

### Calendar APIs (5 APIs)

- `/api/calendar_colors/<audit_number>` - GET
- `/api/calendar_colors/<audit_number>/<psid>` - GET
- `/api/user_audit_calendar` - GET
- `/api/audit_availability/<audit_number>` - GET
- `/api/leave_data/<audit_number>` - GET

### Download APIs (3 APIs)

- `/download_all_bookings` - GET
- `/download_selected_bookings` - POST
- `/api/download_calendar_excel` - GET

---

## 🔥 LIVE CODE EXAMPLES - JS ↔ PYTHON CONNECTION

### **EXAMPLE 1: USER LOGIN**

#### 📱 Frontend (script.js - Line 20-40)

```javascript
psidForm.addEventListener("submit", function (event) {
  event.preventDefault();
  const psid = document.getElementById("psid").value;
  const password = document.getElementById("password").value;
  const passwordHash = sha256(password); // SHA-256 hash

  // ✅ API CALL TO BACKEND
  fetch(dataiku.getWebAppBackendUrl("/login"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      username: psid,
      password: passwordHash,
    }),
  })
    .then((response) => response.json()) // ← Gets JSON response
    .then((data) => {
      if (data.success) {
        sessionStorage.setItem("psid", data.psid);
        sessionStorage.setItem("scheduler_name", data.scheduler_name);
        loginContainer.style.display = "none";
        appContainer.style.display = "block";
        loadAudits(); // ← Calls next API
      }
    });
});
```

#### 🐍 Backend (backend.py - Line 320)

```python
@app.route('/login', methods=['POST'])
def login():
    """User login with SHA-256 password hashing"""
    data = request.get_json()  # ← Receives JSON from JS
    username = data.get('username')
    password_hash = data.get('password')

    # Check credentials from USERS dictionary
    user_info = USERS.get(username)
    if user_info and user_info["password_hash"] == password_hash:
        user_psid = user_info["psid"]

        # Fetch scheduler name from Dataiku dataset
        scheduler_name = None
        if not audit_map_df.empty:
            scheduler_row = audit_map_df[audit_map_df['PSID'] == user_psid]
            if not scheduler_row.empty:
                scheduler_name = scheduler_row.iloc[0]['Scheduler']

        # ✅ SEND JSON RESPONSE BACK TO JS
        return jsonify({
            "success": True,
            "username": username,
            "psid": user_psid,
            "scheduler_name": scheduler_name
        })
    else:
        return jsonify({"success": False, "message": "Invalid credentials"})
```

**📦 JSON Response:**

```json
{
  "success": true,
  "username": "1600922",
  "psid": 1600922,
  "scheduler_name": "John Doe"
}
```

---

### **EXAMPLE 2: LOAD AUDITS DROPDOWN**

#### 📱 Frontend (script.js - Line 100)

```javascript
function loadAudits() {
  const psid = sessionStorage.getItem("psid");

  // ✅ API CALL
  fetch(dataiku.getWebAppBackendUrl(`/audits?psid=${psid}`))
    .then((response) => response.json())
    .then((data) => {
      // data.audit_numbers = ["2025-US-001", "2025-UK-002", ...]
      audits = (data.audit_numbers || []).map((audit_number) => ({
        audit_number: audit_number,
        audit_title: audit_number,
      }));

      populateAuditDropdown(audits); // Populate <select> dropdown

      if (audits.length > 0) {
        loadAuditData(audits[0].audit_number); // Load first audit
      }
    });
}
```

#### 🐍 Backend (backend.py - Line 340)

```python
@app.route('/audits', methods=['GET'])
def get_audits():
    try:
        username = request.args.get('username')  # ← Get query parameter
        if not username:
            return jsonify({"error": "Username is required"}), 400

        user_info = USERS.get(username)
        psid = user_info["psid"]

        # Filter audit_map CSV for this PSID's audits
        mapped_audits = audit_map_df[audit_map_df['PSID'] == int(psid)]
        audit_numbers = mapped_audits['Audit_ID'].astype(str).unique().tolist()

        # ✅ SEND JSON RESPONSE
        return jsonify({"audit_numbers": audit_numbers})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

**📦 JSON Response:**

```json
{
  "audit_numbers": ["2025-US-001", "2025-UK-002", "2025-IN-003"]
}
```

---

### **EXAMPLE 3: GET AUDITORS FOR AUDIT**

#### 📱 Frontend (script.js - Line 180)

```javascript
function loadAuditData(auditNumber) {
  const psid = sessionStorage.getItem("psid");

  // ✅ API CALL - Get employees/auditors
  fetch(dataiku.getWebAppBackendUrl(`/employees/${auditNumber}?psid=${psid}`))
    .then((res) => res.json())
    .then((employeesList) => {
      // employeesList = [{PSID: 1600922, FullName: "John Doe", ...}, ...]
      renderAuditorsTable(employeesList);
    });
}
```

#### 🐍 Backend (backend.py - Line 380)

```python
@app.route('/employees/<audit_number>', methods=['GET'])
def get_employees(audit_number):
    try:
        # Read from Dataiku dataset
        df = load_input_new()

        # Filter by audit number
        employees_df = df[df['audit_issue_number'].astype(str) == str(audit_number)]

        # Clean PSID column
        employees_df['psid'] = pd.to_numeric(employees_df['psid'], errors='coerce')
        employees_df = employees_df.dropna(subset=['psid'])
        employees_df['psid'] = employees_df['psid'].astype(int)

        # Rename columns for frontend
        employees_df_renamed = employees_df.rename(columns={
            'psid': 'PSID',
            'name': 'FullName',
            'auditor_role': 'JobTitle',
            'auditor_country': 'CountryName',
            'matching_score': 'WeightedSimilarityScore',
            'global_rank': 'Rank'
        })

        employees_list = employees_df_renamed.to_dict('records')

        # Background: Auto-book rank 1 auditors
        scheduler_psid = request.args.get('psid')
        if scheduler_psid:
            auto_book_rank_1_auditors(audit_number, scheduler_psid)

        # ✅ SEND JSON RESPONSE
        return jsonify(employees_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
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
    "WeightedSimilarityScore": "85%"
  },
  {
    "PSID": 2024059,
    "FullName": "Jane Smith",
    "JobTitle": "Audit Manager",
    "CountryName": "UK",
    "Rank": 2,
    "WeightedSimilarityScore": "72%"
  }
]
```

---

### **EXAMPLE 4: BOOK AUDITOR (MOST IMPORTANT)**

#### 📱 Frontend (script.js - Line 450)

```javascript
bookSelectedDatesBtn.addEventListener("click", async function () {
  const selectedCheckboxes = Array.from(
    auditorsTableBody.querySelectorAll('input[type="checkbox"]:checked')
  );

  const auditNumber = auditSelect.value;
  const schedulerPsid = sessionStorage.getItem("psid");

  for (const checkbox of selectedCheckboxes) {
    const psid = checkbox.dataset.psid;
    const auditor = nonBookedAuditors.find((a) => a.PSID == psid);

    // Get selected dates from flatpickr calendar
    const flatpickrInstance = flatpickrInstances[sanitizeId(psid)];
    const selectedDates = flatpickrInstance.selectedDates.map((d) =>
      formatLocalDateToYYYYMMDD(d)
    );
    // selectedDates = ['2025-11-15', '2025-11-16', '2025-11-17']

    const bookingData = {
      audit_number: auditNumber,
      audit_title: "Audit Title",
      psid: psid,
      full_name: auditor.FullName,
      role: auditor.auditor_role,
      dates_to_book_list: selectedDates,
      scheduler_psid: schedulerPsid,
    };

    // ✅ API CALL - Manual booking
    const response = await fetch(
      dataiku.getWebAppBackendUrl("/api/manual_book"),
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(bookingData),
      }
    );

    const result = await response.json();
    if (result.success) {
      console.log("Booking successful!");
    } else {
      alert(`Failed: ${result.message}`);
    }
  }

  loadAuditData(auditNumber); // Refresh UI
});
```

#### 🐍 Backend (backend.py - Line 600)

```python
@app.route('/api/manual_book', methods=['POST'])
def add_manual_booking():
    """Handles manual booking requests from the UI"""
    try:
        data = request.get_json()  # ← Receives JSON from JS
        audit_number = data['audit_number']
        psid = int(data['psid'])
        dates_to_book_list = data['dates_to_book_list']  # List of dates
        scheduler_psid = data['scheduler_psid']

        if not dates_to_book_list:
            return jsonify({"success": False, "message": "No dates provided"}), 400

        # STEP 1: Convert individual dates to continuous blocks
        date_blocks = convert_dates_to_blocks(dates_to_book_list)
        # Result: [{'BookedFrom': '2025-11-15', 'BookedTo': '2025-11-17'}, ...]

        bookings_df = load_bookings()  # Read existing bookings from Dataiku
        availability_df = load_availability()  # Read availability data
        new_bookings_to_add = []

        for block in date_blocks:
            start_date = pd.to_datetime(block['BookedFrom']).date()
            end_date = pd.to_datetime(block['BookedTo']).date()

            # STEP 2: Check for date clashes
            is_ok, clash_audit = check_date_clash(psid, start_date, end_date)
            if not is_ok:
                return jsonify({
                    "success": False,
                    "message": f"Date clash with audit {clash_audit}"
                }), 400

            # STEP 3: Calculate booking metrics (splits by week if needed)
            booking_rows = calculate_booking_metrics(
                psid, start_date, end_date, availability_df
            )

            # STEP 4: Prepare booking records
            for booking_row in booking_rows:
                booking_row.update({
                    'audit_number': audit_number,
                    'audit_title': data.get('audit_title', 'N/A'),
                    'PSID': psid,
                    'FullName': data['full_name'],
                    'Role': data['role'],
                    'Phase': "Planning",
                    'Timestamp': datetime.now().isoformat(),
                    'bookedby': scheduler_psid
                })
                new_bookings_to_add.append(booking_row)

        # STEP 5: Write to Dataiku dataset
        if new_bookings_to_add:
            updated_bookings = pd.concat(
                [bookings_df, pd.DataFrame(new_bookings_to_add)],
                ignore_index=True
            )
            write_bookings_df(updated_bookings)  # ← Writes to CSV via Dataiku

            # ✅ SEND SUCCESS RESPONSE
            return jsonify({
                "success": True,
                "message": "Bookings added successfully."
            })
        else:
            return jsonify({"success": False, "message": "No bookings added"}), 400

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
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

**📦 Response:**

```json
{
  "success": true,
  "message": "Bookings added successfully."
}
```

---

### **EXAMPLE 5: GET CALENDAR COLORS**

#### 📱 Frontend (script.js - Line 700)

```javascript
// Fetch calendar colors for each employee
fetch(
  dataiku.getWebAppBackendUrl(`/api/calendar_colors/${auditNumber}/${psid}`)
)
  .then((res) => res.json())
  .then((data) => {
    const auditorCalendarColors = data.calendar_colors || {};
    // auditorCalendarColors = {'2025-11-15': 'green', '2025-11-16': 'red', ...}

    initializeFlatpickr(sanitizedPsid, auditor, auditorCalendarColors);
  });

// Initialize Flatpickr with color coding
function initializeFlatpickr(psid, auditor, colors) {
  flatpickrInstances[psid] = flatpickr(element, {
    mode: "multiple",
    dateFormat: "Y-m-d",
    onDayCreate: function (dObj, dStr, fp, dayElem) {
      const date = formatLocalDateToYYYYMMDD(dayElem.dateObj);
      const colorClass = colors[date]; // ← Get color for this date

      if (colorClass) {
        dayElem.classList.add(`date-${colorClass}`); // Add CSS class
      }
    },
  });
}
```

#### 🐍 Backend (backend.py - Line 950)

```python
@app.route('/api/calendar_colors/<audit_number>/<int:psid>', methods=['GET'])
def get_calendar_colors_for_employee(audit_number, psid):
    try:
        # Get audit window dates
        df_input = load_input_new()
        audit_window_df = df_input[
            df_input['audit_issue_number'].astype(str) == str(audit_number)
        ]
        audit_start_date = pd.to_datetime(
            audit_window_df.iloc[0]['sch_start_date']
        ).date()
        audit_end_date = pd.to_datetime(
            audit_window_df.iloc[0]['sch_end_date']
        ).date()

        # Get all booked dates for this employee across ALL audits
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

        # Get availability data for this employee
        availability_df = load_availability()
        emp_availability = availability_df[
            availability_df['psid'].astype(int) == int(psid)
        ]
        availability_map = emp_availability.set_index(
            'date'
        )['daily_available_hours'].to_dict()

        # Build color map
        calendar_colors = {}
        current_date = audit_start_date - pd.Timedelta(days=30)
        max_date = audit_end_date + pd.Timedelta(days=30)

        while current_date <= max_date:
            date_str = current_date.strftime('%Y-%m-%d')

            if date_str in booked_dates:
                calendar_colors[date_str] = 'red'  # Booked
            elif current_date.weekday() >= 5:  # Weekend
                calendar_colors[date_str] = 'light-blue'
            else:
                available_hours = availability_map.get(date_str, 0)
                if available_hours == 8:
                    calendar_colors[date_str] = 'green'  # Fully available
                elif 0 < available_hours < 8:
                    calendar_colors[date_str] = 'yellow'  # Partial
                elif available_hours == 0:
                    calendar_colors[date_str] = 'orange'  # Leave
                else:
                    calendar_colors[date_str] = 'grey'

            current_date += pd.Timedelta(days=1)

        # ✅ SEND JSON RESPONSE
        return jsonify({"calendar_colors": calendar_colors})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
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
    "2025-11-20": "light-blue",
    "2025-11-21": "light-blue"
  }
}
```

**🎨 CSS (style.css):**

```css
.date-green {
  background-color: #28a745 !important;
} /* Fully available */
.date-red {
  background-color: #dc3545 !important;
} /* Booked */
.date-yellow {
  background-color: #ffc107 !important;
} /* Partially available */
.date-orange {
  background-color: #fd7e14 !important;
} /* Leave */
.date-light-blue {
  background-color: #add8e6 !important;
} /* Weekend */
.date-grey {
  background-color: #808080 !important;
} /* Unavailable */
```

---

## 🔄 COMPLETE DATA FLOW (LOGIN → BOOKING)

```
1. 📱 JS: User enters PSID/password in form
   ↓
2. 📱 JS: fetch('/login', {POST, {username, password_hash}})
   ↓
3. 🐍 PY: @app.route('/login') receives request.get_json()
   ↓
4. 🐍 PY: Validates credentials from USERS dict
   ↓
5. 🐍 PY: return jsonify({success: True, psid, scheduler_name})
   ↓
6. 📱 JS: Receives JSON → sessionStorage.setItem("psid", data.psid)
   ↓
7. 📱 JS: Calls loadAudits() function
   ↓
8. 📱 JS: fetch('/audits?psid=' + psid)
   ↓
9. 🐍 PY: @app.route('/audits') filters audit_map_df by PSID
   ↓
10. 🐍 PY: return jsonify({audit_numbers: ["2025-US-001", ...]})
   ↓
11. 📱 JS: Populates <select> dropdown with audits
   ↓
12. 📱 JS: User selects audit → loadAuditData(auditNumber)
   ↓
13. 📱 JS: fetch('/employees/' + auditNumber + '?psid=' + psid)
   ↓
14. 🐍 PY: @app.route('/employees/<audit_number>')
   ↓
15. 🐍 PY: load_input_new() → Reads Dataiku dataset
   ↓
16. 🐍 PY: Filters by audit_number, cleans data, renames columns
   ↓
17. 🐍 PY: auto_book_rank_1_auditors() runs in background
   ↓
18. 🐍 PY: return jsonify([{PSID, FullName, Rank, ...}])
   ↓
19. 📱 JS: Renders auditors table in HTML
   ↓
20. 📱 JS: fetch('/api/calendar_colors/' + auditNumber + '/' + psid)
   ↓
21. 🐍 PY: Calculates colors based on availability/bookings
   ↓
22. 🐍 PY: return jsonify({calendar_colors: {date: color}})
   ↓
23. 📱 JS: Initializes Flatpickr calendar with color-coded dates
   ↓
24. 📱 JS: User selects dates and clicks "Book Selected Dates"
   ↓
25. 📱 JS: fetch('/api/manual_book', {POST, bookingData})
   ↓
26. 🐍 PY: @app.route('/api/manual_book')
   ↓
27. 🐍 PY: convert_dates_to_blocks(['2025-11-15', '2025-11-16'])
   ↓
28. 🐍 PY: check_date_clash(psid, start, end)
   ↓
29. 🐍 PY: calculate_booking_metrics() → Splits by week
   ↓
30. 🐍 PY: write_bookings_df(updated_bookings) → Dataiku.write_with_schema()
   ↓
31. 🐍 PY: return jsonify({success: True})
   ↓
32. 📱 JS: Shows alert("Booking successful!")
   ↓
33. 📱 JS: Calls loadAuditData() to refresh UI
```

---

## 📂 KEY PYTHON FUNCTIONS

### **Dataiku Read/Write**

```python
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

### **Date Conflict Check**

```python
def check_date_clash(psid, start_date, end_date):
    bookings = load_bookings()
    emp_bookings = bookings[bookings['PSID'] == psid]

    for _, row in emp_bookings.iterrows():
        booked_start = pd.to_datetime(row['BookedFrom'])
        booked_end = pd.to_datetime(row['BookedTo'])

        # Check overlap
        if not (end_date < booked_start or start_date > booked_end):
            return False, row['audit_number']  # ← Clash detected

    return True, None  # ← No clash
```

### **Convert Dates to Blocks**

```python
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
            # Save current block
            date_blocks.append({
                'BookedFrom': current_block_start.strftime('%Y-%m-%d'),
                'BookedTo': current_block_end.strftime('%Y-%m-%d')
            })
            # Start new block
            current_block_start = parsed_dates[i]
            current_block_end = parsed_dates[i]

    # Add last block
    date_blocks.append({
        'BookedFrom': current_block_start.strftime('%Y-%m-%d'),
        'BookedTo': current_block_end.strftime('%Y-%m-%d')
    })

    return date_blocks
```

---

## 🚀 SUMMARY FOR MANAGER

**Application:** Smart Scheduling Assistant (Flask + JavaScript)

**Files:**

- `backend.py` → 20 Flask API endpoints (Python)
- `script.js` → Frontend logic with Fetch API calls (JavaScript)
- `index.html` → UI structure (HTML + Bootstrap)

**How JS & Python Connect:**

1. JS uses `fetch(dataiku.getWebAppBackendUrl('/endpoint'))`
2. Python receives via `@app.route('/endpoint')` decorator
3. Data exchanged as JSON: `request.get_json()` → `jsonify()`
4. Python reads/writes Dataiku datasets (CSV files)

**Main APIs Used:**

1. `/login` → User authentication
2. `/audits` → Get user's audits dropdown
3. `/employees/<audit_number>` → Load auditors table
4. `/api/manual_book` → Create bookings
5. `/api/calendar_colors/<audit_number>/<psid>` → Color-code dates

**Key Features:**

- Real-time availability checking
- Automatic date conflict detection
- Color-coded calendar (green=available, red=booked, yellow=partial, orange=leave)
- Excel export functionality
- Auto-booking for Rank 1 auditors

---

**END OF KNOWLEDGE TRANSFER**
