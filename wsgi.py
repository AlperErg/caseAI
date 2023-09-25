from app import create_app  # Import your Flask application factory function

app = create_app()  # Create an instance of your Flask app

if __name__ == "__main__":
    app.run()