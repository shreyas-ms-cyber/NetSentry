# 🛡️ NetSentry — Network Monitoring Dashboard

**NetSentry** is a production-ready, hybrid-architecture network monitoring and security-visibility platform for SOC analysts, network engineers, and security practitioners. It discovers devices on your authorized local network, identifies open ports, collects live traffic statistics, and detects critical network changes through a premium, dark-mode SOC/NOC dashboard.



![Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-000000?logo=vercel&logoColor=white)




![Render](https://img.shields.io/badge/Deployed%20on-Render-46E3B7?logo=render&logoColor=white)




![License](https://img.shields.io/badge/License-MIT-blue)




![Architecture](https://img.shields.io/badge/Architecture-Hybrid%20Local%20Agent-orange)




![Live Demo](https://img.shields.io/badge/Live%20Demo-Online-brightgreen?logo=vercel)



> 🔍 **Architecture:** Hybrid local-agent model — the cloud never scans your network. All discovery, scanning, and packet capture happens on your machine.

## 🔗 Live Demo

**[Try NetSentry Live →](https://your-netsentry-url.vercel.app)**

> ⚠️ Note: Backend is on Render's free tier — first load may take 30–60 seconds to spin up if idle.

---

## 🌟 Executive Overview
In modern networks, visibility is the first line of defense. NetSentry gives security teams a real-time, explainable view of their local network — showing what's connected, which ports are open, how traffic flows, and what changed — all from a polished, enterprise-grade dashboard.

### Core Features
- **Device Discovery**: ARP-based scanning that automatically finds every active device on your authorized LAN.
- **Port Scanning**: TCP port scans with OPEN/CLOSED/FILTERED status, mapped to common services.
- **Live Traffic Monitoring**: Packets per second, bandwidth usage, and protocol breakdown (TCP/UDP/ICMP/Other).
- **Intelligent Alerting**: Automatic alerts for new devices, newly opened ports, and devices going offline.
- **Premium SOC Dashboard**: Real-time KPI cards, traffic timelines, protocol distribution, and top talkers.
- **Security-First**: Scanning is strictly limited to private RFC1918 networks — no public IP scanning, no arbitrary targets.

---

## 🛠️ Installation & Setup

### Prerequisites
- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL** (or SQLite for dev)

### 1. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with DATABASE_URL and AGENT_API_KEY
python run.py
```
The server will start at `http://localhost:5000`.

### 2. Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env
# Edit .env with VITE_API_BASE_URL
npm run dev
```
Runs at `http://localhost:5173`.

### 3. Local Agent Setup
```bash
cd agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with BACKEND_URL and AGENT_API_KEY
sudo python -m netsentry_agent.main
```
> The agent requires root/sudo privileges for packet capture and ARP scanning.

---

## 🏗️ Architecture

NetSentry follows a hybrid local-agent model:

```
Authorized Local Network
         │
         ▼
  NetSentry Local Agent (Python + Scapy)
  • ARP Discovery  • Port Scanning
  • Packet Capture • Traffic Stats
         │ HTTPS + X-Agent-Key
         ▼
  Flask Backend (Render)
  • Validate & authenticate agent
  • Store telemetry  • Serve REST API
         │
         ▼
  PostgreSQL (Neon) — historical telemetry
         │ HTTPS
         ▼
  React Frontend (Vercel) — SOC/NOC Dashboard
```

- **Frontend**: React 18, Vite, Chart.js, Bootstrap 5, Font Awesome 6.
- **Backend**: Python 3.11, Flask 3, SQLAlchemy, Flask-CORS.
- **Agent**: Python 3.11, Scapy, psutil, requests.
- **Database**: PostgreSQL (Neon) with SQLite fallback for development.

---

## 🎓 Interview & Portfolio Guide
If presenting this in an interview, focus on these points:
1. **The Hybrid Architecture**: Why the local agent is essential (cloud platforms can't access your LAN) and how it keeps scanning secure and local.
2. **Network Security**: Strict RFC1918 private-range validation, agent API key authentication, CORS protection.
3. **Real-time Data Flow**: How the agent pushes telemetry via authenticated REST APIs and the frontend polls for live updates.
4. **SOC Workflow**: How alerts, device status, and traffic analytics power a complete monitoring cycle.
5. **Tech Choices**: Why Python (Scapy/psutil) for the agent, Flask for the API, and React for the dashboard.

---

## 🚀 Future Roadmap
- [ ] **VirusTotal/Shodan Integration** – Enrich IP and domain reputation.
- [ ] **Real-time WebSocket Updates** – Replace polling with live push.
- [ ] **Multi-user Roles** – Admin, Analyst, Viewer permissions.
- [ ] **Mobile-first Companion App** – React Native or PWA.

---

## 📝 License
MIT License — see [LICENSE](LICENSE) for details.

---

**Author:** Shreyas M S · [GitHub](https://github.com/shreyas-ms-cyber) · [LinkedIn](https://linkedin.com)
