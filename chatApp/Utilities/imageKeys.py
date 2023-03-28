import base64
import datetime
from django.core.files.base import ContentFile

def imageKeys(chat_data, Image, radon_title, user):
    images_id = ()
    image_title = f'{radon_title} {user} {str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))}'
    try:
        # get images and save as objects
        image_keys = list(chat_data)[-int(chat_data["image_length"]):]

        for i in image_keys:
            imageModel = Image()
            image_data = chat_data[i]
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr))
            file_name = "chatImage." + ext

            imageModel.name = image_title
            imageModel.image.save(file_name, data, save=True)
            imageModel.save()

        # get images and extract ID
        for i in image_keys:
            image = Image.objects.filter(
                name=image_title)
            images_id = (tuple(image.values_list('id', flat=True)))
            break

        return images_id
    except Exception as e:
        print(e)
