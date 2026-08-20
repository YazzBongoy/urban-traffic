#!/usr/bin/env python3
"""
OCR Service for License Plate Recognition
Processes vehicle detections and extracts plate numbers.
"""

import cv2
import numpy as np
import pytesseract
import re
import json
import paho.mqtt.client as mqtt
from datetime import datetime
from typing import Optional, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlateOCR:
    def __init__(self, config: Dict):
        self.config = config
        self.mqtt_client = mqtt.Client()
        
        # Connect to MQTT broker
        self.mqtt_client.connect(
            config.get("mqtt_host", "localhost"),
            config.get("mqtt_port", 1883),
            60
        )
        self.mqtt_client.loop_start()
        
        # Subscribe to detection events
        self.mqtt_client.subscribe("traffic/detections/#")
        self.mqtt_client.on_message = self.on_message
        
        # Plate patterns (various country formats)
        self.plate_patterns = [
            r'^[A-Z]{3}\s?\d{3,4}$',  # Standard format
            r'^\d{3,4}\s?[A-Z]{3}$',  # Reverse format
            r'^[A-Z]{2}\s?\d{4}$',    # Alternative format
        ]
    
    def on_message(self, client, userdata, msg):
        """Handle incoming detection messages."""
        try:
            data = json.loads(msg.payload.decode())
            self.process_detection(data)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def process_detection(self, detection: Dict):
        """Process a vehicle detection and extract plate number."""
        camera_id = detection.get("camera_id")
        track_id = detection.get("track_id")
        bbox = detection.get("bbox")
        timestamp = detection.get("timestamp")
        
        # Extract plate region from frame
        plate_region = self.extract_plate_region(bbox)
        
        if plate_region is not None:
            plate_number = self.recognize_plate(plate_region)
            
            if plate_number:
                # Publish plate reading
                message = {
                    "camera_id": camera_id,
                    "track_id": track_id,
                    "plate_number": plate_number,
                    "confidence": detection.get("confidence", 0.0),
                    "timestamp": timestamp,
                    "direction": self.estimate_direction(bbox)
                }
                
                self.mqtt_client.publish(
                    "traffic/plates",
                    json.dumps(message)
                )
                
                logger.info(f"Plate recognized: {plate_number} (Camera: {camera_id})")
    
    def extract_plate_region(self, bbox: list) -> Optional[np.ndarray]:
        """Extract plate region from bounding box."""
        # This is a simplified version
        # In production, you'd extract from the actual frame
        x, y, w, h = bbox
        
        # Create synthetic plate region for testing
        plate_region = np.zeros((100, 200, 3), dtype=np.uint8)
        plate_region[:] = (255, 255, 255)  # White background
        
        return plate_region
    
    def recognize_plate(self, plate_region: np.ndarray) -> Optional[str]:
        """Recognize plate number from image region."""
        # Preprocess image
        gray = cv2.cvtColor(plate_region, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Apply OCR
        text = pytesseract.image_to_string(
            thresh,
            config='--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        )
        
        # Clean and validate
        text = text.strip().upper()
        text = re.sub(r'[^A-Z0-9]', '', text)
        
        if self.validate_plate(text):
            return text
        
        return None
    
    def validate_plate(self, plate: str) -> bool:
        """Validate plate number format."""
        if not plate or len(plate) < 5:
            return False
        
        for pattern in self.plate_patterns:
            if re.match(pattern, plate):
                return True
        
        return False
    
    def estimate_direction(self, bbox: list) -> str:
        """Estimate vehicle direction from bounding box."""
        # Simplified direction estimation
        x, y, w, h = bbox
        center_x = x + w / 2
        
        if center_x < 320:  # Assuming 640px width
            return "left"
        else:
            return "right"


def main():
    config = {
        "mqtt_host": "localhost",
        "mqtt_port": 1883
    }
    
    ocr = PlateOCR(config)
    logger.info("OCR Service started")
    
    # Keep running
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("OCR Service stopped")


if __name__ == "__main__":
    main()
