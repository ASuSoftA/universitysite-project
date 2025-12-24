import os
import uuid
from flask import current_app

def save_image(file):
    if not file or file.filename == '':
        return None

    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4().hex}{ext}"

    upload_path = os.path.join(
        current_app.root_path,
        'static',
        'uploads',
        'faculties'
    )

    os.makedirs(upload_path, exist_ok=True)

    file.save(os.path.join(upload_path, filename))
    return filename
