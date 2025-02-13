from flask import Flask, render_template, request, send_file
from PIL import Image, ImageEnhance
import os
import random

app = Flask(__name__, static_folder="static", template_folder="templates")

UPLOAD_FOLDER = "uploads"
MODIFIED_FOLDER = "modified"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MODIFIED_FOLDER, exist_ok=True)

def modify_image(image_path):
    """Modyfikuje obraz, aby był unikalny."""
    image = Image.open(image_path)

    # Zmiana jasności
    enhancer = ImageEnhance.Brightness(image)
    brightness_factor = random.uniform(0.3, 1)
    image = enhancer.enhance(brightness_factor)

    # Dodanie szumu (pikselowe zmiany)
    pixels = image.load()
    width, height = image.size
    for _ in range(int(width * height * 0.09)):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        r, g, b = pixels[x, y]
        pixels[x, y] = (min(255, r + random.randint(-20, 20)),
                        min(255, g + random.randint(-20, 20)),
                        min(255, b + random.randint(-20, 20)))

    modified_path = os.path.join(MODIFIED_FOLDER, f"modified_{random.randint(100,999)}.jpg")
    image.save(modified_path)
    return modified_path

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files["file"]
        if file:
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)

            modified_path = modify_image(file_path)
            return send_file(modified_path, as_attachment=True)

    return render_template("index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render przydziela dynamiczny port
    app.run(host="0.0.0.0", port=port)