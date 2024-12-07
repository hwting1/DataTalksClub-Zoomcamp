from urllib import request
from io import BytesIO
import numpy as np
from PIL import Image
import tflite_runtime.interpreter as tflite

interpreter = tflite.Interpreter(model_path="model_2024_hairstyle_v2.tflite")
interpreter.allocate_tensors()
input_index = interpreter.get_input_details()[0]['index']
output_index = interpreter.get_output_details()[0]['index']

def predict(url):
    with request.urlopen(url) as resp:
        buffer = resp.read()
    stream = BytesIO(buffer)
    img = Image.open(stream)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    img = img.resize((200, 200), Image.NEAREST)
    img = np.array(img, dtype=np.float32)
    img = np.expand_dims(img, axis=0) / 255.0
    interpreter.set_tensor(input_index, img)
    interpreter.invoke()
    pred = interpreter.get_tensor(output_index)
    return pred[0].tolist()

def lambda_handler(event, context):
    url = event["url"]
    result = predict(url)
    return result