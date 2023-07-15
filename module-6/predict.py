import pickle
import mlflow

from flask import Flask, request, jsonify

RUN_ID = 'de9409e3282d4abda11017c47373ed85'
MLFLOW_TRACKING_URI = "http://localhost:5000"
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

logged_model = f'runs:/{RUN_ID}/model'

model = mlflow.pyfunc.load_model(logged_model)

# client = MlflowClient(tracking_uri=MLFLOW_TRACKING_URI)

# client.download_artifacts(run_id=RUN_ID, path='dict_vectorizer.bin')

# with open('lin_reg_2.bin', 'rb') as f_in:
#     (dv, model) = pickle.load(f_in)


def prepare_features(ride):
    features = {}
    features['PU_DO'] = '%s_%s' % (ride['PULocationID'], ride['PULocationID'])
    features['trip_distance'] = ride['trip_distance']
    return features


def predict(features):
    """Return linear regression precitions."""
    preds = model.predict(features)
    return float(preds[0])


app = Flask('duration-prediction')


@app.route('/predict', methods=['POST'])
def predict_endpoint():
    rider = request.get_json()
    features = prepare_features(rider)
    pred = predict(features)

    result = {
        'duration': pred,
        'version': RUN_ID,
    }

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9696)
