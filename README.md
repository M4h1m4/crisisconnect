# CrisisConnect — Emergency Resource Agent

> **An AI agent that connects people in crisis to the nearest help in seconds.**

CrisisConnect is not a chatbot. It is an action-oriented AI agent that understands any crisis — from hunger to a stolen wallet to a medical emergency — finds real-world resources near you, and tells you exactly what to do next.

---

## The Problem

When crisis strikes, people don't know where to go or what to do. Whether it's finding food, a place to sleep, the nearest hospital, or what to do when your car breaks down — searching the internet under stress is slow and confusing. CrisisConnect eliminates that friction with an AI agent that acts in seconds.

---

## Features

### Core Features

| Feature | Description |
|---|---|
| **Dynamic Crisis Analysis** | LLM analyzes any situation — not just fixed categories. Handles food, shelter, medical, financial, legal, automotive, safety, and more |
| **LLM-Generated Search** | Instead of hardcoded search terms, the Nemotron model decides what to search for based on your specific situation |
| **Immediate Advice** | The agent gives you urgent action items BEFORE searching for resources (e.g., "Call your bank to freeze your card") |
| **Urgency Detection** | Classifies situations as critical/high/medium/low and adjusts response tone accordingly |
| **Location Awareness** | Auto-detect your location via browser GPS, or type a location like "near SJSU" and the agent resolves it via Google Geocoding |
| **Real-Time Resource Discovery** | Searches Google Maps Places API with LLM-generated queries to find relevant nearby resources |
| **Image-Based Crisis Detection** | Upload a photo of a crisis situation — the Vision AI analyzes what's happening and provides safety guidance |
| **Authority Notification** | For critical situations (fire, medical, accident), the system can trigger authority notifications with precise location data |
| **Interactive Map** | Embedded Google Map drops color-coded pins for every resource found |
| **Chat Interface** | Clean, accessible chat UI for conversational interaction with the agent |

### How It Handles Any Crisis

| User Says | Agent Does |
|---|---|
| "I'm hungry and near SJSU" | Searches for food banks, community kitchens, soup kitchens nearby |
| "My credit card was stolen" | Advises to call bank immediately, searches for police stations and bank branches |
| "My car broke down on the highway" | Tells user to turn on hazards, searches for tow trucks and auto repair shops |
| "Someone is having a seizure" | Tells user to call 911, clears area, searches for hospitals and ERs |
| "I need a lawyer, I got scammed" | Searches for legal aid and free legal clinics |
| "I'm locked out of my apartment" | Searches for locksmiths and 24-hour services |
| _Uploads photo of a fire_ | Vision AI analyzes the image, provides escape guidance, notifies authorities |

### API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Health check |
| `/api/chat` | POST | Main chat endpoint — text-based crisis assistance |
| `/api/crisis/image` | POST | Crisis report with image description + ARCore/GPS location |
| `/api/crisis/analyze-image` | POST | Upload an image for Vision AI analysis |
| `/api/crisis/analyze-and-guide` | POST | Upload image + get full agent guidance with nearby resources |

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                       │
│                                                           │
│  ┌──────────────┐  ┌──────────────────────────────────┐  │
│  │   Chat UI     │  │   Google Map (pins/markers)      │  │
│  │  - Messages   │  │   - Color-coded resource pins    │  │
│  │  - Input bar  │  │   - User location marker         │  │
│  │  - Cards      │  │   - Click for details            │  │
│  │  - GPS button │  │                                  │  │
│  └──────┬───────┘  └──────────┬───────────────────────┘  │
│         └──────────┬───────────┘                          │
│                    │ REST API                              │
└────────────────────┼──────────────────────────────────────┘
                     │
┌────────────────────┼──────────────────────────────────────┐
│             BACKEND (FastAPI + LangGraph)                   │
│                    │                                        │
│  ┌─────────────────▼──────────────────────┐                │
│  │          LangGraph Agent                │                │
│  │                                         │                │
│  │  1. Situation Analyzer Node             │                │
│  │     LLM analyzes crisis, generates      │                │
│  │     search queries + immediate advice   │                │
│  │                                         │                │
│  │  2. Location Resolver Node              │                │
│  │     Google Geocoding API                │                │
│  │                                         │                │
│  │  3. Resource Finder Node                │                │
│  │     Google Places API (dynamic queries) │                │
│  │                                         │                │
│  │  4. Response Generator Node             │                │
│  │     LLM generates actionable guidance   │                │
│  └─────────────────────────────────────────┘                │
│                                                             │
│  ┌─────────────────────────────────────────┐                │
│  │          Vision Pipeline                 │                │
│  │  - Image upload + base64 encoding        │                │
│  │  - Nemotron Nano 12B VL analysis         │                │
│  │  - Crisis classification + severity      │                │
│  │  - Authority notification (mock)         │                │
│  └─────────────────────────────────────────┘                │
│                                                             │
│  LLM: NVIDIA Nemotron-3-Super-120B via OpenRouter           │
│  Vision: NVIDIA Nemotron-Nano-12B-V2-VL via OpenRouter      │
└─────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| **LLM** | NVIDIA Nemotron 3 Super 120B A12B (via OpenRouter) |
| **Vision Model** | NVIDIA Nemotron Nano 12B V2 VL (via OpenRouter) |
| **Agent Framework** | LangGraph + LangChain |
| **Backend** | Python 3.13, FastAPI |
| **Frontend** | React 19, Vite, Tailwind CSS |
| **Maps** | Google Maps JavaScript API + Places API + Geocoding API |

---

## Example Interactions

**User:** "I haven't eaten today and I'm near SJSU."

**Agent:**
> Sacred Heart Community Kitchen is your best option — 187 N Market St, San Jose. Open now.
> Walk south on S 4th St, about 10 minutes. Second Harvest Food Bank is also nearby at 4001 N 1st St.

**User:** "My wallet was stolen near downtown San Jose"

**Agent:**
> Call your bank immediately to freeze your cards. The nearest police station is San Jose Police Department — 201 W Mission St, 0.5 miles away. Head there to file a report. Chase Bank branch is at 170 Park Center Plaza if you need a replacement card.

**User:** _Uploads photo of a car accident_

**Agent:**
> This appears to be a vehicle collision. If anyone is injured, call 911 immediately. Do not move injured persons. The nearest hospital is Santa Clara Valley Medical Center — 751 S Bascom Ave, 2.1 miles away.

---

## Getting Started

### Prerequisites
- Python 3.13+
- Node.js 18+
- OpenRouter API key ([openrouter.ai](https://openrouter.ai))
- Google Maps API key (Places, Geocoding, Maps JavaScript APIs enabled)

### Backend Setup
```bash
cd backend
uv venv venv --python 3.13
source venv/bin/activate
uv pip install -r ../requirements.txt
cp .env.example .env   # Add your API keys
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env   # Add your Google Maps key
npm run dev
```

### Environment Variables

**Backend (`backend/.env`):**

| Variable | Description |
|---|---|
| `OPENROUTER_API_KEY` | Your OpenRouter API key (sk-or-...) |
| `GOOGLE_MAPS_API_KEY` | Google Maps API key (Places + Geocoding + JS Maps) |

**Frontend (`frontend/.env`):**

| Variable | Description |
|---|---|
| `VITE_GOOGLE_MAPS_API_KEY` | Same Google Maps API key |
| `VITE_API_URL` | Backend URL (default: `http://localhost:8000`) |

---

## Project Structure

```
CrisisConnect/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app — chat, image, and crisis endpoints
│   │   ├── config.py            # Settings (OpenRouter, Google Maps, model names)
│   │   ├── agent/
│   │   │   ├── graph.py         # LangGraph agent workflows (chat + crisis)
│   │   │   ├── nodes.py         # Agent nodes (analyze, locate, find, respond)
│   │   │   └── state.py         # Agent state schema
│   │   ├── services/
│   │   │   ├── vision.py        # NVIDIA Vision model integration
│   │   │   └── crisis.py        # Crisis classification + authority notification
│   │   ├── tools/
│   │   │   ├── google_places.py # Google Places API (dynamic query search)
│   │   │   └── google_geocode.py# Google Geocoding (text → lat/lng)
│   │   └── models/
│   │       └── schemas.py       # Pydantic schemas (ChatRequest, Resource, etc.)
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # Split-panel layout (chat + map)
│   │   ├── components/
│   │   │   ├── ChatPanel.tsx    # Chat messages + input
│   │   │   ├── MapPanel.tsx     # Google Map with colored markers
│   │   │   ├── MessageBubble.tsx# Message display
│   │   │   └── ResourceCard.tsx # Resource card with directions link
│   │   ├── hooks/
│   │   │   └── useGeolocation.ts# Browser geolocation hook
│   │   └── services/
│   │       └── api.ts           # Backend API client
│   ├── package.json
│   └── .env.example
├── requirements.txt
├── README.md
└── .gitignore
```

---

## License

MIT
