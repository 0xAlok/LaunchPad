from app import create_app

app = create_app()

if __name__ == "__main__":
    # To seed DB: run `python seed.py` manually
    # from seed import seed
    # seed()

    app.run(debug=True, port=5001)
