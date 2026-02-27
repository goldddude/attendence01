# Quick Start Guide - Faculty Authentication System

## 🚀 Starting the Application

1. **Start the server:**
   ```bash
   python run_simple.py
   ```

2. **Access the application:**
   - Open your browser and go to: `http://localhost:5000`
   - Or use your computer's IP address for NFC scanning: `http://192.168.x.x:5000`

## 👤 Testing Faculty Login

### First Time Login

1. **Navigate to Login Page:**
   - Click "Faculty Login" button on homepage
   - Or go directly to: `http://localhost:5000/login.html`

2. **Enter Faculty Details:**
   - **Name:** Enter any name (e.g., "Dr. John Smith")
   - **Email:** Enter any email (e.g., "john.smith@university.edu")
   - Click "Send OTP"

3. **Verify OTP:**
   - The OTP will be displayed on screen (e.g., "123456")
   - In production, this would be sent to the email
   - Enter the 6-digit OTP in the input field
   - (Optional) Check "Remember me for 30 days" for persistent login
   - Click "Verify & Login"

4. **Success!**
   - You'll be redirected to the Scan Attendance page
   - Your name and email will be displayed at the top

### Subsequent Logins (with Remember Me)

If you checked "Remember me":
- Just visit the login page
- You'll be automatically logged in and redirected
- No need to enter OTP again for 30 days

## 📱 Recording Attendance

1. **After Login:**
   - You'll see your faculty info displayed
   - Select a **Section** (S-01 to S-20)
   - Select a **Subject** (Operating System, Java, Python, etc.)
   - Click "Start Scanning"

2. **Scan NFC Cards:**
   - Tap NFC-enabled ID cards near your Android device
   - Each scan will show:
     - Student name
     - Register number
     - Section
     - Subject
     - Timestamp

3. **Stop Scanning:**
   - Click "Stop Scanning" when done
   - Click "Clear Log" to clear the scan history

## 📊 Viewing Statistics

1. **Access Dashboard:**
   - Click "Statistics" in the navigation (after login)
   - Or go to: `http://localhost:5000/dashboard.html`

2. **View Data:**
   - See total students, present today, absent today
   - View attendance trends chart
   - See top attendees
   - View students by class/section

3. **Logout:**
   - Click the "Logout" button in the top-right corner
   - Confirms before logging out
   - Redirects to login page

## 🔐 Testing Different Scenarios

### Scenario 1: New Faculty Member
```
Name: Dr. Sarah Johnson
Email: sarah.johnson@university.edu
Section: S-05
Subject: Computer Networks
```

### Scenario 2: Different Section/Subject
```
Name: Prof. Michael Chen
Email: michael.chen@university.edu
Section: S-12
Subject: Data Structures and Algorithms (DSA)
```

### Scenario 3: Remember Me Feature
1. Login with any faculty
2. Check "Remember me for 30 days"
3. Close browser completely
4. Reopen and visit login page
5. Should auto-login without OTP

## 🧪 Testing Checklist

- [ ] Can create new faculty account
- [ ] OTP is generated and displayed
- [ ] Can verify OTP and login
- [ ] Faculty name appears in header
- [ ] Can select section (required)
- [ ] Can select subject (required)
- [ ] Can start NFC scanning
- [ ] Attendance records show section and subject
- [ ] Can access Statistics dashboard
- [ ] Statistics show faculty name
- [ ] Can logout successfully
- [ ] Remember me works across sessions
- [ ] Protected pages redirect to login when not authenticated

## 🐛 Troubleshooting

### Issue: Can't access login page
**Solution:** Make sure the server is running (`python run_simple.py`)

### Issue: OTP not showing
**Solution:** Check browser console for errors. OTP should appear in the blue info box.

### Issue: Remember me not working
**Solution:** 
- Check if cookies/localStorage are enabled
- Try clearing browser cache
- Make sure you checked the "Remember me" checkbox

### Issue: NFC not working
**Solution:**
- Use Chrome browser on Android
- Enable NFC in phone settings
- Access via IP address (not localhost)
- Make sure you're on the same WiFi network

### Issue: Can't access dashboard
**Solution:** 
- Make sure you're logged in
- Check if session is active
- Try logging in again

## 📝 Sample Test Data

### Faculty Accounts to Test
```
1. Name: Dr. Alice Brown
   Email: alice.brown@university.edu
   Sections: S-01, S-02, S-03

2. Name: Prof. Bob Wilson
   Email: bob.wilson@university.edu
   Sections: S-10, S-11

3. Name: Dr. Carol Davis
   Email: carol.davis@university.edu
   Sections: S-15, S-16, S-17
```

### Subjects to Test
- Operating System
- Engineering Mathematics
- Computer Networks
- DAA (Design and Analysis of Algorithms)
- ACD (Advanced Computer Design)
- DSA (Data Structures and Algorithms)
- Java Programming
- Python Programming

## 🎯 Expected Behavior

### Login Flow
1. Enter name and email → OTP generated
2. Enter OTP → Session created
3. Redirected to scan page → Faculty info displayed
4. Select section and subject → Can start scanning
5. Scan NFC cards → Attendance recorded with section/subject
6. Logout → Session cleared, redirected to login

### Protected Pages
- `/scan-attendance.html` - Requires login
- `/dashboard.html` - Requires login
- All redirect to `/login.html` if not authenticated

### Session Persistence
- **Without Remember Me:** Session lasts until browser is closed
- **With Remember Me:** Session lasts 30 days
- **After Logout:** All sessions cleared immediately

## 🔄 Next Steps After Testing

1. **Integrate Email Service:**
   - Configure SMTP settings
   - Update faculty_service.py to send actual emails
   - Remove OTP display from UI

2. **Add Faculty Management:**
   - Admin panel to manage faculty
   - Assign sections to faculty
   - Assign subjects to faculty

3. **Enhanced Analytics:**
   - Filter by section
   - Filter by subject
   - Faculty-specific reports

4. **Export Features:**
   - Export attendance by section
   - Export attendance by subject
   - Generate PDF reports

---

**Happy Testing! 🎉**

For issues or questions, check the main documentation in `FACULTY_AUTH_IMPLEMENTATION.md`
