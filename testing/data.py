import time
import random
import requests

# Replace with your actual API endpoint
API_ENDPOINT = "http://localhost:8000/api/sensor-data/"

def generate_sensor_data():
    """Generate random ECG and temperature sensor data."""
    ecg_value = random.uniform(60.0, 100.0)  # Simulate ECG value (e.g., 60 to 100 bpm)
    temperature_value = random.uniform(36.0, 37.5)  # Simulate temperature value (e.g., 36 to 37.5 °C)
    return {
        "ecg": round(ecg_value, 2),
        "temperature": round(temperature_value, 2)
    }

def send_sensor_data(data):
    """Send the sensor data to the Django Ninja API endpoint."""
    try:
        response = requests.post(API_ENDPOINT, json=data)
        if response.status_code == 200:
            print(f"Data sent successfully: {data}")
        else:
            print(f"Failed to send data. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending data: {e}")

if __name__ == "__main__":
    while True:
        # Generate random sensor data
        sensor_data = generate_sensor_data()

        # Send the generated data to the server
        send_sensor_data(sensor_data)

        # Wait for 2 seconds before sending the next set of data
        time.sleep(2)
