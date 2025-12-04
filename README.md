# Hackathon Registration Platform

A full-stack web application built using **Flask**, **SQLite**, and **SendGrid API** for managing hackathon events, user registrations, and admin operations.

---

## 🚀 Features

### 🔐 User Authentication
- Email-based login.
- OTP verification using **SendGrid Web API**.
- Secure session management.

### 📝 User Registration
- Users can register using:
  - Username
  - Email
- UUID-based user IDs.

### 🧾 Event Registration
- Users can register a team for any upcoming event.
- Each registration includes:
  - Team name  
  - Member details (name + phone)
  - Auto-stored registration date
  - Event mapping using event_id

### 🎉 Events Module
- Admins can add events with:
  - Event name  
  - Description  
  - Event date  
  - Last date  
  - Upload date  
  - Prizes  
- Events only show if **last_date ≥ today**.

### 🛠 Admin Dashboard
- Admin login with username & password.
- View all users.
- View all registrations.
- Event creation page.
- Secure admin session.

---

## 🗂 Database Structure

### **auth_users**
| Column   | Type        | Notes |
|----------|-------------|-------|
| id       | UUID String | PK |
| username | String      |  |
| email    | String      | Unique |

### **events**
| Column           | Type | Notes |
|------------------|------|-------|
| event_id         | INT  | PK, Auto Increment |
| event_name       | String |
| description      | Text |
| event_date       | String |
| last_date        | String |
| event_upload_date| String |
| creator          | UUID (FK to users) |
| prize1           | String |
| prize2           | String |

### **registrations**
| Column        | Type | Notes |
|---------------|------|-------|
| reg_id        | INT | PK |
| userid        | UUID | FK -> users |
| event_name    | String |
| event_id      | INT | FK -> events |
| email         | String |
| member1_name  | String |
| member1_phone | String |
| member2_name  | String |
| member2_phone | String |
| reg_date      | String |

### **admins**
| Column   | Type | Notes |
|----------|------|-------|
| admin_id | INT  | PK |
| name     | String | Unique |
| password | String |

---

## 📡 Tech Stack

- **Backend:** Flask, Python  
- **Database:** SQLite3  
- **Email Service:** SendGrid Web API  
- **Frontend:** HTML, CSS (custom UI based on your theme)  
- **Deployment:** Render Web Service  

---

## ⚙ Environment Variables

Create these in your Render dashboard:

| Variable | Description |
|---------|-------------|
| `SENDGRID_API_KEY_NEW` | sendgri api key |

---

## 📬 SendGrid Setup

1. Verify sender email (`ivinjose.work@gmail.com`)  
2. Create API key  
3. Add to Render environment  
4. Use SendGrid Python SDK

---

## ▶ How to Run Locally

```bash
pip install -r requirements.txt
set SENDGRID_API_KEY_NEW=sendgridapikey
python main.py
