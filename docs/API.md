# API Documentation

## Authentication

All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

## Endpoints

### Auth

#### POST /api/v1/auth/login
Login and get access token.

**Request:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

### Cameras

#### GET /api/v1/cameras/
List all cameras.

**Response:**
```json
[
  {
    "id": 1,
    "name": "Camera 1",
    "location": "Intersection A",
    "latitude": -4.4419,
    "longitude": 15.2663,
    "rtsp_url": "rtsp://...",
    "status": "online",
    "is_360": true
  }
]
```

#### POST /api/v1/cameras/
Create a new camera.

#### GET /api/v1/cameras/{id}
Get camera by ID.

#### GET /api/v1/cameras/{id}/status
Get camera status.

### Vehicles

#### GET /api/v1/vehicles/
List all vehicles.

#### GET /api/v1/vehicles/search/{plate}
Search vehicles by plate number.

#### GET /api/v1/vehicles/{id}/history
Get vehicle detection history.

### Traffic

#### GET /api/v1/traffic/realtime
Get real-time traffic data.

#### GET /api/v1/traffic/history
Get historical traffic data.

#### GET /api/v1/traffic/zones
List traffic zones.

#### GET /api/v1/traffic/heatmap
Get traffic heatmap data.

### Analytics

#### GET /api/v1/analytics/statistics
Get traffic statistics.

#### GET /api/v1/analytics/predictions
Get traffic predictions.

#### GET /api/v1/analytics/reports
Generate traffic report.
