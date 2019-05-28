import pytest
import requests


def test_swagger():

    model_endpoint = 'http://localhost:5000/swagger.json'

    r = requests.get(url=model_endpoint)
    assert r.status_code == 200
    assert r.headers['Content-Type'] == 'application/json'

    json = r.json()
    assert 'swagger' in json
    assert json.get('info') and json.get('info').get('title') == 'MAX Toxic Comment Classifier'


def test_metadata():

    model_endpoint = 'http://localhost:5000/model/metadata'

    r = requests.get(url=model_endpoint)
    assert r.status_code == 200

    metadata = r.json()
    assert metadata['id'] == 'max-toxic-comment-classifier'
    assert metadata['name'] == 'MAX Toxic Comment Classifier'
    assert metadata['description'] == 'BERT Base finetuned on toxic comments from Wikipedia.'
    assert metadata['license'] == 'Apache V2'
    assert metadata['type'] == 'Text Classification'
    assert 'developer.ibm.com' in metadata['source']


def test_invalid_input():

    model_endpoint = 'http://localhost:5000/model/predict'

    invalid_data = {
        "not_text": []
    }

    invalid_data2 = {}

    invalid_data3 = ''

    invalid_data4 = 3459_000

    invalid_data5 = {'text': 45435}

    invalid_data6 = {'text': [45435]}

    r = requests.post(url=model_endpoint, json=invalid_data)
    assert r.status_code == 400

    r = requests.post(url=model_endpoint, json=invalid_data2)
    assert r.status_code == 400

    r = requests.post(url=model_endpoint, json=invalid_data3)
    assert r.status_code == 400

    r = requests.post(url=model_endpoint, json=invalid_data4)
    assert r.status_code == 400

    r = requests.post(url=model_endpoint, json=invalid_data5)
    assert r.status_code == 400

    r = requests.post(url=model_endpoint, json=invalid_data6)
    assert r.status_code == 400


def test_labels_reponse():

    model_endpoint = 'http://localhost:5000/model/labels'

    r = requests.get(url=model_endpoint)

    assert r.status_code == 200
    response = r.json()
    assert response['count'] == 6
    assert set(response['labels'].keys()) == {'threat', 'insult', 'toxic', 'severe_toxic', 'identity_hate', 'obscene'}


def test_predict_response():

    model_endpoint = 'http://localhost:5000/model/predict'

    json_data = {
        "text": ["good string",
                 "dumb string"]
    }

    r = requests.post(url=model_endpoint, json=json_data)

    assert r.status_code == 200
    response = r.json()
    assert response['status'] == 'ok'

    # verify that 'good string' is non-toxic
    assert round(float(response['predictions'][0][0]['toxic'])) == 0
    # verify that 'dumb string' is in fact toxic
    assert round(float(response['predictions'][1][0]['toxic'])) == 1
    # verify that we have 6 labels
    assert len(response['predictions'][1][0].keys()) == 6

    json_data2 = {
        "text": [
            "I would like to respectfully punch you in the mouth.",
            "The Model Asset Exchange is a crucial element of a developer's toolkit.",
            "This code is amongst the ugliest I have ever encountered."
        ]
    }

    r = requests.post(url=model_endpoint, json=json_data2)

    assert r.status_code == 200
    response = r.json()
    assert response['status'] == 'ok'

    # verify the outcome of the first comment
    assert round(float(response['predictions'][0][0]['toxic'])) == 1
    # verify the outcome of the second comment
    assert round(float(response['predictions'][1][0]['toxic'])) == 0
    # verify the outcome of the third comment
    assert round(float(response['predictions'][2][0]['toxic'])) == 1

    # The last entry of assets/test_examples.csv contains all types of toxicity. This is verified here.
    with open('assets/test_examples.csv', 'rb') as fh:
        for line in fh:
            pass

        json_data3 = {
            "text": [str(line).split(',')[0]]
        }

    r = requests.post(url=model_endpoint, json=json_data3)

    assert r.status_code == 200
    response = r.json()

    assert response['status'] == 'ok'
    assert round(float(response['predictions'][0][0]['toxic'])) == 1
    assert round(float(response['predictions'][0][0]['severe_toxic'])) == 1
    assert round(float(response['predictions'][0][0]['obscene'])) == 1
    assert round(float(response['predictions'][0][0]['insult'])) == 1
    assert round(float(response['predictions'][0][0]['threat'])) == 1
    assert round(float(response['predictions'][0][0]['identity_hate'])) == 1

    # Test different input batch sizes
    for input_size in [4, 16, 32, 64, 75]:
        json_data4 = {
            "text": ["good string"]*input_size
        }

        r = requests.post(url=model_endpoint, json=json_data4)

        assert r.status_code == 200
        response = r.json()
        assert response['status'] == 'ok'

        assert len(response['predictions']) == len(json_data4["text"])


if __name__ == '__main__':
    pytest.main([__file__])
