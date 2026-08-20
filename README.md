# Urban Traffic Management System

Système intelligent de gestion du trafic urbain utilisant des caméras 360° et la reconnaissance automatique de plaques d'immatriculation (RNI).

## 🎯 Objectifs

- **Collecte temps réel** des données trafic via caméras 360°
- **Reconnaissance automatique** des plaques d'immatriculation
- **Analyse intelligente** des flux de circulation
- **Optimisation** de la signalisation et du trafic
- **Réduction** de la congestion et de la pollution

## 🏗️ Architecture

Voir [ARCHITECTURE.md](./ARCHITECTURE.md) pour les détails techniques.

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Caméras    │────▶│   Edge      │────▶│  Backend    │
│  360°       │     │  Computing  │     │  (FastAPI)  │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                    ┌─────────────┐     ┌──────▼──────┐
                    │  Dashboard  │◀────│  Database   │
                    │  (React)    │     │  (PG + TS)  │
                    └─────────────┘     └─────────────┘
```

## 📁 Structure du Projet

```
urban-traffic/
├── backend/           # API FastAPI
│   ├── app/
│   │   ├── api/       # Routes API
│   │   ├── core/      # Config, security
│   │   ├── models/    # SQLAlchemy models
│   │   ├── schemas/   # Pydantic schemas
│   │   ├── services/  # Business logic
│   │   └── utils/     # Helpers
│   ├── tests/
│   ├── alembic/       # Migrations
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/          # Dashboard React
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── utils/
│   ├── Dockerfile
│   └── package.json
├── mobile/            # App React Native
│   ├── src/
│   └── app.json
├── iot/               # Edge Computing
│   ├── video_processor/
│   ├── ocr_service/
│   └── edge_agent/
├── ml/                # Machine Learning
│   ├── models/
│   ├── training/
│   └── inference/
├── infra/             # Infrastructure
│   ├── terraform/
│   ├── kubernetes/
│   └── docker/
├── docs/              # Documentation
├── scripts/           # Scripts utilitaires
└── .github/           # CI/CD
    └── workflows/
```

## 🚀 Démarrage Rapide

### Prérequis
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+

### Installation

```bash
# Cloner le repository
git clone https://github.com/YazzBongoy/urban-traffic.git
cd urban-traffic

# Copier la configuration
cp .env.example .env

# Démarrer les services
docker-compose up -d

# Initialiser la base de données
cd backend && alembic upgrade head

# Lancer le backend
uvicorn app.main:app --reload

# Lancer le frontend
cd frontend && npm install && npm run dev
```

### Variables d'Environnement

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/urban_traffic
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256

# Cameras
RTSP_STREAM_URL=rtsp://admin:pass@camera-ip:554/stream

# Storage
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
```

## 📊 Fonctionnalités

### Phase 1 (MVP)
- [ ] Authentification et autorisation
- [ ] Gestion des caméras
- [ ] Flux vidéo en temps réel
- [ ] Détection basique de véhicules
- [ ] Dashboard de monitoring

### Phase 2
- [ ] OCR plaques d'immatriculation
- [ ] Historique véhicules
- [ ] Heatmaps trafic
- [ ] Alertes automatiques
- [ ] Rapports statistiques

### Phase 3
- [ ] Prédiction trafic (ML)
- [ ] Optimisation feux
- [ ] Application mobile
- [ ] Intégration capteurs
- [ ] API publique

## 🧪 Tests

```bash
# Backend tests
cd backend && pytest

# Frontend tests
cd frontend && npm test

# Load testing
locust -f tests/load/locustfile.py
```

## 📈 Monitoring

- **Metrics**: Prometheus + Grafana
- **Logs**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Traces**: Jaeger
- **Uptime**: UptimeRobot / Healthchecks.io

## 🔒 Sécurité

- JWT avec refresh tokens
- HTTPS obligatoire
- Rate limiting
- Input validation (Pydantic)
- SQL injection protection (SQLAlchemy)
- XSS protection
- CORS configuré
- Audit logging

## 📄 License

Proprietary - AS CAT SARL

## 👥 Équipe

AS CAT SARL - Kinshasa, RDC

## 📞 Contact

- Email: contact@ascatsarl.com
- GitHub: https://github.com/YazzBongoy/urban-traffic
