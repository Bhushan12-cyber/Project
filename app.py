from flask import Flask, render_template, request
import cv2
import numpy as np
import joblib
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

model = joblib.load('model.pkl')
label_encoder = joblib.load('labels.pkl')

def extract_features(image_path):
    image = cv2.imread(image_path)
    image = cv2.resize(image, (200, 200))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, np.ones((5,5), np.uint8))
    mean = np.mean(morph)
    std = np.std(morph)
    var = np.var(morph)
    entropy = -np.sum((morph/255) * np.log2((morph/255) + 1e-10)) / morph.size
    kurt = np.mean((morph - mean)**4) / (std**4 + 1e-10)
    return [mean, std, entropy, var, kurt]

@app.route("/", methods=["GET", "POST"])
def index():
    prediction = None
    if request.method == "POST":
        file = request.files["file"]
        if file:
            path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(path)
            features = np.array(extract_features(path)).reshape(1, -1)
            pred = model.predict(features)
            prediction = label_encoder.inverse_transform(pred)[0]
    return render_template("index.html", prediction=prediction)

if __name__ == "__main__":
    app.run(debug=True)
