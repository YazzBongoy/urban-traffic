export type UserRole = 'admin' | 'operator' | 'viewer'

export interface User {
  id: number
  username: string
  email: string
  role: UserRole
  is_active: boolean
  created_at: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
}

export type CameraStatus = 'online' | 'offline' | 'maintenance'

export interface Camera {
  id: number
  name: string
  location: string
  latitude: number
  longitude: number
  rtsp_url: string
  is_360: boolean
  status: CameraStatus
  created_at: string
  updated_at: string
}

export interface TrafficZone {
  id: number
  name: string
  description: string | null
  polygon: string | null
  congestion_level: number
  vehicle_count: number
  average_speed: number
  updated_at: string
}

export interface RealtimeTraffic {
  zones: TrafficZone[]
  total_vehicles: number
  average_congestion: number
  timestamp: string
}

export interface Vehicle {
  id: number
  plate_number: string
  vehicle_type: string | null
  color: string | null
  owner_name: string | null
  owner_phone: string | null
  is_stolen: boolean
  created_at: string
  updated_at: string
}

export interface PlateReading {
  id: number
  plate_number: string
  confidence: number
  direction: string | null
  speed: number | null
  vehicle_id: number | null
  camera_id: number
  image_url: string | null
  timestamp: string
}

export interface Statistics {
  period: string
  total_vehicles: number
  average_speed: number
  average_congestion: number
}
