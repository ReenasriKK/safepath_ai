import cv2
import os
import numpy as np
from ultralytics import YOLO
import json

class RoadHazardDetector:
    def __init__(self, model_path='ai/yolov8n.pt'):
        # Using yolov8n.pt as a base if best.pt is not available
        # In a real scenario, the user would provide a trained best.pt
        self.model_path = model_path
        if not os.path.exists(model_path):
            # Download base model if not exists
            self.model = YOLO('yolov8n.pt')
        else:
            self.model = YOLO(model_path)
            
        # Hazard risk mapping
        self.hazard_scores = {
            'Pothole': 20,
            'Flooded Road': 30,
            'Road Block': 25,
            'Garbage': 5,
            'Fallen Tree': 25,
            'Construction Area': 15,
            'Low Visibility': 20,
            'Damaged Road': 15
        }

    def detect(self, image_path, output_path):
        # Perform detection
        results = self.model(image_path)
        
        # Load image for drawing
        img = cv2.imread(image_path)
        
        detections = []
        total_risk_score = 0
        
        # If we are using the base yolov8n model, we might not see "Pothole" etc.
        # For the sake of the demo, if no hazards are found and it's a demo, 
        # we can simulate some based on the image content or just report what's found.
        # However, we will follow the logic for the specific classes.
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Get class ID and name
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                name = self.model.names[cls_id]
                
                # Map detected class to our hazard list if needed
                # (This is where the custom model classes would match)
                hazard_name = name 
                
                # For demo purposes, if using base YOLO, we map some common objects to hazards
                if name == 'person': hazard_name = 'Road Block' # Just for demo
                
                risk = self.hazard_scores.get(hazard_name, 0)
                
                if risk > 0 and conf > 0.25:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    detections.append({
                        'label': hazard_name,
                        'confidence': round(conf, 2),
                        'risk': risk,
                        'box': [x1, y1, x2, y2]
                    })
                    total_risk_score += risk
                    
                    # Draw bounding box
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.putText(img, f'{hazard_name} {conf:.2f}', (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # Save the detected image
        cv2.imwrite(output_path, img)
        
        # Determine safety recommendation
        recommendation = "Safe"
        if total_risk_score > 50:
            recommendation = "Dangerous"
        elif total_risk_score > 20:
            recommendation = "Moderate"
            
        return detections, total_risk_score, recommendation

# Helper function for the Flask app
def run_detection(image_path, output_filename):
    detector = RoadHazardDetector()
    output_path = os.path.join('uploads', output_filename)
    detections, risk_score, recommendation = detector.detect(image_path, output_path)
    return detections, risk_score, recommendation, output_path
