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

# Flask settings
DEBUG = False

# Flask-restplus settings
RESTPLUS_MASK_SWAGGER = False
SWAGGER_UI_DOC_EXPANSION = 'none'

# API metadata
API_TITLE = 'MAX Toxic Comment Classifier'
API_DESC = 'Detect 6 types of toxicity in user comments.'
API_VERSION = '2.0.0'

# default model
MODEL_NAME = 'BERT_PyTorch'
DEFAULT_MODEL_PATH = f'assets/{MODEL_NAME}/'

# the output labels
LABEL_LIST = ['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate']

# the metadata of the model
MODEL_META_DATA = {
    'id': 'max-toxic-comment-classifier',
    'name': 'MAX Toxic Comment Classifier',
    'description': 'BERT Base finetuned on toxic comments from Wikipedia.',
    'type': 'Text Classification',
    'source': 'https://developer.ibm.com/exchanges/models/all/max-toxic-comment-classifier/',
    'license': 'Apache V2'
}
