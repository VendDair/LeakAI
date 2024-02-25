import json
import requests
import base64 as bs

def get_data(key: str):
    # Reads the json from src/data.json and returns the value by key provided
    try:
        with open("src/data.json", "r") as file:
            data = json.load(file)
            return data.get(key)
    except FileNotFoundError:
        print("Error: JSON file not found.")
        exit(69)
    except json.JSONDecodeError:
        print("error: unable to decode json file.")
        exit(69)

def write_data(key: str, value: str):
    try:
        with open("src/data.json", "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        print("Error: JSON file not found.")
        exit(69)
    except json.JSONDecodeError:
        print("Error: unable to decode json file.")
        exit(69)

    data[key] = value

    with open("src/data.json", "w") as file:
        json.dump(data, file)


def get_headers():
    key = get_data("key")
    return {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {key}"
    }

def generate(prompt: str, model: str, steps: int, guidance: float, negative_prompt: str):
    url = "https://api.getimg.ai/v1/stable-diffusion/text-to-image"

    payload = {
        "model": model,
        "prompt": prompt,
        "negative_prompt": f"Disfigured, blurry, ugly, distortion, {negative_prompt}",
        "width": 512,
        "height": 512,
        # "steps": 25,
        "steps": steps,
        # "guidance": 7.5,
        "guidance": guidance,
        "scheduler": "dpmsolver++",
        "output_format": "jpeg"
    }
    
    response = requests.post(url, json=payload, headers=get_headers())
    responseJson = response.json()
    
    base64_image = responseJson["image"]
    print(base64_image)

    return save_to_img(base64_image.encode("utf-8"), f"src/images/{get_data('id')}.jpg")


def save_to_img(base64, file_name):
    
    write_data("last_image_used", file_name)
    write_data("base64", base64.decode())

    with open(file_name, "wb") as file:
        file.write(bs.decodebytes(base64))

    write_data("id", get_data("id")+1)

    return file_name


def get_models():
    url = "https://api.getimg.ai/v1/models"

    headers = {
        "accept": "application/json",
        "authorization": "Bearer key-4fRqe77EDaVaCV12w7fWqYXXtjg9DJTxqbuHfOwjekC5iB9r2j8XciHSxlcKw7gpNnslNWF4OwYBotJfji0TJomrgMbRuh64"
    }
    response = requests.get(url, headers=headers)
    models = []
    for item in response.json():
        models.append(item["id"])
    return models





