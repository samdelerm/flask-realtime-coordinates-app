# Flask Real-Time Coordinates App

This project is a Flask web application that displays real-time coordinates of five points, including a ball and two blue and green points. The application utilizes Flask-SocketIO for real-time communication between the server and the client.

## Project Structure

```
flask-realtime-coordinates-app
├── app.py                # Main entry point of the Flask application
├── requirements.txt      # Lists project dependencies
├── static
│   └── style.css         # CSS styles for the web application
├── templates
│   └── index.html        # HTML template for displaying coordinates
└── README.md             # Project documentation
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd flask-realtime-coordinates-app
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```
   python app.py
   ```

2. Open your web browser and navigate to `http://127.0.0.1:5000` to view the real-time coordinates.

## Dependencies

- Flask
- Flask-SocketIO

## License

This project is licensed under the MIT License.