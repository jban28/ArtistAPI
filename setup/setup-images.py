import json
from PIL import Image

current_image_folder = "/mnt/c/Users/James/Google Drive/Programming/MattPagettWebsite/MattPagettVue/public"
new_image_folder = "./images/"

bodies_json = json.load(open("./setup/bodies.json", "r"))
flowers_json = json.load(open("./setup/flowers.json", "r"))
images_json = bodies_json + flowers_json

all_images = []

i = 0
j = 0
for image in images_json:
    image_file = Image.open(f"{current_image_folder}{image['srcFull']}")
    thumb_file = Image.open(f"{current_image_folder}{image['srcThumb']}")
    
    url = image["name"]
    for char in url:
        if char.isspace():
            url = url.replace(" ", "_")
        elif not (char.isalnum() or (char == "-")):
            url = url.replace(char, "")

    new_file_path = f"Matt_Pagett/{image['series']}/full/{url}.jpg"
    image_file.save(f"{new_image_folder}{new_file_path}")
    image_file.close()

    new_thumb_path = f"Matt_Pagett/{image['series']}/thumb/{url}.jpg"
    thumb_file.save(f"{new_image_folder}{new_thumb_path}")
    thumb_file.close()

    image["sequence"] = i
    image["srcFull"] = new_file_path
    image["srcThumb"] = new_thumb_path
    
    if image["series"] == "bodies":
        image["sequence"] = i
        i += 1
    elif image["series"] == "flowers":
        image["sequence"] = j
        j += 1
    


    all_images.append(image)


json_file = open("images.json", "w")
json_file.write(json.dumps(all_images, indent=2))