from flask import Flask, render_template, request, send_file
from PIL import Image, ImageEnhance, ImageOps, ImageFilter, ExifTags
import os
import random

app = Flask(__name__, static_folder="static", template_folder="templates")

UPLOAD_FOLDER = "uploads"
MODIFIED_FOLDER = "modified"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MODIFIED_FOLDER, exist_ok=True)

def modify_image(image_path):
    """Modyfikuje obraz, aby był unikalny dla algorytmów wykrywających duplikaty"""
    image = Image.open(image_path)

    # 1️⃣ USUWANIE METADANYCH (EXIF)
    image = ImageOps.exif_transpose(image)  # Obrót, jeśli EXIF zawiera orientację
    data = list(image.getdata())
    image = Image.new(image.mode, image.size)
    image.putdata(data)  # Tworzy nowy obraz bez metadanych EXIF

    # 2️⃣ LOSOWY OBRÓT OBRAZU O KILKA STOPNI
    rotation_angle = random.uniform(-10, 10)  # Losowy obrót od -5° do +5°
    image = image.rotate(rotation_angle, expand=True)  # Expand=True zapobiega ucięciu rogów

    # 3️⃣ LOSOWA ZMIANA JASNOŚCI I KONTRASTU
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(random.uniform(0.9, 1.1))  # Lekka zmiana jasności

    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(random.uniform(0.9, 1.3))  # Lekka zmiana kontrastu

    # 4️⃣ DODAWANIE SZUMU DO OBRAZU
    pixels = image.load()
    width, height = image.size
    for _ in range(int(width * height * 0.09)):  # 2% pikseli losowo zmienionych
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        r, g, b = pixels[x, y]
        pixels[x, y] = (min(255, r + random.randint(-15, 15)),
                        min(255, g + random.randint(-15, 15)),
                        min(255, b + random.randint(-15, 15)))

    # 5️⃣ LEKKIE ROZMYCIE I SZUM GAUSSOWSKI
    if 0:
        image = image.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.3, 0.7)))

    # 6️⃣ ODBICIE LUSTRZANE (ZMIANA WZORU OBRAZU)
    if 0:
        image = ImageOps.mirror(image)

    # 7️⃣ USUNIĘCIE METADANYCH PRZY ZAPISIE
    modified_path = os.path.join(MODIFIED_FOLDER, f"modified_{random.randint(100,999)}.jpg")
    image.save(modified_path, "JPEG", quality=95)  # Zapisuje bez metadanych EXIF

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
    port = int(os.environ.get("PORT", 10000))  # Render wymaga portu
    app.run(host="0.0.0.0", port=port)
