FROM agrigorev/model-2024-hairstyle:v3

RUN pip install \
    https://github.com/alexeygrigorev/tflite-aws-lambda/raw/main/tflite/tflite_runtime-2.14.0-cp310-cp310-linux_x86_64.whl \
    pillow \
    numpy==1.23.2

COPY lambda_function.py .
COPY model_2024_hairstyle.tflite .

CMD ["lambda_function.lambda_handler"]
