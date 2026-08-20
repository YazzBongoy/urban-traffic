# Urban Traffic Management System

Système intelligent de gestion du trafic urbain utilisant des caméras 360° et la reconnaissance automatique de plaques d'immatriculation (RNI).

## Qu'est-ce que cette application ?

Cette application est une **plateforme complète de gestion du trafic urbain** qui résout les problèmes de congestion routière dans les villes. Elle combine plusieurs technologies pour offrir une solution intelligente et temps réel.

## Ce que fait l'application

### 1. Surveillance Vidéo en Temps Réel
- **Collecte automatique** des flux vidéo depuis des caméras 360° positionnées aux intersections stratégiques
- **Détection et comptage** des véhicules (voitures, motos, bus, camions) en temps réel
- **Vision nocturne** grâce aux capteurs infrarouges des caméras
- **Stockage sécurisé** des images et vidéos dans un système objet (MinIO/S3)

### 2. Reconnaissance Automatique de Plaques (RNI)
- **Lecture automatique** des plaques d'immatriculation des véhicules en circulation
- **Identification précise** avec un taux de précision supérieur à 95%
- **Historique complet** des déplacements de chaque véhicule
- **Recherche instantanée** par numéro de plaque pour les forces de l'ordre

### 3. Analyse Intelligente du Trafic
- **Cartographie interactive** du trafic en temps réel sur une interface web
- **Heatmaps** montrant les zones de congestion
- **Statistiques détaillées** : nombre de véhicules, vitesse moyenne, taux de congestion
- **Prédictions** basées sur le Machine Learning (modèle LSTM)

### 4. Détection et Gestion des Incidents
- **Alertes automatiques** en cas d'accident ou d'embouteillage
- **Signalement** par les utilisateurs via l'application mobile
- **Escalade** vers les services d'urgence
- **Suivi en temps réel** de la résolution des incidents

### 5. Optimisation de la Signalisation
- **Contrôle intelligent** des feux de signalisation basé sur les données réelles
- **Réduction automatique** du temps d'attente aux carrefours
- **Adaptation** aux conditions de trafic en temps réel

## Bénéfices Concrets

| Problème | Solution | Résultat |
|----------|----------|----------|
| Embouteillages chroniques | Analyse temps réel + optimisation feux | Réduction de 30% du temps de trajet |
| Accident non signalé | Détection automatique + alerte | Intervention en < 5 minutes |
| Véhicule volé en circulation | Recherche par plaque | Identification instantanée |
| Pollution excessive | Réduction des temps d'attente | Diminution des émissions CO2 |
| Manque de données | Collecte automatique | Décisions basées sur les faits |

## Architecture Technique

```
┌─────────────────────────────────────────────────────────────────┐
│                    UTILISATEURS                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Dashboard   │  │  App Mobile  │  │  Forces de   │          │
│  │  Web         │  │  iOS/Android │  │  l'ordre     │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API GATEWAY (Nginx)                           │
│              Rate Limiting / SSL / Load Balancing                │
└──────────────────────────┬──────────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Backend     │  │  Analytics   │  │  Alerts      │
│  FastAPI     │  │  Service     │  │  Service     │
│  (Python)    │  │  (ML/DL)     │  │  (Email/SMS) │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BASE DE DONNÉES                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  PostgreSQL  │  │  TimescaleDB │  │  Redis       │          │
│  │  (Données)   │  │  (Séries     │  │  (Cache +    │          │
│  │              │  │   temporelles)│  │   Temps réel)│          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    IoT / EDGE                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Caméras     │  │  Capteurs    │  │  Edge        │          │
│  │  360° (RTSP) │  │  Route       │  │  Computing   │          │
│  │              │  │  (IoT)       │  │  (NVIDIA)    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

## Fonctionnalités Principales

### Tableau de Bord Web
- Carte interactive avec positions des caméras et niveaux de trafic
- Graphiques en temps réel (véhicules/heure, vitesse moyenne, congestion)
- Historique et tendances sur 7/30/90 jours
- Export de rapports PDF
- Gestion des utilisateurs et des droits d'accès

### Application Mobile
- Visualisation du trafic en temps réel
- Alertes personnalisées (zone domicile/travail)
- Navigation avec conditions trafic intégrées
- Signalement d'incidents avec photo et géolocalisation

### Interface Administration
- Gestion des caméras (ajout, configuration, maintenance)
- Configuration des zones géographiques
- Gestion des alertes et notifications
- Monitoring système et logs

## Stack Technique

| Composant | Technologie | Justification |
|-----------|-------------|---------------|
| Backend API | FastAPI (Python) | Performance, asynchrone, auto-documentation |
| Frontend Web | React + TypeScript | Composants réutilifiés, typage fort |
| Base de données | PostgreSQL + TimescaleDB | Données relationnelles + séries temporelles |
| Cache | Redis | Temps réel, pub/sub, sessions |
| Vidéo | OpenCV + YOLOv8 | Détection objets en temps réel |
| OCR | Tesseract + DeepSort | Reconnaissance de plaques |
| ML | TensorFlow/Keras (LSTM) | Prédiction trafic |
| Mobile | React Native | Code partagé iOS/Android |
| IoT | MQTT + Edge Computing | Communication légère, traitement local |
| Conteneurs | Docker + Kubernetes | Déploiement scalable |
| CI/CD | GitHub Actions | Intégration continue automatisée |

## Prérequis

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

## Installation et Démarrage

```bash
# Cloner le repository
git clone https://github.com/YazzBongoy/urban-traffic.git
cd urban-traffic

# Configurer l'environnement
cp .env.example .env
# Éditer .env avec vos paramètres

# Démarrer tous les services
docker-compose up -d

# Initialiser la base de données
docker-compose exec backend alembic upgrade head

# Accéder aux interfaces
# Dashboard: http://localhost:3000
# API Docs: http://localhost:8000/docs
# MinIO: http://localhost:9001
```

## Démarrage Rapide (sans Docker)

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Structure de l'Application

```
urban-traffic/
├── backend/                 # API REST FastAPI
│   ├── app/
│   │   ├── api/v1/          # Routes API (auth, cameras, vehicles, traffic)
│   │   ├── core/            # Configuration, sécurité, base de données
│   │   ├── models/          # Modèles SQLAlchemy (User, Camera, Vehicle, etc.)
│   │   ├── schemas/         # Schémas Pydantic pour validation
│   │   └── services/        # Logique métier
│   └── alembic/             # Migrations de base de données
├── frontend/                # Application web React
│   └── src/
│       ├── components/      # Composants UI réutilisables
│       ├── pages/           # Pages (Dashboard, Cameras, Vehicles, etc.)
│       ├── hooks/           # Hooks React personnalisés
│       └── services/        # Appels API
├── iot/                     # Composants Edge/IoT
│   ├── video_processor/     # Traitement vidéo (OpenCV + YOLOv8)
│   ├── ocr_service/         # Service reconnaissance de plaques
│   └── edge_agent/          # Agent pour NVIDIA Jetson
├── ml/                      # Modèles Machine Learning
│   └── traffic_predictor.py # Prédiction trafic (LSTM)
├── docs/                    # Documentation détaillée
├── scripts/                 # Scripts de déploiement
└── .github/workflows/       # CI/CD automatisé
```

## API Principale

### Authentification
```bash
POST /api/v1/auth/login    # Connexion, retourne un token JWT
GET  /api/v1/auth/me       # Informations utilisateur connecté
```

### Caméras
```bash
GET    /api/v1/cameras/           # Liste toutes les caméras
POST   /api/v1/cameras/           # Ajouter une caméra
GET    /api/v1/cameras/{id}       # Détails d'une caméra
GET    /api/v1/cameras/{id}/status # Statut en temps réel
```

### Véhicules
```bash
GET    /api/v1/vehicles/              # Liste des véhicules
GET    /api/v1/vehicles/search/{plate} # Recherche par plaque
GET    /api/v1/vehicles/{id}/history   # Historique des passages
```

### Trafic
```bash
GET    /api/v1/traffic/realtime   # Données trafic en temps réel
GET    /api/v1/traffic/history    # Historique (avec filtres date/zone)
GET    /api/v1/traffic/zones      # Liste des zones surveillées
GET    /api/v1/traffic/heatmap    # Données pour carte de chaleur
```

### Analytics
```bash
GET    /api/v1/analytics/statistics   # Statistiques globales
GET    /api/v1/analytics/predictions  # Prédictions trafic
GET    /api/v1/analytics/reports      # Génération de rapports
```

## Tests

```bash
# Tests backend (pytest)
cd backend && pytest

# Tests frontend (Jest)
cd frontend && npm test

# Tests de charge (Locust)
locust -f tests/load/locustfile.py
```

## Monitoring et Observabilité

- **Métriques** : Prometheus + Grafana
- **Logs** : ELK Stack (Elasticsearch, Logstash, Kibana)
- **Traces** : Jaeger
- **Santé** : Endpoint `/health` pour vérification

## Sécurité

- Authentification JWT avec refresh tokens
- Chiffrement TLS 1.3 pour toutes les communications
- Contrôle d'accès basé sur les rôles (RBAC)
- Validation stricte des entrées (Pydantic)
- Protection contre les injections SQL (SQLAlchemy ORM)
- Rate limiting pour éviter les abus
- Audit logging de toutes les actions

## Équipe et Support

- **Développeur** : AS CAT SARL - Kinshasa, RDC
- **Email** : contact@ascatsarl.com
- **GitHub** : https://github.com/YazzBongoy/urban-traffic

## Licence

Proprietary - Tous droits réservés
