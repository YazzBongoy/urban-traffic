# Architecture Technique v2 — Urban Traffic Management System

| | |
|---|---|
| **Version** | 2.0 |
| **Date** | 2026-08-21 |
| **Statut** | Cible validée — migration à planifier |
| **Auteur** | AS CAT SARL — Kinshasa, RDC |
| **Remplace** | Architecture v1 (`git history`) |

---

## 1. Bilan de la revue de l'architecture v1

La revue du code réel (pas seulement des documents) révèle des écarts majeurs entre l'architecture documentée et l'implémentation.

### 1.1 Constats bloquants (P0)

| # | Constat | Preuve | Impact |
|---|---------|--------|--------|
| B1 | **Le backend ne démarre pas** : `main.py` importe `api_router` depuis `app.api.v1`, mais il est défini dans `app/api/__init__.py`. `app/api/v1/__init__.py` contient un doublon mort des routes auth. | `backend/app/main.py:5`, `app/api/v1/__init__.py:8-31` | `ImportError` au démarrage uvicorn — aucun endpoint servi |
| B2 | **Aucun endpoint protégé** sauf `/auth/me`. Création de caméras et consultation de données RNI (véhicules volés) accessibles sans JWT. Aucun contrôle de rôle malgré `UserRole`. | `endpoints/cameras.py:18-24`, `vehicles.py:12-28` | Exposition totale des données de surveillance |
| B3 | **Pipeline OCR impossible** : le service OCR souscrit aux détections (bboxes JSON uniquement) et fabrique une image blanche factice au lieu d'un crop réel. Le champ `confidence` attendu n'est même pas publié par le video_processor. | `iot/ocr_service/main.py:84-94`, `video_processor/main.py:98-104` | La RNI — fonctionnalité cœur — ne peut jamais fonctionner |
| B4 | **Pas de broker MQTT dans docker-compose** alors que les 3 services iot publient/souscrivent en MQTT sur `localhost:1883`. Incohérence doc (« Redis Streams / Kafka ») vs code (paho-mqtt). | `docker-compose.yml:3-68`, `iot/*/main.py` | Pipeline iot non exécutable dans la stack |
| B5 | **Mismatch temps réel** : frontend prévu avec `socket.io-client` mais backend n'expose aucun WebSocket (0 occurrence dans le code Python). De plus `frontend/src/` n'existe pas. | `package.json:19`, grep backend | Contrat temps purement aspirationnel |
| B6 | **CI en échec permanent** : `npm ci` sans lockfile, build/lint/test frontend sans sources, pytest sur `backend/tests/` vide (exit 5). La CI n'a jamais pu passer. | `.github/workflows/ci.yml:62-94` | Zéro protection réelle |

### 1.2 Constats majeurs (P1)

| # | Constat | Preuve | Impact |
|---|---------|--------|--------|
| M1 | **TimescaleDB inutilisé** : aucune `create_hypertable`, extension jamais activée ; tables plain PostgreSQL. Index manquants sur `plate_readings(plate_number, timestamp, vehicle_id, camera_id)` et `traffic_metrics(zone_id, timestamp)`. | `alembic/versions/001_initial.py` | Full-scan sur séries temporelles, dégradation linéaire |
| M2 | **Sécurité faible** : fallback `SECRET_KEY` codé en dur (+ hardcodé dans compose), JWT HS256 symétrique, CORS `allow_methods=["*"]` + credentials, MinIO `minioadmin/minioadmin`, aucun rate limiting, identifiants RTSP en clair. | `core/config.py:11`, `docker-compose.yml:11,62-63` | Surface d'attaque large |
| M3 | **Duplication edge/cloud** : `edge_agent` ≈ 60-70 % copié de `video_processor` (MQTT, YOLO, boucle principale), avec divergence de topic (`traffic/edge/{id}/detections` vs souscription OCR `traffic/detections/#` → messages perdus). Pas de reconnect RTSP côté video_processor, pas de shutdown gracieux nulle part, QoS 0. | `edge_agent/main.py:32-107` vs `video_processor/main.py:27-85` | Dérive logicielle, perte de messages, zombies de processus |
| M4 | **ML non industrialisable** : fuite de données (scaler fit avant split), entraîné sur données synthétiques sinusoïdales, pas de registry/versioning/réentraînement/drift. | `ml/traffic_predictor.py:53 vs 147-149` | Prédictions non fiables, non reproductibles |
| M5 | **Observabilité absente** : Prometheus/Grafana/ELK/Jaeger revendiqués dans README mais aucun `/metrics`, logs non structurés, health check superficiel (ne vérifie ni DB ni Redis). | `main.py:26-28` | Exploitation impossible |
| M6 | **Qualité API** : pagination absente (caméras, historique trafic), recherche plaque en `ILIKE '%…%'` non bornée, `period` ignoré (branches if/else identiques), bcrypt synchrone dans routes async (~100 ms bloqué/connexion), validation d'entrée lacunaire (lat/long non bornées, emails non validés, wildcards SQL). | `services/analytics.py:14-29`, `services/auth.py:27` | Perf, cohérence, robustesse |
| M7 | **Docs divergentes** : DEPLOYMENT.md décrit `infra/terraform` et manifests Helm inexistants ; API.md affirme que tout est protégé par JWT (faux) et documente un login JSON alors que l'implémentation prend de l'OAuth2 form. | `docs/*` | Perte de confiance dans la documentation |

---

## 2. Journal des décisions d'architecture (ADR)

| ADR | Décision | Justification | Alternatives écartées |
|-----|----------|---------------|----------------------|
| ADR-01 | **Broker MQTT : Mosquitto (dev/edge), EMQX (prod)** | Léger pour Jetson, ACL + mTLS supportés, clustering EMQX en prod | Kafka (trop lourd pour l'edge, overhead ops) ; Redis Streams conservé en complément pour fan-out interne |
| ADR-02 | **Temps réel navigateur : WebSocket natif FastAPI + Redis pub/sub**, abandon de socket.io | Protocole standard, un seul serveur, fan-out multi-instances via Redis | socket.io (protocole propriétaire, aucun serveur côté Python) |
| ADR-03 | **Transport d'images : références MinIO + notification MQTT** (pas de frames dans les topics) | Les topics transportent des métadonnées légères ; crops plaques poussés vers MinIO avec TTL 24 h | Frames base64 dans MQTT (sature le broker) ; mémoire partagée (impossible multi-hôte) |
| ADR-04 | **Une seule instance TimescaleDB** (pas de PostgreSQL séparé) | TimescaleDB est PostgreSQL ; simplifie ops, sauvegardes, licences | Deux clusters (coût double, sync complexe) |
| ADR-05 | **JWT asymétrique RS256** + refresh rotation | Les workers iot vérifient les tokens sans partager le secret de signature | HS256 (secret partagé = surface de compromission) |
| ADR-06 | **Observabilité : OpenTelemetry** (traces + métriques) → Prometheus/Grafana/Jaeger | Standard vendor-neutral, un seul SDK | Stacks propriétaires |
| ADR-07 | **Codebase vision unique** avec profils de déploiement (`cloud` / `edge`) | Élimine la duplication M3, un seul chemin d'évolution | Deux codebases (dérive garantie) |
| ADR-08 | **MLOps : MLflow** pour registry + tracking, réentraînement hebdomadaire programmé | Open source, suffisant au stade actuel | SageMaker/Vertex (coût, lock-in) |
| ADR-09 | **OCR plaques : remplacer Tesseract seul** par pipeline dédié ALPR (détection plaque YOLOv8 + reconnaissance LPRNet/PaddleOCR) | Tesseract seul n'atteint pas 95 % sur plaques en mouvement ; objectif réaliste avec pipeline dédié | Tesseract + pré-traitements (plafond ~80 % en conditions réelles) |

---

## 3. Vue d'ensemble cible

```
┌────────────────────────────────────────────────────────────────────────────┐
│                            UTILISATEURS                                    │
│     Dashboard Web (React+Vite)      App Mobile (React Native)              │
└───────────────┬────────────────────────────┬───────────────────────────────┘
                │ HTTPS/WSS                  │ HTTPS
┌───────────────▼────────────────────────────▼───────────────────────────────┐
│                     API GATEWAY (Traefik/Nginx)                            │
│         TLS 1.3 · rate limiting · headers sécurité · WSS upgrade           │
└───────────────┬────────────────────────────────────────────────────────────┘
                │
┌───────────────▼───────────────────────────┐   ┌──────────────────────────┐
│            BACKEND FastAPI                │   │      OBSERVABILITÉ       │
│  REST /api/v1 · WS natif /ws              │   │  OpenTelemetry Collector │
│  JWT RS256 · RBAC · slowapi               │◄──┤  Prometheus · Grafana    │
│  /metrics · traces OTel                   │   │  Jaeger · Loki           │
└──────┬──────────────┬─────────────────────┘   └──────────────────────────┘
       │ SQL          │ Redis (cache, pub/sub WS, leases caméra→worker)
┌──────▼──────────────▼──────────────────────────────────────────────────────┐
│                          DONNÉES                                           │
│  TimescaleDB (hypertables traffic_metrics, plate_readings ;                │
│    agrégats continus 5min/1h ; retention 2 ans)                            │
│  MinIO/S3 (crops plaques TTL 24h, snapshots incidents)                     │
└──────▲─────────────────────────────────────────────────────────────────────┘
       │ SQL (écriture batch)          ┌────────────────────────────┐
┌──────┴──────────────────────┐        │      BROKER MQTT           │
│     SERVICES TRAITEMENT     │        │  Mosquitto (dev/edge)      │
│  ingestion-service (MQTT→TS)│◄──────►│  EMQX cluster (prod)       │
│  ocr-service (ALPR dédié)   │  QoS 1 │  mTLS + ACL par topic      │
│  alert-engine (règles)      │        └──────────▲─────────────────┘
└─────────────────────────────┘                   │ MQTT TLS
                                       ┌──────────┴─────────────────┐
                                       │      EDGE / IoT            │
                                       │  vision-worker (profil     │
                                       │  cloud, GPU/CPU pool K8s)  │
                                       │  vision-agent (profil edge,│
                                       │  Jetson TensorRT INT8,     │
                                       │  store-and-forward)        │
                                       │  Caméras 360° RTSP/ONVIF   │
                                       └────────────────────────────┘
```

---

## 4. Flux de données temps réel cible

1. **Capture** — la caméra diffuse en RTSP ; le worker vision (cloud ou edge) ouvre le flux avec reconnexion à backoff exponentiel (1 s → 60 s max, jitter).
2. **Détection** — YOLOv8 (export TensorRT INT8 sur Jetson) détecte véhicules (classes 2,3,5,7) ; DeepSORT assure le tracking.
3. **Crop & stockage** — pour chaque track confirmé, le worker découpe la zone plaque probable et pousse le crop vers MinIO (`s3://plates/{camera_id}/{track_id}/{timestamp}.jpg`, TTL 24 h).
4. **Publication détection** — topic `traffic/v1/detections/{camera_id}`, QoS 1, payload validé par schéma :

```json
{
  "schema": "detection.v1",
  "camera_id": 12,
  "track_id": 4821,
  "vehicle_class": "car",
  "bbox_ltrb": [512, 380, 640, 520],
  "confidence": 0.91,
  "plate_crop_uri": "s3://plates/12/4821/2026-08-21T09-14-03Z.jpg",
  "occurred_at": "2026-08-21T09:14:03.412Z",
  "worker_id": "vision-cloud-7"
}
```

5. **Reconnaissance plaque** — ocr-service consomme `traffic/v1/detections/#`, télécharge le crop depuis MinIO, exécute le pipeline ALPR (détection plaque → redressement → LPRNet), publie `traffic/v1/plates/{camera_id}` QoS 1 :

```json
{
  "schema": "plate.v1",
  "camera_id": 12,
  "track_id": 4821,
  "plate_raw": "AB-123-CD",
  "plate_normalized": "AB123CD",
  "confidence": 0.96,
  "country": "COD",
  "crop_uri": "s3://plates/12/4821/2026-08-21T09-14-03Z.jpg",
  "occurred_at": "2026-08-21T09:14:04.105Z"
}
```

6. **Ingestion** — ingestion-service écrit en batch (buffer 500 events ou 2 s) dans TimescaleDB : `plate_readings` et `traffic_metrics` (hypertables).
7. **Règles & alertes** — alert-engine évalue les règles (vitesse, file d'attente, véhicule recherché) et déclenche notifications (email/SMS/push).
8. **Diffusion dashboard** — ingestion-service publie aussi sur Redis pub/sub canal `realtime:{zone_id}` ; chaque instance FastAPI abonnée pousse aux clients WebSocket `/ws?zones=...`.
9. **Analytics** — agrégats continus TimescaleDB (5 min, 1 h) alimentent statistiques et features du modèle LSTM ; prédictions exposées via `/api/v1/analytics/predictions`.

Horodatage : toujours ISO 8601 UTC timezone-aware (`datetime.now(timezone.utc)`). Horloge edge synchronisée par NTP/chrony — sinon rejet du message (horodatage côté broker).

---

## 5. Composants

### 5.1 API Gateway (Traefik)
TLS 1.3 termination, rate limiting IP, security headers (HSTS, X-Content-Type-Options), routage WSS, health checks upstream. Certificats via Let's Encrypt/acme.

### 5.2 Backend FastAPI
- Correction immédiate du wiring routeur (B1) : un seul `api_router` dans `app/api/v1/__init__.py`, suppression du doublon.
- Dépendance d'auth obligatoire par défaut (`dependencies=[Depends(get_current_user)]` au niveau router), endpoints publics explicitement marqués. Matrice RBAC : `admin` > `operator` > `viewer`.
- Rate limiting slowapi (login : 5/min/IP ; API : 100/min/utilisateur).
- Health check approfondi `/health/live` (process) et `/health/ready` (ping DB + Redis, timeout 2 s).
- bcrypt via `run_in_executor` ou remplacement par Argon2id async-friendly.
- Pagination stricte (limit ≤ 200), validation Pydantic bornée (lat/long, plages de dates, échappement wildcards ILIKE), `response_model` systématique.
- JWT RS256 : clé privée backend uniquement, clé publique distribuée aux services ; rotation refresh tokens ; révocation via Redis denylist.

### 5.3 Pipeline Vision (codebase unique, deux profils)
Un paquet `vision/` avec profil `cloud` (worker GPU pool K8s, N caméras/worker selon lease Redis) et profil `edge` (Jetson, 1-2 caméras, TensorRT INT8, store-and-forward local si coupure réseau — buffer disque circulaire rejoué à la reconnexion).
Exigences communes : gestion SIGTERM/SIGINT (release capture, déconnexion MQTT, flush), reconnexion RTSP backoff exponentiel, pacing par horodatage frame (jamais `time.sleep` fixe après lecture bloquante), drop de frames si retard (toujours traiter la frame la plus récente), MQTT QoS 1 + `reconnect_delay_set` + LWT (`status/vision/{worker_id}` retained).

### 5.4 Service OCR / ALPR
Pipeline dédié : détection plaque (YOLOv8-plate) → redressement perspective → reconnaissance LPRNet/PaddleOCR → normalisation regex formats RDC/CEMAC. Précision cible réaliste : ≥ 95 % sur crops nets jour, ≥ 85 % nuit IR. Tesseract abandonné comme composant principal (conservable en fallback offline).

### 5.5 Analytics / ML
- Correction fuite : fit du scaler sur train uniquement, pipeline sklearn sérialisé avec le modèle.
- Données réelles issues des agrégats continus (jamais de synthétique en production).
- MLflow : tracking des runs, registry de modèles (staging → production), versioning datasets.
- Réentraînement hebdomadaire automatique ; promotion conditionnée à MAE < seuil sur backtest.
- Monitoring drift : PSI/KS hebdomadaire sur distribution des features ; alarme si PSI > 0.2.
- Export ONNX pour infération low-latency dans ingestion-service.

### 5.6 Couche données
- **TimescaleDB (instance unique)** :
  - Hypertables : `traffic_metrics` (chunk 1 jour), `plate_readings` (chunk 1 semaine).
  - Agrégats continus : `traffic_metrics_5min`, `traffic_metrics_1h` (vehicle_count, avg_speed, congestion_level).
  - Retention : `traffic_metrics` brut 90 jours (les agrégats conservent 2 ans) ; `plate_readings` 90 jours (RGPD, voir §6) puis anonymisation (plate_hash tronqué) et conservation agrégée 2 ans.
  - Index : `(plate_number, timestamp DESC)`, `(camera_id, timestamp DESC)`, `(zone_id, timestamp DESC)` ; extension pg_trgm + index GIN pour recherche floue plaques.
- **MinIO** : buckets `plates` (TTL 24 h), `incidents` (durée légale), versioning désactivé, chiffrement SSE-S3.
- **Redis** : cache lecture, pub/sub realtime, leases caméra→worker (TTL 30 s renouvelé), denylist JWT, rate limiting distribué.

### 5.7 Temps réel frontend
WebSocket natif `/ws` (auth par token en query param ou premier message), souscription par zones. Fan-out multi-instances via Redis pub/sub. Reconnexion côté client avec backoff + resync via `/traffic/realtime`.

---

## 6. Sécurité

| Domaine | Mesure |
|---------|--------|
| Secrets | Fail-fast au démarrage si `SECRET_KEY` non défini ou égal au défaut en prod. Docker secrets / Vault ; interdiction des secrets dans compose/git (scan gitleaks en CI). |
| Authentification | JWT RS256, access 15 min / refresh 7 j avec rotation, denylist Redis. OAuth2 password flow conservé pour le CLI, login JSON pour SPA. |
| Autorisation | RBAC systématique (voir matrice §5.2) ; données RNI restreintes au rôle `operator+` ; journalisation d'accès aux lectures de plaques (qui, quand, quelle plaque). |
| MQTT | mTLS obligatoire, ACL par topic (worker X ne publie que `traffic/v1/detections/{ses caméras}`), authentification par certificat client par worker. |
| Réseau | TLS partout (RTSP over TLS si supporté, sinon réseau caméras isolé VLAN), MinIO non exposé hors cluster, ports DB/Redis non publiés en prod. |
| RGPD / ANPR | Base légale documentée ; minimisation (crop plaque uniquement, pas de visages) ; rétention 90 j puis anonymisation irréversible ; droit d'accès/suppression outillé ; DPIA requise avant mise en service ; affichage légal sur voie publique. |
| Application | Validation stricte Pydantic, ORM exclusivement (anti-injection), CORS origins explicites sans wildcard+credentials, security headers au gateway. |

---

## 7. Observabilité

- **Traces** : OpenTelemetry SDK (FastAPI auto-instrumentation, httpx, SQLAlchemy) → Collector → Jaeger. `correlation_id` propagé HTTP → MQTT (header user-properties) → logs.
- **Métriques applicatives** (Prometheus `/metrics`) : `vision_frames_processed_total{camera}`, `vision_fps{camera}`, `detections_total{class}`, `ocr_reads_total{result=ok|low_conf|error}`, `plate_read_latency_seconds`, `mqtt_messages_dropped_total`, `ws_active_connections`, `ingest_batch_lag_seconds`.
- **Logs** : JSON structuré (structlog), niveaux par env, agrégés Loki.
- **Dashboards Grafana** : santé flotte caméras, débit détections, taux lecture plaques, latence bout-en-bout (P50/P95), saturation workers.
- **Alertes** (Alertmanager) : caméra sans frame > 2 min, worker down, lag ingestion > 30 s, taux OCR ok < 70 %/15 min, drift PSI > 0.2, certificat MQTT < 14 jours.

---

## 8. Scalabilité & haute disponibilité

| Axe | Stratégie |
|-----|-----------|
| Workers vision | Lease Redis par caméra (TTL 30 s) : un seul worker actif par flux, reprise automatique en cas de panne. Scaling = ajouter des workers, réassignation < 60 s. |
| Backend API | Stateless, HPA CPU/RPS ; sessions en Redis ; WS fan-out via pub/sub (pas d'affinité nécessaire). |
| Broker | Dev : Mosquitto single. Prod : EMQX 2+ nœuds, LB TCP 8883. |
| Ingestion | Consommateurs MQTT groupés (shared subscriptions `$share/ingest/...`), écriture batch idempotente (upsert par natural key camera+track+ts). |
| TimescaleDB | Réplica streaming pour lectures analytics ; sauvegardes pgBackRest quotidiennes + WAL continu, PITR 7 j. |
| MinIO | Mode erasure-coded 4 nœuds en prod. |
| Edge | Autonomie 24 h store-and-forward ; dégradation gracieuse (comptage sans OCR si lien saturé). |

Cibles conservées de v1 : latence détection < 100 ms, précision OCR > 95 % (jour), réponse API < 200 ms, uptime 99,9 %.

---

## 9. Topologies de déploiement

### 9.1 Développement (docker-compose enrichi)
Services : `traefik`, `backend`, `frontend`, `db` (timescaledb), `redis`, `minio`, `mosquitto`, `ingestion`, `ocr`, `vision-worker` (profile `samples` avec flux vidéo de test), `otel-collector`, `prometheus`, `grafana`. Healthchecks sur tous les services, `depends_on: condition: service_healthy`, suppression du champ obsolète `version`, secrets via `.env` git-ignoré, profils compose pour lancer le pipeline iot à la demande.

### 9.2 Edge (NVIDIA Jetson)
Container runtime NVIDIA ; image `vision-agent` multi-arch avec modèle TensorRT INT8 pré-compilé ; config locale YAML (caméra, broker, buffer) ; systemd unit avec restart=always ; télémétrie LWT ; mise à jour OTA par tag d'image (watchtower restreint).

### 9.3 Production Kubernetes
Namespaces `urban-traffic-{prod,staging}` ; Helm chart unique (valeurs par env) ; node pools séparés CPU/GPU ; HPA sur backend et workers vision (métrique custom files en attente) ; PodDisruptionBudgets ; NetworkPolicies (seul ingestion parle à DB, seuls workers parlent au broker) ; cert-manager pour TLS et certs MQTT ; backups testés mensuellement (restore drill).

---

## 10. Plan de migration v1 → v2

| Phase | Contenu | Effort | Livrable |
|-------|---------|--------|----------|
| **P0 — Stabiliser** (1-2 sem.) | Fix wiring routeur (B1) ; auth+RBAC sur tous les endpoints (B2) ; fail-fast SECRET_KEY ; CORS explicite ; healthchecks compose + depends_on conditions ; seed CI réparable (lockfile, 1 test smoke backend, min 1 test frontend) ; suppression champ `version` compose | S | Backend démarrable, CI verte, endpoints protégés |
| **P1 — Socle temps réel** (2-3 sem.) | Ajout mosquitto + ingestion-service ; schémas de messages v1 (JSON Schema validés) ; WebSocket natif + Redis pub/sub ; retrait socket.io-client ; tests d'intégration MQTT→DB | M | Pipeline détection→dashboard de bout en bout |
| **P2 — Vision & OCR** (3-4 sem.) | Fusion edge_agent/video_processor en `vision/` profils cloud/edge ; reconnect/shutdown/pacing/QoS1 ; crop MinIO + refs ; ALPR dédié remplace Tesseract ; index + hypertables + agrégats continus + retention | L | RNI fonctionnelle avec précision mesurée |
| **P3 — Observabilité & sécurité durcie** (2-3 sem.) | OTel + Prometheus + dashboards + alertes ; RS256 + rotation ; mTLS MQTT + ACL ; slowapi ; gitleaks/trivy en CI ; journalisation accès plaques | M | Exploitabilité prod + conformité RGPD outillée |
| **P4 — MLOps & K8s** (3-4 sem.) | MLflow registry + réentraînement hebdo + drift ; chart Helm ; HPA/GPU pool ; NetworkPolicies ; backup/restore drills ; DEPLOYMENT.md réécrit pour correspondre au réel | L | Plateforme production-ready scalable |

Règle : chaque phase est fusionnable indépendamment ; pas de phase Pn+1 tant que la CI n'est pas verte sur Pn.

---

## 11. Risques résiduels

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| Qualité optique/réseau des caméras sur site (Kinshasa) | Haute | Précision OCR sous objectifs | POC terrain 2 semaines avant déploiement massif ; seuils conf adaptés ; SLA opérateur télécom |
| Coupures électriques/internet fréquentes | Haute | Pertes de données | Store-and-forward edge, UPS caméras, buffers locaux |
| Cadre juridique ANPR RDC mouvant | Moyenne | Blocage mise en service | DPIA + revue juridique avant P3 ; mode « comptage anonyme » dégradable |
| Dérive modèle LSTM saisonnière | Moyenne | Prédictions erronées | Drift monitoring + fallback sur moyennes historiques |
| Capacité équipe ops K8s | Moyenne | Incidents prod | P4 tardif volontairement ; runbooks ; Grafana alerts simples d'abord |
