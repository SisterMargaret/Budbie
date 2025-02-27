from django.core.exceptions import ValidationError
import os

def allow_only_images_validator(file):
    ext = os.path.splitext(file.name)[1]
    print(ext)
    valid_extensions = ['.png','.jpg','.jpeg']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension. only allowed' + str(valid_extensions))