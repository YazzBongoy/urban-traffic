# Architecture Technique - Urban Traffic Management System

## Vue d'ensemble

Système de gestion du trafic urbain basé sur des caméras 360° et la reconnaissance automatique de plaques d'immatriculation (RNI).

## Architecture Globale

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        COUCHE PRÉSENTATION                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │  Dashboard    │  │  Mobile App  │  │  API Portal  │                  │
│  │  (React)      │  │  (React      │  │  (Swagger)   │                  │
│  │              │  │   Native)    │  │              │                  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                  │
└─────────┼──────────────────┼──────────────────┼────────────────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     COUCHE API GATEWAY                                   │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    Nginx / Traefik                                │   │
│  │              Rate Limiting / SSL / Load Balancing                 │   │
│  └──────────────────────────┬───────────────────────────────────────┘   │
└─────────────────────────────┼───────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│   API Service    │ │  Analytics       │ │  Notification    │
│   (FastAPI)      │ │  Service         │ │  Service         │
│                  │ │  (Python)        │ │  (Python)        │
│  - Auth/JWT      │ │  - ML Models     │ │  - Email         │
│  - CRUD          │ │  - Statistics    │ │  - SMS           │
│  - WebSockets    │ │  - Predictions   │ │  - Push          │
└────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     COUCHE TRAITEMENT                                    │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                  Message Queue (Redis Streams / Kafka)           │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │  Video       │  │  OCR         │  │  Traffic      │                  │
│  │  Processor   │  │  Service     │  │  Optimizer    │                  │
│  │  (OpenCV)    │  │  (Tesseract) │  │  (ML)         │                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                  │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     COUCHE DONNÉES                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │  PostgreSQL  │  │  TimescaleDB │  │  Redis       │                  │
│  │  (Primary)   │  │  (Time       │  │  (Cache +    │                  │
│  │              │  │   Series)    │  │   Sessions)  │                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                  │
│  ┌──────────────┐  ┌──────────────┐                                    │
│  │  MinIO/S3    │  │  Elasticsearch│                                    │
│  │  (Images)    │  │  (Logs)      │                                    │
│  └──────────────┘  └──────────────┘                                    │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     COUCHE IoT / EDGE                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │  Caméras     │  │  Capteurs    │  │  Edge        │                  │
│  │  360°        │  │  Route       │  │  Computing   │                  │
│  │  (RTSP/ONVIF)│  │  (IoT)       │  │  (Jetson)    │                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                  │
└─────────────────────────────────────────────────────────────────────────┘
```

## Composants Détaillés

### 1. Frontend - Dashboard Web

**Technologies:**
- React 18+ avec TypeScript
- TailwindCSS pour le styling
- Recharts/D3.js pour les graphiques
- Leaflet/Mapbox pour la cartographie
- Socket.io pour les mises à jour en temps réel

**Fonctionnalités:**
- Cartographie interactive du trafic en temps réel
- Tableaux de bord avec métriques KPI
- Historique et analyse statistique
- Gestion des alertes et notifications
- Interface d'administration

### 2. Frontend - Application Mobile

**Technologies:**
- React Native avec TypeScript
- Expo pour le build
- React Navigation

**Fonctionnalités:**
- Visualisation trafic en temps réel
- Alertes personnalisées
- Navigation avec conditions trafic
- Reporting d'incidents

### 3. Backend API (FastAPI)

**Technologies:**
- Python 3.11+ avec FastAPI
- SQLAlchemy 2.0 + Alembic
- JWT pour l'authentification
- WebSocket pour le temps réel

**Endpoints Principaux:**
```
/api/v1/
├── auth/              # Authentication
│   ├── login
│   ├── register
│   └── refresh
├── cameras/           # Gestion caméras
│   ├── list
│   ├── create
│   ├── {id}/stream
│   └── {id}/status
├── vehicles/          # Véhicules détectés
│   ├── list
│   ├── {plate}/history
│   └── search
├── traffic/           # Données trafic
│   ├── realtime
│   ├── history
│   ├── zones
│   └── heatmap
├── analytics/         # Analyses
│   ├── statistics
│   ├── predictions
│   └── reports
├── incidents/         # Incidents
│   ├── list
│   ├── create
│   └── {id}/status
└── admin/             # Administration
    ├── users
    ├── zones
    └── settings
```

### 4. Services de Traitement

#### Video Processor
- Capture flux RTSP depuis caméras 360°
- Détection de véhicules (YOLOv8)
- Tracking multi-objets (DeepSORT)
- Détection d'événements (accidents, embouteillages)

#### OCR Service
- Extraction de plaques d'immatriculation
- Normalisation des caractères
- Validation et base de données de référence

#### Traffic Optimizer
- Prédiction du trafic (LSTM/Transformer)
- Optimisation des feux de signalisation
- Recommandations d'itinéraires

### 5. Base de Données

#### PostgreSQL (Données transactionnelles)
```sql
-- Tables principales
cameras          -- Informations caméras
vehicles         -- Véhicules enregistrés
plate_readings   -- Lectures de plaques
traffic_zones    -- Zones géographiques
incidents        -- Incidents signalés
signals          -- État des feux
users            -- Utilisateurs système
```

#### TimescaleDB (Données temporelles)
```sql
-- Hypertables pour séries temporelles
traffic_metrics      -- Métriques par minute/heure
vehicle_counts       -- Comptages véhicules
speed_averages       -- Vitesses moyennes
congestion_levels    -- Niveaux de congestion
```

#### Redis
- Cache des données en temps réel
- Sessions utilisateur
- File de messages (pub/sub)
- Rate limiting

### 6. Infrastructure IoT

#### Edge Computing (NVIDIA Jetson)
- Pré-traitement vidéo local
- Réduction de bande passante
- Détection temps réel
- Fallback en cas de coupure réseau

#### Caméras 360°
- Protocole: RTSP/ONVIF
- Résolution: 4K minimum
- IR pour vision nocturne
- Connectivité: PoE + 4G backup

## Flux de Données

```
Caméra 360° ──RTSP──▶ Edge (Jetson) ──MQTT──▶ Message Queue
                                                    │
                                                    ▼
                                            Video Processor
                                                    │
                                            ┌───────┴───────┐
                                            ▼               ▼
                                    Plate Readings    Traffic Data
                                            │               │
                                            ▼               ▼
                                    ┌───────────────────────────┐
                                    │     PostgreSQL +           │
                                    │     TimescaleDB            │
                                    └─────────────┬─────────────┘
                                                  │
                                    ┌─────────────┴─────────────┐
                                    ▼                           ▼
                            Analytics Service           Real-time API
                                    │                           │
                                    ▼                           ▼
                            Reports / ML             Dashboard / Mobile
```

## Déploiement

### Architecture Cloud (Production)
- Kubernetes (EKS/GKE/AKS)
- Docker containers
- Terraform pour IaC
- Prometheus + Grafana pour le monitoring

### Architecture Locale (Développement)
- Docker Compose
- Minikube pour K8s local
- Hot reload pour le dev

## Sécurité

- Authentification JWT avec refresh tokens
- Chiffrement TLS 1.3 pour toutes les communications
- RBAC (Role-Based Access Control)
- Audit logging
- Conformité RGPD pour les données personnelles
- Anonymisation des plaques selon réglementation

## Performance Cible

| Métrique | Objectif |
|----------|----------|
| Latence détection | < 100ms |
| Précision OCR | > 95% |
| Débit transactions | > 1000/s |
| Uptime | 99.9% |
| Rétention données | 2 ans |
| Temps réponse API | < 200ms |
