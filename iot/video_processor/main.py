#!/usr/bin/env python3
"""
Video Processor for Urban Traffic Management
Processes RTSP streams from 360° cameras and detects vehicles.
"""

import cv2
import numpy as np
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoProcessor:
    def __init__(self, config: Dict):
        self.config = config
        self.model = YOLO("yolov8n.pt")
        self.tracker = DeepSort(max_age=30)
        self.mqtt_client = mqtt.Client()
        
        # Connect to MQTT broker
        self.mqtt_client.connect(
            config.get("mqtt_host", "localhost"),
            config.get("mqtt_port", 1883),
            60
        )
        self.mqtt_client.loop_start()
        
    def process_stream(self, camera_id: int, rtsp_url: str):
        """Process a single RTSP stream."""
        cap = cv2.VideoCapture(rtsp_url)
        
        if not cap.isOpened():
            logger.error(f"Failed to open stream: {rtsp_url}")
            return
            
        logger.info(f"Processing stream from camera {camera_id}")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.warning(f"Failed to read frame from camera {camera_id}")
                time.sleep(1)
                continue
            
            # Detect vehicles
            detections = self.detect_vehicles(frame)
            
            # Track vehicles
            tracks = self.tracker.update_tracks(detections, frame=frame)
            
            # Publish results
            self.publish_detections(camera_id, tracks, frame)
            
            # Display (optional, for debugging)
            if self.config.get("display", False):
                self.display_frame(frame, tracks)
            
            time.sleep(1.0 / self.config.get("frame_rate", 5))
        
        cap.release()
    
    def detect_vehicles(self, frame: np.ndarray) -> List[Tuple]:
        """Detect vehicles in frame using YOLO."""
        results = self.model(frame, classes=[2, 3, 5, 7])  # car, motorcycle, bus, truck
        
        detections = []
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = box.conf[0].item()
                cls = int(box.cls[0].item())
                
                if conf > self.config.get("confidence", 0.7):
                    detections.append(([x1, y1, x2 - x1, y2 - y1], conf, cls))
        
        return detections
    
    def publish_detections(self, camera_id: int, tracks: List, frame: np.ndarray):
        """Publish detection results via MQTT."""
        timestamp = datetime.utcnow().isoformat()
        
        for track in tracks:
            if not track.is_confirmed():
                continue
            
            track_id = track.track_id
            bbox = track.to_ltrb()
            
            message = {
                "camera_id": camera_id,
                "track_id": track_id,
                "bbox": bbox.tolist(),
                "timestamp": timestamp,
                "frame_shape": frame.shape[:2]
            }
            
            self.mqtt_client.publish(
                f"traffic/detections/{camera_id}",
                json.dumps(message)
            )
    
    def display_frame(self, frame: np.ndarray, tracks: List):
        """Display frame with tracking info."""
        for track in tracks:
            if not track.is_confirmed():
                continue
            
            bbox = track.to_ltrb().astype(int)
            track_id = track.track_id
            
            cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
            cv2.putText(
                frame,
                f"ID: {track_id}",
                (bbox[0], bbox[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )
        
        cv2.imshow("Traffic Monitor", frame)
        cv2.waitKey(1)


def main():
    config = {
        "mqtt_host": "localhost",
        "mqtt_port": 1883,
        "frame_rate": 5,
        "confidence": 0.7,
        "display": False
    }
    
    processor = VideoProcessor(config)
    
    # Example: process camera 1
    processor.process_stream(
        camera_id=1,
        rtsp_url="rtsp://admin:password@camera-ip:554/stream"
    )


if __name__ == "__main__":
    main()
