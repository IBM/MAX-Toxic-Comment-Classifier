# Flask settings
DEBUG = False

# Flask-restplus settings
RESTPLUS_MASK_SWAGGER = False
SWAGGER_UI_DOC_EXPANSION = 'none'

# API metadata
API_TITLE = 'MAX Toxic Comment Classifier'
API_DESC = 'Detect 6 types of toxicity in user comments.'
API_VERSION = '1.0.1'

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
