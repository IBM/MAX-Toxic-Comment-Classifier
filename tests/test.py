#
# Copyright 2018-2019 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

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

    invalid_data4 = 3459000

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

    # verify that the input string is being returned
    assert response["results"][0]["original_text"] == "good string"

    # verify that 'good string' is non-toxic
    assert round(float(response['results'][0]['predictions']['toxic'])) == 0
    # verify that 'dumb string' is in fact toxic
    assert round(float(response['results'][1]['predictions']['toxic'])) == 1
    # verify that we have 6 labels
    assert len(response['results'][1]['predictions'].keys()) == 6

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
    assert round(float(response['results'][0]['predictions']['toxic'])) == 1
    # verify the outcome of the second comment
    assert round(float(response['results'][1]['predictions']['toxic'])) == 0
    # verify the outcome of the third comment
    assert round(float(response['results'][2]['predictions']['toxic'])) == 1

    # The last entry of samples/test_examples.csv contains all types of toxicity. This is verified here.
    with open('samples/test_examples.csv', 'rb') as fh:
        for line in fh:
            pass

        json_data3 = {
            "text": [str(line).split(',')[0]]
        }

    r = requests.post(url=model_endpoint, json=json_data3)

    assert r.status_code == 200
    response = r.json()

    assert response['status'] == 'ok'
    assert round(float(response['results'][0]['predictions']['toxic'])) == 1
    assert round(float(response['results'][0]['predictions']['severe_toxic'])) == 1
    assert round(float(response['results'][0]['predictions']['obscene'])) == 1
    assert round(float(response['results'][0]['predictions']['insult'])) == 1
    assert round(float(response['results'][0]['predictions']['threat'])) == 1
    assert round(float(response['results'][0]['predictions']['identity_hate'])) == 1

    # Test different input batch sizes
    for input_size in [4, 16, 32, 64, 75]:
        json_data4 = {
            "text": ["good string"]*input_size
        }

        r = requests.post(url=model_endpoint, json=json_data4)

        assert r.status_code == 200
        response = r.json()
        assert response['status'] == 'ok'

        assert len(response['results']) == len(json_data4["text"])


if __name__ == '__main__':
    pytest.main([__file__])
