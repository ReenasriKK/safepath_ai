# SafePath AI

**Tagline:** "AI-Powered Road Hazard Detection & Safe Route Recommendation"

## 1. Project Overview

SafePath AI is a comprehensive web application designed to enhance road safety by integrating AI-powered road hazard detection with intelligent route recommendation. Unlike traditional navigation systems that primarily focus on distance or travel time, SafePath AI analyzes real-time and community-reported road conditions to suggest safer routes, thereby minimizing risks for travelers. This project aims to deliver a production-quality application suitable for an AI project demonstration, showcasing a robust AI component and a professional user experience.

## 2. Problem Statement

Road hazards such as potholes, flooded areas, and unexpected obstacles pose significant risks to drivers, leading to accidents, vehicle damage, and increased travel times. Existing navigation systems often fail to account for these dynamic road conditions, leaving drivers vulnerable to unforeseen dangers. There is a critical need for a system that can proactively identify and communicate these hazards, enabling safer travel decisions.

## 3. Existing System Limitations

Traditional navigation applications typically rely on static map data and real-time traffic information. Their limitations include:

*   **Lack of Hazard Awareness:** Inability to detect and report dynamic road hazards like potholes, debris, or localized flooding.
*   **Route Optimization based on limited factors:** Routes are primarily optimized for shortest distance or fastest travel time, neglecting safety considerations.
*   **Delayed Information:** Community-reported hazards are often manually updated, leading to delays in information dissemination.
*   **No Predictive Analysis:** Absence of AI-driven analysis to predict potential risks based on environmental factors or historical data.

## 4. Proposed System: SafePath AI

SafePath AI addresses these limitations by offering an intelligent road safety platform. The system will:

*   **AI-Powered Hazard Detection:** Utilize advanced computer vision models (YOLOv8) to detect various road hazards from user-uploaded images.
*   **Dynamic Risk Assessment:** Assign a risk score to road segments based on detected hazards and community reports.
*   **Safe Route Recommendation:** Recommend alternative routes that minimize exposure to identified hazards, prioritizing user safety.
*   **Community Reporting:** Enable users to report hazards, contributing to a collective, real-time database of road conditions.
*   **User-Friendly Interface:** Provide a modern, intuitive interface for seamless interaction and information access.

## 5. Objectives

The primary objectives of the SafePath AI project are to:

*   Develop a Flask-based web application with secure user authentication.
*   Implement a robust AI module using YOLOv8 for accurate road hazard detection.
*   Integrate mapping functionalities (Leaflet.js, OpenStreetMap) for route visualization and hazard display.
*   Establish a system for calculating and displaying a 
Road Risk Score and Safety Score.
*   Create a community reporting feature for users to contribute hazard information.
*   Design a responsive and aesthetically pleasing UI with a dark, glassmorphism theme.
*   Generate comprehensive documentation including installation instructions and future scope.

## 6. Architecture

The SafePath AI application follows a client-server architecture, primarily utilizing the Flask web framework for the backend and a combination of HTML5, CSS3, and JavaScript for the frontend. The AI component, powered by YOLOv8, is integrated into the backend for image processing and hazard detection.

```mermaid
graph TD
    A[User] --> B(Web Browser)
    B --> C{Flask Application}
    C --> D[Authentication/Authorization]
    C --> E[Database (SQLite/SQLAlchemy)]
    C --> F[AI Module (YOLOv8, OpenCV)]
    C --> G[Mapping Services (Leaflet.js, OSRM API)]
    D --> E
    F --> E
    G --> B
    E --> C
    F --> C
    G --> C
```

## 7. AI Workflow

1.  **Image Upload:** Users upload road images via the web interface.
2.  **Pre-processing:** Images are pre-processed (e.g., resizing, normalization) if necessary.
3.  **Object Detection:** The YOLOv8 model processes the image to detect predefined road hazards (Pothole, Flooded Road, Road Block, Garbage, Fallen Tree, Construction Area, Low Visibility, Damaged Road).
4.  **Bounding Boxes & Confidence:** For each detected object, bounding boxes and confidence scores are generated.
5.  **Risk Scoring:** Each detected hazard contributes to a cumulative Road Risk Score based on predefined points:

    | Hazard Type       | Risk Points |
    | :---------------- | :---------- |
    | Pothole           | 20          |
    | Flooded Road      | 30          |
    | Road Block        | 25          |
    | Garbage           | 5           |
    | Fallen Tree       | 25          |
    | Construction Area | 15          |
    | Low Visibility    | 20          |
    | Damaged Road      | 15          |

6.  **Safety Recommendation:** The total Road Risk Score is converted into a Safety Score and a corresponding recommendation (Safe, Moderate, Dangerous).
7.  **Route Adjustment:** Based on the Safety Score and detected hazards, the system can recommend safer alternative routes.

## 8. YOLO Explanation

YOLO (You Only Look Once) is a state-of-the-art, real-time object detection system. YOLOv8, the latest iteration, offers improved accuracy and speed. It works by dividing the image into a grid and predicting bounding boxes and class probabilities for each grid cell simultaneously. This single-pass approach makes it highly efficient for applications requiring real-time performance, such as road hazard detection.

## 9. Technology Stack

| Category         | Technology      | Description                                          |
| :--------------- | :-------------- | :--------------------------------------------------- |
| **Frontend**     | HTML5           | Structure of web pages                               |
|                  | CSS3            | Styling, including dark theme & glassmorphism        |
|                  | Bootstrap 5     | Responsive design and UI components                  |
|                  | JavaScript      | Interactive elements and client-side logic           |
|                  | Chart.js        | Data visualization (e.g., dashboard charts)          |
| **Backend**      | Python Flask    | Lightweight web framework for application logic      |
| **Database**     | SQLite          | Serverless, file-based database                      |
|                  | SQLAlchemy      | Python SQL toolkit and Object-Relational Mapper      |
| **Authentication** | Flask-Login     | User session management                              |
| **Mapping**      | Leaflet.js      | Open-source JavaScript library for interactive maps  |
|                  | OpenStreetMap   | Free editable map of the world                       |
|                  | OSRM API        | Routing service for calculating paths                |
| **AI/ML**        | YOLOv8          | Real-time object detection for hazard identification |
|                  | Ultralytics     | Framework for YOLO models                            |
|                  | OpenCV          | Computer Vision library for image processing         |
|                  | NumPy           | Numerical computing for AI data manipulation         |
|                  | Pandas          | Data analysis and manipulation                       |

## 10. Installation

To set up and run SafePath AI locally, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd SafePathAI
    ```
2.  **Create a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: .\venv\Scripts\activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Download YOLOv8 model:**
    The `ai/detect.py` script will attempt to download `yolov8n.pt` if `ai/yolov8n.pt` is not found. For production use, you would typically train your own `best.pt` model and place it in the `ai/` directory.

5.  **Run the application:**
    ```bash
    python app.py
    ```

    The application will be accessible at `http://127.0.0.1:5000`.

## 11. Project Structure

```
SafePathAI/
├── app.py
├── models.py
├── routes.py
├── ai/
│   ├── detect.py
│   └── yolov8n.pt  # Or best.pt (downloaded automatically or custom trained)
├── templates/
│   ├── base.html
│   ├── landing.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── map.html
│   ├── hazard_detection.html
│   ├── hazard_result.html
│   ├── community_reports.html
│   ├── history.html
│   ├── profile.html
│   └── admin.html
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── img/
├── uploads/  # For uploaded images and detected outputs
├── database.db  # SQLite database file
├── requirements.txt
└── README.md
```

## 12. Future Scope

*   **Real-time Video Analysis:** Integrate live video stream processing for continuous hazard detection.
*   **Mobile Application:** Develop native iOS/Android applications for enhanced user experience and device integration.
*   **Predictive Hazard Mapping:** Use historical data and weather patterns to predict potential hazard locations.
*   **Advanced Routing Algorithms:** Implement more sophisticated routing algorithms that dynamically adjust based on real-time hazard data.
*   **Gamification:** Introduce elements like leaderboards and badges for community reporting to encourage participation.
*   **Integration with Vehicle Systems:** Explore integration with in-car systems for direct alerts and navigation.

## 13. Contributing

Contributions are welcome! Please fork the repository and submit pull requests.

## 14. License

This project is licensed under the MIT License.

## 15. Contact

For any inquiries, please contact [Your Name/Email/GitHub Profile].
