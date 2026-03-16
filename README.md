# CrisisConnect — Emergency Resource Agent

> **An AI agent that connects people in crisis to the nearest help in seconds.**

CrisisConnect is not a chatbot. It is an action-oriented AI agent that understands your emergency, finds real-world resources near you, and guides you to them — all in seconds.

---

## The Problem

During emergencies or crises, people often don't know:
- Where the nearest shelter is
- Where they can get food
- Where the closest hospital or clinic is
- What the next steps should be

Searching the internet under stress is slow and confusing. CrisisConnect eliminates that friction.

---

## Features

### Core Features (v1 — Hackathon Scope)

| Feature | Description |
|---|---|
| **Intent Understanding** | AI determines what you need — food, shelter, medical help, or emergency services — from natural language input |
| **Location Awareness** | Auto-detect your location via browser GPS, or type a location like "near SJSU" and the agent resolves it |
| **Real-Time Resource Discovery** | Searches Google Maps Places API to find real, nearby resources (shelters, food banks, hospitals, clinics, police stations) |
| **Smart Prioritization** | Ranks results by distance, open/closed status, and relevance to your situation |
| **Actionable Guidance** | Doesn't just list resources — tells you what to do: walking time, availability, directions |
| **Interactive Map** | Embedded Google Map drops pins for every resource found, with clickable markers for details |
| **Chat Interface** | Clean, accessible chat UI for conversational interaction with the agent |
| **Emergency Escalation** | Detects life-threatening situations and immediately surfaces 911/crisis hotline numbers |

### Resource Categories

| Category | Examples |
|---|---|
| **Food** | Food banks, community kitchens, free meal programs, soup kitchens |
| **Shelter** | Homeless shelters, temporary housing, overnight safe spaces, warming centers |
| **Medical** | Hospitals, urgent care clinics, free clinics, mental health crisis centers |
| **Emergency** | Police stations, fire stations, crisis hotlines, domestic violence hotlines |

### Stretch Features (if time permits)

| Feature | Description |
|---|---|
| **Category Tabs** | Quick-filter buttons for Food / Shelter / Medical / Emergency |
| **Dark Mode** | Reduced eye strain for nighttime use |
| **Mobile Responsive** | Fully usable on phones (critical for the target audience) |
| **Multi-Turn Context** | Agent remembers conversation history for follow-up questions |
| **Directions Link** | Direct "Get Directions" link opening Google Maps navigation |

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   FRONTEND (React)                   │
│                                                      │
│  ┌──────────────┐  ┌─────────────────────────────┐  │
│  │   Chat UI     │  │   Google Map (pins/markers) │  │
│  │  - Messages   │  │   - Resource locations       │  │
│  │  - Input bar  │  │   - User location            │  │
│  │  - Cards      │  │   - Click for details        │  │
│  └──────┬───────┘  └──────────┬──────────────────┘  │
│         │                      │                      │
│         └──────────┬───────────┘                      │
│                    │ REST API                         │
└────────────────────┼─────────────────────────────────┘
                     │
┌────────────────────┼─────────────────────────────────┐
│                BACKEND (FastAPI + LangGraph)           │
│                    │                                   │
│  ┌─────────────────▼──────────────────┐               │
│  │         LangGraph Agent             │               │
│  │                                     │               │
│  │  1. Intent Classifier Node          │               │
│  │     (food/shelter/medical/emergency)│               │
│  │                                     │               │
│  │  2. Location Resolver Node          │               │
│  │     (Google Geocoding API)          │               │
│  │                                     │               │
│  │  3. Resource Finder Node            │               │
│  │     (Google Maps Places API)        │               │
│  │                                     │               │
│  │  4. Response Generator Node         │               │
│  │     (NVIDIA Nemotron LLM)           │               │
│  └─────────────────────────────────────┘               │
│                                                        │
│  Tools:                                                │
│  ├── google_places_search(query, location, radius)     │
│  ├── google_geocode(address)                           │
│  └── get_directions(origin, destination)               │
│                                                        │
│  LLM: NVIDIA Nemotron-3-Super-49B via build.nvidia.com │
└────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| **LLM** | NVIDIA Nemotron 3 Super 49B (via NVIDIA API — `build.nvidia.com`) |
| **Agent Framework** | LangGraph + LangChain |
| **Backend** | Python 3.11+, FastAPI |
| **Frontend** | React 18, Vite, Tailwind CSS |
| **Maps** | Google Maps JavaScript API + Places API + Geocoding API |
| **Deployment** | Vercel (frontend), Railway (backend) |

---

## Example Interactions

**User:** "I haven't eaten today and I'm near SJSU."

**Agent:**
> Here are nearby free food options:
>
> 1. **Sacred Heart Community Kitchen** — 0.7 mi, Open now
>    _187 N Market St, San Jose_
>
> 2. **Second Harvest Food Bank** — 1.3 mi
>    _4001 N 1st St, San Jose_
>
> You can walk to Sacred Heart in about 10 minutes. Head south on S 4th St.

_(Map shows pins for both locations with your position marked)_

---

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- NVIDIA API key ([build.nvidia.com](https://build.nvidia.com))
- Google Maps API key (Places, Geocoding, Maps JavaScript APIs enabled)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Add your API keys
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env   # Add your Google Maps key
npm run dev
```

### Environment Variables

| Variable | Description |
|---|---|
| `NVIDIA_API_KEY` | Your NVIDIA API key from build.nvidia.com |
| `GOOGLE_MAPS_API_KEY` | Google Maps API key (Places + Geocoding + JS Maps) |

---

## Project Structure

```
CrisisConnect/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── agent/
│   │   │   ├── graph.py         # LangGraph agent definition
│   │   │   ├── nodes.py         # Agent nodes (intent, location, resources, response)
│   │   │   └── state.py         # Agent state schema
│   │   ├── tools/
│   │   │   ├── google_places.py # Google Places API tool
│   │   │   └── google_geocode.py# Google Geocoding tool
│   │   ├── models/
│   │   │   └── schemas.py       # Pydantic request/response models
│   │   └── config.py            # Settings and env vars
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── ChatPanel.tsx     # Chat messages + input
│   │   │   ├── MapPanel.tsx      # Google Map with markers
│   │   │   ├── MessageBubble.tsx # Individual message display
│   │   │   └── ResourceCard.tsx  # Resource result card
│   │   ├── hooks/
│   │   │   └── useGeolocation.ts # Browser geolocation hook
│   │   └── services/
│   │       └── api.ts            # Backend API client
│   ├── package.json
│   └── .env.example
├── docs/
│   └── plans/
├── README.md
└── .gitignore
```

---

## License

MIT
