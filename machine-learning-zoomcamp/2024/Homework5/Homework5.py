import pickle
from flask import Flask, request, jsonify

dv_file = "dv.bin"
model_file = "model1.bin"

with open(dv_file, 'rb') as f_in:
    dv = pickle.load(f_in)

with open(model_file, 'rb') as f_in:
    model = pickle.load(f_in)

app = Flask("subscription")

@app.route('/', methods=['POST'])
def predict():
    customer = request.get_json()

    X = dv.transform([customer])
    y_pred = model.predict_proba(X)[0, 1]
    subscribe = y_pred >= 0.5

    result = {
        'subscription_probability': float(y_pred),
        'subscribe': bool(subscribe)
    }

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9696)