# 🎓 KIIT Campus Navigator

A web-based campus pathfinding application for KIIT University, Bhubaneswar. It uses the **A\* Search Algorithm** to compute the optimal route between campus buildings, visualized on an interactive map.

---

## ✨ Features

- 🗺️ **Interactive Map** — Real-time campus map powered by Leaflet.js + OpenStreetMap
- 🤖 **A\* Pathfinding** — Optimal route calculation using heuristic-based search
- 🎙️ **Voice Commands** — Hands-free navigation using speech recognition
- 📍 **Animated Path** — Dashed polyline drawn between start and destination markers
- 📝 **Feedback Form** — Sends feedback directly to email via Gmail SMTP
- 🌙 **Dark Mode** — Toggle between light and dark themes
- 📱 **Responsive** — Works on desktop and mobile

---

## 🗂️ Project Structure

```
kiit-campus-navigator/
├── app.py                  # Flask backend, A* algorithm, SMTP, voice
├── templates/
│   └── index.html          # Main HTML template (Jinja2)
├── static/
│   ├── css/
│   │   └── style.css       # Styling + dark mode
│   └── js/
│       └── script.js       # Map, pathfinding UI, voice, feedback
├── .env                    # Secret credentials (never commit this)
├── .vscode
│   └── settings.json
├── .gitignore
└── requirements.txt
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/kiit-campus-navigator.git
cd kiit-campus-navigator
```

### 2. Install dependencies
```bash
pip install flask python-dotenv SpeechRecognition pyttsx3 pyaudio
```

### 3. Configure environment variables

Create a `.env` file in the project root:
```
SENDER_EMAIL=yourname@gmail.com
SENDER_PASSWORD=xxxx xxxx xxxx xxxx
```

> **How to get a Gmail App Password:**
> 1. Enable 2-Step Verification at [myaccount.google.com/security](https://myaccount.google.com/security)
> 2. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
> 3. Create a new app password and paste it above
>
> ⚠️ Do **not** use an institutional `@kiit.ac.in` email — Google Workspace accounts have SMTP disabled by the admin.

### 4. Run the app
```bash
python app.py
```

Visit `http://127.0.0.1:5000` in your browser.

---

## 🧠 Algorithm

The app uses **A\* Search** for pathfinding across the campus graph.

| Property | Detail |
|---|---|
| Algorithm | A* Search |
| Heuristic | Euclidean distance (lat/lng → km) |
| Graph | Manually defined adjacency list |
| Output | Optimal path + total distance + nodes explored |

Campus nodes and edge weights (in km) are defined in `app.py` under `LOCATIONS` and `GRAPH`.

---

## 🗺️ Campus Locations

| Campus | Coordinates |
|---|---|
| Campus 3 | 20.3531, 85.8165 |
| Campus 6 | 20.3525, 85.8195 |
| Campus 8 | 20.3512, 85.8194 |
| Campus 12 | 20.3545, 85.8194 |
| Campus 13 | 20.3565, 85.8185 |
| Campus 14 | 20.3561, 85.8154 |
| Campus 15 | 20.3487, 85.8148 |
| Campus 17 | 20.3492, 85.8194 |
| Campus 20 | 20.3540, 85.8162 |
| Campus 25 | 20.3640, 85.8162 |

---

## 🎙️ Voice Command Usage

Click **"Use Voice Command"** and say:
```
"Start Campus 6 Destination Campus 25"
```
The app will automatically select the locations and find the path.

---

## 🔒 Security Notes

- Never commit your `.env` file — it's listed in `.gitignore`
- Never hardcode credentials directly in `app.py`
- Rotate your App Password if it's ever accidentally exposed

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Pathfinding | A* Search (custom implementation) |
| Frontend | HTML, CSS, JavaScript |
| Map | Leaflet.js + OpenStreetMap |
| Voice | SpeechRecognition + pyttsx3 |
| Email | Gmail SMTP + python-dotenv |

---

## 👨‍💻 Author

**KIIT University — CSE Project**  
📧 23051825@kiit.ac.in  
☎ +91 9039860092

---

© 2026 KIIT University | Smart Campus Navigator
