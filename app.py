from app.web_app import create_app

app = create_app(model_paths={
    "internship": "model/internship_cnn.keras",
    "medical": "model/medical_cnn.keras"
})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
