# Plant Growth Analytics System

## Introduction

The Plant Growth Analytics System is designed to provide insights into optimal growing conditions for plants based on real-time sensor data. This system enables easy ingestion of sensor data, performs analytics, and delivers actionable insights for plant care.

## Key Features

- **Efficient Sensor Data Ingestion**: Upload multiple sensor readings at once or a single reading.
- **Analytics**: Provides optimal environmental conditions for plants and plant growth trends.
- **Containerization**: Ensures easy deployment via Docker.

## API Endpoints

### 1. Data Ingestion

#### **POST** `/api/v1/sensor-data/batch`
- **Description**: Upload multiple sensor readings.
- **Response**: `201 Created`

#### **POST** `/api/v1/sensor-data/single`
- **Description**: Upload a single sensor reading for a plant.
- **Response**: `201 Created`

#### **GET** `/api/v1/sensor-data/{zone_id}`
- **Description**: Retrieves all sensor data for a specific zone.
- **Response**: Returns sensor data for the given zone.

#### **GET** `/api/v1/sensor-data/{zone_id}/{plant_id}`
- **Description**: Retrieves sensor data for a specific plant in a zone.
- **Response**: Returns sensor data for the given plant in the specified zone.

### 2. Analytics Endpoints

#### **GET** `/api/v1/analytics/growth-rate/{plant_id}`
- **Description**: Returns the growth rate for a plant over time.

#### **GET** `/api/v1/analytics/optimal-conditions/{species_id}`
- **Description**: Determines the ideal growing conditions for a plant species.
- **Response Example**:
    ```json
    {
      "zone_id": "zone_1",
      "plant_id": "tomato_1",
      "temperature": 25.22,
      "humidity": 64.19,
      "soil_moisture": 0.7,
      "light_level": 803.5,
      "id": "778e5eee-aa6a-42db-a73d-d86f7b0551f9"
    }
    ```

## Future Considerations

- **Security**: Implement token expiration and refreshing mechanisms.
- **Rate Limiting**: Prevent over-usage of certain endpoints.

## Setup Instructions

1. **Clone Repository**:
    ```bash
    git clone <repo_url>
    cd plant-growth-analytics
    ```

2. **Run Docker Compose**:
    ```bash
    docker-compose up --build
    ```

3. **Access the API**:
    - API URL: `http://localhost:8000`

## AI Usage Documentation

### AI Role

- **Docker Setup Guidance**: Used AI to guide the initial setup of Docker.
- **Project Requirements Verification**: Cross-checked the entire project with the requirements to ensure all conditions were met.
- **Troubleshooting**: Troubleshot compatibility issues related to older Docker versions and libraries.
- **Debugging**: Used AI to assist in resolving errors and debugging the application.

## Additional Future Considerations

- **Organization**: Add more folders and modularity for better organization.
- **Front-End Implementation**: Implement a front-end with React.js or Vue.js.
- **Machine Learning**: Incorporate machine learning models for further data analysis and predictions.
- **Data Smoothing**: Use data smoothing techniques for improved accuracy.
- **Analytics and Reporting**: Add detailed analytics and visual reporting.
- **Environment Variables**: Utilize environment variables to store sensitive information (e.g., database password).

## Conclusion

The Plant Growth Analytics System satisfies the core requirements by enabling efficient sensor data ingestion, providing actionable insights through analytics endpoints, and optimizing the database for performance. Containerization ensures ease of deployment, making the system scalable and robust.
