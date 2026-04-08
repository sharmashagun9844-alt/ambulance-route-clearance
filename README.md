# 🚑 Ambulance Route Clearance Environment

> A real-world OpenEnv environment where an AI agent controls traffic signals to clear the fastest route for ambulances in emergency situations.

**Team:** The Fine-Tuners  
**Hackathon:** Meta PyTorch OpenEnv Hackathon x Scaler School of Technology  

---

## 🎯 What This Environment Does

The agent acts as an intelligent traffic controller. Given a virtual city with roads and traffic signals, and an ambulance trying to reach a hospital, the agent must:
- Clear red signals on the ambulance's route
- Reroute around blocked roads (Task 3)
- Minimize the time taken to reach the hospital

Every second counts in a real emergency — this environment trains AI agents to make those seconds matter. 🏥

---

## 🎯 The Problem Statement (The "Why")
"In emergency response, every second counts. Traditional GPS often optimizes for the shortest distance, not the fastest clearance. This project implements a priority-based pathfinding system that clears routes for emergency vehicles by calculating dynamic traffic weights."

---

## 🎯 Technical Architecture (The "How")

Logic Engine: Explain how you assigned "weights" to roads (e.g., a road with high traffic has a higher weight, making the algorithm avoid it).

Data Structures: Mention if you used Graphs (Nodes = Intersections, Edges = Roads) and Priority Queues.

---

## 🎯 The "First Principles" Section

"Built from scratch without high-level AI wrappers to ensure full control over the decision-making logic and system transparency."

---

## 🎯 Future Roadmap (The "Security" Link)

"Planned Update: Implementing AES-256 encryption for vehicle-to-infrastructure (V2I) communication to prevent unauthorized route manipulation."

## 📋 Tasks

| Task | Difficulty | Description | Signals | Ambulances |
|------|-----------|-------------|---------|------------|
| Task 1 | Easy | Single signal, light traffic | 1 | 1 |
| Task 2 | Medium | Full route optimization | 3 | 1 |
| Task 3 | Hard | Multi-ambulance emergency + blocked road | 4 | 2 |

---

## 🔧 Action Space

```json
{
  "signal_id": 1,
  "new_status": "green",
  "reroute": false
}
```

| Field | Type | Description |
|-------|------|-------------|
| signal_id | int | ID of the traffic signal to control |
| new_status | str | "green" to clear, "red" to block |
| reroute | bool | True to reroute ambulance around blocked road |

---

## 👁️ Observation Space

```json
{
  "ambulance_position": 0,
  "hospital_position": 5,
  "signals": [{"id": 1, "position": 2, "status": "red", "traffic": "light"}],
  "blocked_roads": [],
  "time_elapsed": 0,
  "ambulances": 1,
  "reward": 0.0,
  "done": false,
  "message": "Episode started"
}
```

---

## 🏆 Scoring

| Action | Reward |
|--------|--------|
| Clear signal (light traffic) | +0.3 |
| Clear signal (moderate traffic) | +0.4 |
| Clear signal (heavy traffic) | +0.5 |
| Correct reroute | +0.3 |
| Ambulance reaches hospital | +0.5 |

Final score normalized to **0.0 – 1.0**

---

## 🚀 Setup

### Run locally
```bash
pip install -r server/requirements.txt
uvicorn server.app:app --reload --port 7860
```

### Run with Docker
```bash
docker build -t ambulance-env .
docker run -p 7860:7860 ambulance-env
```

---

## 🌐 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/reset` | POST | Start new episode |
| `/step` | POST | Agent takes action |
| `/state` | GET | Current environment state |
| `/tasks` | GET | List tasks + action schema |
| `/grader` | GET | Score after episode |
| `/baseline` | GET | Run baseline agent on all tasks |

---

## 💡 Real World Impact

In India, ambulances get stuck in traffic every single day — every minute of delay costs lives. This environment trains AI agents to intelligently manage traffic signals in real emergency scenarios.
