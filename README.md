# Real-time-Process-Monitoring-Dashboard
Real-time Process Monitoring Dashboard

A Flask-based real-time system monitoring dashboard that displays CPU & Memory usage, along with process details. The UI is designed with a dark theme and neon accents for a modern look.

Features

✅ Live CPU & Memory Usage Monitoring (Updated in real-time)

✅ Graphical Representation using Chart.js

✅ Process Table showing the top 10 processes

✅ Process Termination (Kill button to stop a process)

✅ Dark Theme with Neon UI

Tech Stack

Frontend: HTML, CSS, JavaScript (Chart.js for graphs)

Backend: Flask (Python)

System Stats: psutil (CPU & Memory monitoring)

Installation & Setup

1️⃣ Clone the Repository

bash

git clone https://github.com/Akshita42/Real-time-Process-Monitor.git
cd Real-time-Process-Monitor

2️⃣ Create a Virtual Environment (Optional but Recommended)

bash

python -m venv venv
source venv/bin/activate  # For Mac/Linux
venv\Scripts\activate     # For Windows

3️⃣ Install Dependencies

bash

pip install -r requirements.txt

4️⃣ Run the Flask Server

bash

python app.py

➡ Open http://127.0.0.1:5000/ in your browser

How It Works

🔹 The Flask backend fetches system stats using psutil and sends JSON data to the frontend.

🔹 The UI updates dynamically to reflect CPU/memory usage and process details.

🔹 Clicking the Kill button terminates a selected process.

Screenshots

📌 Include a screenshot of your dashboard here

Future Enhancements

🚀 Add disk & network usage stats

🚀 Improve process management (pause, resume, priority adjustment)

🚀 Implement user authentication for access control

Contributing
Feel free to fork this project, create issues, or submit pull requests! 🎉

License
No Licsence 
