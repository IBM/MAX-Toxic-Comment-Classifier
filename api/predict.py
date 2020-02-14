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

from core.model import ModelWrapper
from maxfw.core import MAX_API, PredictAPI, MetadataAPI
from flask_restplus import fields
from flask import abort

# Set up parser for input data (http://flask-restplus.readthedocs.io/en/stable/parsing.html)
input_parser = MAX_API.model('ModelInput', {
    'text': fields.List(fields.String, required=True,
                        description='List of user comments (strings) to be analyzed for toxicity.')
})

# Creating a JSON response model: https://flask-restplus.readthedocs.io/en/stable/marshalling.html#the-api-model-factory
label_description = {
    'toxic': 'very bad, unpleasant, or harmful',
    'severe_toxic': 'extremely bad and offensive',
    'obscene': '(of the portrayal or description of sexual matters) offensive or disgusting by accepted standards of '
               'morality and decency',
    'threat': 'a statement of an intention to inflict pain, injury, damage, or other hostile action on someone in '
              'retribution for something done or not done',
    'insult': 'speak to or treat with disrespect or scornful abuse',
    'identity_hate': 'hatred, hostility, or violence towards members of a race, ethnicity, nation, religion, gender, '
                     'gender identity, sexual orientation or any other designated sector of society'
}

label_prediction = MAX_API.model('LabelPrediction', {
    'toxic': fields.Float(required=True, description=label_description['toxic']),
    'severe_toxic': fields.Float(required=True, description=label_description['severe_toxic']),
    'obscene': fields.Float(required=True, description=label_description['obscene']),
    'threat': fields.Float(required=True, description=label_description['threat']),
    'insult': fields.Float(required=True, description=label_description['insult']),
    'identity_hate': fields.Float(required=True, description=label_description['identity_hate']),
})


results_response = MAX_API.model("ModelResultResponse", {
    'original_text': fields.String(reqired=True, description='User submitted text'),
    'predictions': fields.Nested(label_prediction, description='Predicted labels and probabilities')
})

predict_response = MAX_API.model('ModelPredictResponse', {
    'status': fields.String(required=True, description='Response status message'),
    'results': fields.List(fields.Nested(results_response), description='Original Text, predicted labels, and probabilities')
})


class ModelLabelsAPI(MetadataAPI):
    '''API for getting information about the available toxicity tags.'''

    @MAX_API.doc('labels')
    def get(self):
        '''Return the list of labels that can be predicted by the model.'''
        result = dict()
        result['labels'] = {label: label_description[label] for label in label_description}
        result['count'] = len(label_description.keys())
        return result


class ModelPredictAPI(PredictAPI):
    model_wrapper = ModelWrapper()

    @MAX_API.doc('predict')
    @MAX_API.expect(input_parser, validate=True)
    @MAX_API.marshal_with(predict_response)
    def post(self):
        """Make a prediction given input data"""
        result = {'status': 'error'}

        input_json = MAX_API.payload

        # Make sure the input list is not empty
        if len(input_json['text']) == 0:
            abort(400, 'An empty list was provided. Please put add the input strings to this list.')

        try:
            output = self.model_wrapper.predict(input_json['text'])
            result['results'] = []
            for i in range(len(output)):
                res = {'original_text': input_json['text'][i],
                       'predictions': output[i]}
                result['results'].append(res)
            result['status'] = 'ok'
            return result

        except:  # noqa
            abort(500, "Model Inference Failed with valid input")
