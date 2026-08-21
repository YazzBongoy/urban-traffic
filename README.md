# Urban Traffic Management System

![CI](https://github.com/YazzBongoy/urban-traffic/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![React](https://img.shields.io/badge/react-18-61dafb.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688.svg)
![Docker](https://img.shields.io/badge/docker-compose-2496ED.svg)
![License](https://img.shields.io/badge/license-proprietary-red.svg)

Système intelligent de gestion du trafic urbain utilisant des caméras 360° et la reconnaissance automatique de plaques d'immatriculation (RNI).

## Sommaire

- [Qu'est-ce que cette application ?](#quest-ce-que-cette-application-)
- [Ce que fait l'application](#ce-que-fait-lapplication)
- [Bénéfices concrets](#bénéfices-concrets)
- [Architecture technique](#architecture-technique)
- [Fonctionnalités principales](#fonctionnalités-principales)
- [Stack technique](#stack-technique)
- [État du projet & Roadmap](#état-du-projet--roadmap)
- [Prérequis](#prérequis)
- [Installation et démarrage](#installation-et-démarrage)
- [Commandes Make](#commandes-make)
- [Variables d'environnement](#variables-denvironnement)
- [Structure de l'application](#structure-de-lapplication)
- [API principale](#api-principale)
- [Tests](#tests)
- [Monitoring et observabilité](#monitoring-et-observabilité)
- [Sécurité](#sécurité)
- [Documentation](#documentation)
- [Contribuer](#contribuer)
- [Équipe et support](#équipe-et-support)

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
| Frontend Web | React + TypeScript | Composants réutilisables, typage fort |
| Base de données | PostgreSQL + TimescaleDB | Données relationnelles + séries temporelles |
| Cache | Redis | Temps réel, pub/sub, sessions |
| Vidéo | OpenCV + YOLOv8 | Détection objets en temps réel |
| OCR | Tesseract + DeepSort | Reconnaissance de plaques |
| ML | TensorFlow/Keras (LSTM) | Prédiction trafic |
| Mobile | React Native | Code partagé iOS/Android |
| IoT | MQTT + Edge Computing | Communication légère, traitement local |
| Conteneurs | Docker + Kubernetes | Déploiement scalable |
| CI/CD | GitHub Actions | Intégration continue automatisée |

## État du projet & Roadmap

Le projet suit un plan d'implémentation de 12 mois (détails dans [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)) :

| Phase | Période | Contenu | Statut |
|-------|---------|---------|--------|
| 1 — Fondations | Mois 1-2 | Infra Docker, CI/CD, backend core (JWT, CRUD), frontend React | ✅ Terminé |
| 2 — Core Features | Mois 3-5 | Vidéo RTSP + YOLOv8, OCR plaques, données trafic temps réel | 🚧 En cours |
| 3 — Analytics & Intelligence | Mois 6-8 | Dashboard analytics, ML (LSTM), alertes email/SMS/push | ⏳ Planifié |
| 4 — Optimisation | Mois 9-10 | Optimisation feux, itinéraires recommandés | ⏳ Planifié |
| 5 — Déploiement production | Mois 11-12 | Kubernetes, monitoring complet, mise en service | ⏳ Planifié |

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

## Commandes Make

Un `Makefile` est fourni pour simplifier le quotidien :

```bash
make help           # Afficher toutes les commandes disponibles
make setup          # Configuration initiale de l'environnement de dev
make start          # Démarrer tous les services (docker-compose up -d)
make stop           # Arrêter les services
make restart        # Redémarrer les services
make logs           # Suivre les logs en temps réel
make status         # État des services
make test           # Tous les tests (backend + frontend)
make test-backend   # Tests backend uniquement (pytest)
make test-frontend  # Tests frontend uniquement (vitest)
make lint           # Lint backend (ruff) + frontend (eslint)
make migrate        # Appliquer les migrations Alembic
make makemigration msg="description"  # Créer une nouvelle migration
make shell          # Shell dans le conteneur backend
make db-shell       # Shell PostgreSQL (psql)
make redis-shell    # Shell Redis (redis-cli)
make build          # Construire les images Docker
make clean          # Nettoyage complet (volumes + prune)
```

## Variables d'environnement

Copier `.env.example` vers `.env` puis adapter :

| Variable | Description | Exemple |
|----------|-------------|---------|
| `DATABASE_URL` | Connexion PostgreSQL/TimescaleDB | `postgresql+asyncpg://postgres:postgres@localhost:5432/urban_traffic` |
| `REDIS_URL` | Connexion Redis | `redis://localhost:6379` |
| `SECRET_KEY` | Clé secrète JWT (**à changer en production**) | `your-secret-key-change-in-production` |
| `JWT_ALGORITHM` | Algorithme de signature JWT | `HS256` |
| `VITE_API_URL` | URL de l'API pour le frontend | `http://localhost:8000` |
| `RTSP_STREAM_URL` | Flux RTSP des caméras 360° | `rtsp://admin:password@camera-ip:554/stream` |
| `MINIO_ENDPOINT` | Endpoint MinIO/S3 | `localhost:9000` |
| `MINIO_ACCESS_KEY` | Clé d'accès MinIO | `minioadmin` |
| `MINIO_SECRET_KEY` | Clé secrète MinIO | `minioadmin` |

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

## Documentation

Documentation détaillée dans le dépôt :

| Document | Contenu |
|----------|---------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Architecture technique complète (couches, flux de données, performance cible) |
| [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) | Plan d'implémentation sur 12 mois, phase par phase |
| [docs/API.md](docs/API.md) | Référence détaillée de l'API REST |
| [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) | Guide du développeur (conventions, workflow) |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Guide de déploiement (Docker, Kubernetes, production) |

## Contribuer

Ce projet est développé en interne par AS CAT SARL. Le workflow est le suivant :

1. Créer une branche depuis `develop` : `git checkout -b feature/ma-fonctionnalite`
2. Commiter avec des messages conventionnels (`feat:`, `fix:`, `docs:`, `test:`…)
3. Vérifier la qualité : `make lint && make test`
4. Ouvrir une Pull Request vers `develop` — la CI (GitHub Actions) doit passer
5. Après revue, merge vers `main` pour les releases

## Équipe et Support

- **Développeur** : AS CAT SARL - Kinshasa, RDC
- **Email** : contact@ascatsarl.com
- **GitHub** : https://github.com/YazzBongoy/urban-traffic

## Licence

Proprietary - Tous droits réservés
