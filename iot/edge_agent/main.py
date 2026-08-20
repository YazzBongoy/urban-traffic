#!/usr/bin/env python3
"""
Edge Agent for NVIDIA Jetson
Runs on edge devices to process video locally and reduce bandwidth.
"""

import cv2
import numpy as np
from ultralytics import YOLO
import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime
from typing import Dict, List
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EdgeAgent:
    def __init__(self, config: Dict):
        self.config = config
        self.camera_id = config.get("camera_id", 1)
        self.rtsp_url = config.get("rtsp_url")
        
        # Load YOLO model
        self.model = YOLO("yolov8n.pt")
        
        # MQTT connection
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.connect(
            config.get("mqtt_host", "localhost"),
            config.get("mqtt_port", 1883),
            60
        )
        self.mqtt_client.loop_start()
        
        # Statistics
        self.stats = {
            "frames_processed": 0,
            "vehicles_detected": 0,
            "start_time": datetime.utcnow()
        }
    
    def run(self):
        """Main processing loop."""
        logger.info(f"Starting Edge Agent for camera {self.camera_id}")
        
        cap = cv2.VideoCapture(self.rtsp_url)
        
        if not cap.isOpened():
            logger.error(f"Failed to open stream: {self.rtsp_url}")
            return
        
        while True:
            ret, frame = cap.read()
            
            if not ret:
                logger.warning("Failed to read frame, reconnecting...")
                cap.release()
                time.sleep(5)
                cap = cv2.VideoCapture(self.rtsp_url)
                continue
            
            # Process frame
            detections = self.process_frame(frame)
            
            # Publish if vehicles detected
            if detections:
                self.publish_detections(detections)
            
            self.stats["frames_processed"] += 1
            
            # Log stats every 100 frames
            if self.stats["frames_processed"] % 100 == 0:
                self.log_stats()
            
            # Control frame rate
            time.sleep(1.0 / self.config.get("frame_rate", 5))
        
        cap.release()
    
    def process_frame(self, frame: np.ndarray) -> List[Dict]:
        """Process a single frame and detect vehicles."""
        results = self.model(frame, classes=[2, 3, 5, 7])  # car, motorcycle, bus, truck
        
        detections = []
        
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = box.conf[0].item()
                cls = int(box.cls[0].item())
                
                if conf > self.config.get("confidence", 0.7):
                    detection = {
                        "bbox": [x1, y1, x2 - x1, y2 - y1],
                        "confidence": conf,
                        "class": cls,
                        "class_name": self.model.names[cls]
                    }
                    detections.append(detection)
                    self.stats["vehicles_detected"] += 1
        
        return detections
    
    def publish_detections(self, detections: List[Dict]):
        """Publish detection results via MQTT."""
        message = {
            "camera_id": self.camera_id,
            "timestamp": datetime.utcnow().isoformat(),
            "detections": detections,
            "stats": self.stats
        }
        
        self.mqtt_client.publish(
            f"traffic/edge/{self.camera_id}/detections",
            json.dumps(message)
        )
    
    def log_stats(self):
        """Log processing statistics."""
        elapsed = (datetime.utcnow() - self.stats["start_time"]).seconds
        fps = self.stats["frames_processed"] / max(elapsed, 1)
        
        logger.info(
            f"Camera {self.camera_id}: "
            f"{self.stats['frames_processed']} frames, "
            f"{self.stats['vehicles_detected']} vehicles, "
            f"{fps:.2f} FPS"
        )


def main():
    config = {
        "camera_id": int(os.getenv("CAMERA_ID", 1)),
        "rtsp_url": os.getenv("RTSP_URL", "rtsp://admin:password@camera-ip:554/stream"),
        "mqtt_host": os.getenv("MQTT_HOST", "localhost"),
        "mqtt_port": int(os.getenv("MQTT_PORT", 1883)),
        "frame_rate": int(os.getenv("FRAME_RATE", 5)),
        "confidence": float(os.getenv("CONFIDENCE", 0.7))
    }
    
    agent = EdgeAgent(config)
    agent.run()


if __name__ == "__main__":
    main()
