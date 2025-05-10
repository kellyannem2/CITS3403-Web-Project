# FitTrack 🏃‍♀️🍎

A fitness tracker web app for logging meals, tracking exercises, and sharing your progress with friends or groups.

---

## 📑 Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Setup and Installation](#setup-and-installation)
- [Troubleshooting](#troubleshooting)
- [Usage](#usage)
- [Contributing](#contributing)
- [License & References](#license--references)

---

## ✨ Features

- **User authentication** with registration, login, and secure password change/reset
- **Flash messages** for feedback on actions (e.g. login errors, save confirmations)
- **Profile avatars** — upload a custom image for your account
- **Encrypted USDA API key storage** via SQLAlchemy-Utils and AES encryption
- **Meal logging** via:
  - Searching a central food database
  - Custom meal entry with name, calories, and timestamp
- **Exercise logging** with calorie burn calculation
- **Dynamic charts** for weekly calorie intake using Chart.js
- **Share your stats** with a friend or group via a modal
- **Group leaderboard** support — track progress with your team

---

## 🧪 Technologies Used

### Frontend:
- HTML5
- CSS3
- JavaScript
- Flatpickr (date/time picker)
- Chart.js (weekly calorie charts)

### Backend:
- Python 3
- Flask
- Flask-WTF (form handling)
- Flask-Migrate (database migrations)
- SQLAlchemy (ORM)
- SQLite (development database)
- SQLAlchemy-Utils (encrypted fields)

---

## ⚙️ Setup and Installation

1. **Clone the repo:**
   ```bash
   git clone https://github.com/kellyannem2/CITS3403-Web-Project.git FitTrack
   cd FitTrack
   ```

2. **Create a virtual environment:**

   **Windows:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

   **Mac/Linux:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set the encryption key (optional, auto-generated if not set):**
   ```bash
   set DB_ENCRYPTION_KEY=<your base64 key>
   ```

5. **Initialize the database:**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. **Run the app:**

   **Windows PowerShell:**
   ```powershell
   $env:FLASK_APP = "app"
   flask run
   ```

   **Mac/Linux or Git Bash:**
   ```bash
   export FLASK_APP=app
   flask run
   ```

---
### 🔑 USDA API Key (Optional, but recommended)

To use the food database search feature:

1. Go to [https://fdc.nal.usda.gov/api-key-signup.html](https://fdc.nal.usda.gov/api-key-signup.html)
2. Sign up with your email address to generate a **free API key**
3. Once you receive the key:
   - Log in to your FitTrack account
   - Navigate to **My Account > USDA API Key**
   - Enter the key and your current password
   - Save changes — the key is encrypted before being stored

---

## 🛠️ Troubleshooting

If you're setting up FitTrack for the first time and run into issues, here are some common fixes:

- **App won’t start?**
  - Did you activate your virtual environment?
    ```bash
    .\venv\Scripts\activate  # Windows
    ```
  - Did you run `flask run` with the right environment variable?
    ```bash
    $env:FLASK_APP = "app"
    ```

- **Missing dependencies?**
  - Run:
    ```bash
    pip install -r requirement.txt
    ```

- **Database migration fails or tables missing?**
  - Run:
    ```bash
    flask db migrate -m "init"
    flask db upgrade
    ```

- **Frontend isn’t showing charts or modals?**
  - Ensure you're connected to the internet for the CDN libraries (Chart.js, Flatpickr).
  - Open the browser dev tools (`F12`) and check the console for missing script errors.

If you're still stuck, open an issue or check the setup steps again from the top.


---

## 👟 Usage

1. **Sign up and log in**
2. **Log a meal** via food search or custom entry (includes calories + timestamp)
3. **Track your exercise** and view your weekly calorie burn
4. **Invite a friend or join a group** to:
   - Share stats privately
   - Contribute to a group-only leaderboard
5. **Manage your account**:
   - Upload a profile photo
   - Change email/password
   - Store an optional USDA API key

---

## 🤝 Contributing

1. Fork this repo
2. Create your branch: `git checkout -b feature/amazing-idea`
3. Commit your changes: `git commit -m "Add some feature"`
4. Push to the branch: `git push origin feature/amazing-idea`
5. Open a Pull Request 🎉

---

## 📄 License & References

- **License:** [MIT](LICENSE)
- **Logo source:** [`fittracker_logo.png`](static/images/fittracker_logo.png) generated or adapted from public domain/CC0 resources.
- This project was created as part of a university group project for CITS3403.

---