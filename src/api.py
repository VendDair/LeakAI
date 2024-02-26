import json
import requests
import base64 as bs
import g4f

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

def get_set_base64(file_path: str):
    with open(file_path, "rb") as image_file:
        binary_data = image_file.read()
        base64 = bs.b64encode(binary_data).decode('utf-8')
        write_data("base64", bs.b64encode(binary_data).decode('utf-8'))
        print(base64)
        return base64


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

    return save_to_img(base64_image.encode("utf-8"))


def save_to_img(base64):
    file_name = f"src/images/{get_data('id')}.jpg"  
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


def gpt_request(text: str):
    response = g4f.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user",
           "content": f'Make an prompt for Ai that generate photos based on user prompt. Your task is to rewrite the following prompt to make the result as best as possible (it doesnt need to be long). Your answer need to be only the prompt: "{text}"'}],
        # stream=True,
        version="0.1.9.3",
        # provider=g4f.Provider.You,
    )
    resp_list = []
    for message in response:
        resp_list.append(message)
    resp = "".join(resp_list)
    return resp

def image_to_image(prompt: str, model: str, steps: int, guidance: float, strength: float, negative_prompt: str):
    url = "https://api.getimg.ai/v1/stable-diffusion/image-to-image"

    payload = {
        "model": model,
        "prompt": prompt,
        "negative_prompt": f"Disfigured, blurry, ugly, distortion, {negative_prompt}",
        "image": get_data("base64"),
        "strength": strength,
        "steps": steps,
        "guidance": guidance
    }

    response = requests.post(url, json=payload, headers=get_headers())

    print(response.text)

    responseJson = response.json()

    base64_image = responseJson["image"]
    return save_to_img(base64_image.encode("utf-8"))

def upscale():
    url = "https://api.getimg.ai/v1/enhancements/upscale"

    payload = {
        "model": "real-esrgan-4x",
        "image": get_data("base64"),
        "scale": 4,
        "output_format": "jpeg"
    }
    response = requests.post(url, json=payload, headers=get_headers())

    print(response.text)
    responseJson = response.json()

    base64_image = responseJson["image"]
    return save_to_img(base64_image.encode("utf-8"))






