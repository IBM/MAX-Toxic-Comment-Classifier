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

from maxfw.model import MAXModelWrapper

import logging
from config import DEFAULT_MODEL_PATH, LABEL_LIST, MODEL_META_DATA as model_meta

import torch
import time
import numpy as np
from pytorch_pretrained_bert.tokenization import BertTokenizer
from torch.utils.data import TensorDataset, DataLoader, SequentialSampler
from core.bert_pytorch import BertForMultiLabelSequenceClassification, InputExample, convert_examples_to_features

logger = logging.getLogger()


class ModelWrapper(MAXModelWrapper):

    MODEL_META_DATA = model_meta

    def __init__(self, path=DEFAULT_MODEL_PATH):
        """Instantiate the BERT model."""
        logger.info('Loading model from: {}...'.format(path))

        # Load the model
        # 1. set the appropriate parameters
        self.eval_batch_size = 64
        self.max_seq_length = 256
        self.do_lower_case = True

        # 2. Initialize the PyTorch model
        model_state_dict = torch.load(DEFAULT_MODEL_PATH+'pytorch_model.bin', map_location='cpu')
        self.tokenizer = BertTokenizer.from_pretrained(DEFAULT_MODEL_PATH, do_lower_case=self.do_lower_case)
        self.model = BertForMultiLabelSequenceClassification.from_pretrained(DEFAULT_MODEL_PATH,
                                                                             num_labels=len(LABEL_LIST),
                                                                             state_dict=model_state_dict)
        self.device = torch.device("cpu")
        self.model.to(self.device)

        # 3. Set the layers to evaluation mode
        self.model.eval()

        logger.info('Loaded model')

    def _pre_process(self, input):
        # Record the time spent in the prediction functions
        self.start_time = time.time()

        # Converting the input to features
        test_examples = [InputExample(guid=i, text_a=x, labels=[]) for i, x in enumerate(input)]
        test_features = convert_examples_to_features(test_examples, self.max_seq_length, self.tokenizer)

        all_input_ids = torch.tensor([f.input_ids for f in test_features], dtype=torch.long)
        all_input_mask = torch.tensor([f.input_mask for f in test_features], dtype=torch.long)
        all_segment_ids = torch.tensor([f.segment_ids for f in test_features], dtype=torch.long)

        # Turn input examples into batches
        test_data = TensorDataset(all_input_ids, all_input_mask, all_segment_ids)
        test_sampler = SequentialSampler(test_data)
        self.test_dataloader = DataLoader(test_data, sampler=test_sampler, batch_size=self.eval_batch_size)

        return test_examples

    def _post_process(self, result):
        """Convert the prediction output to the expected output."""
        # Generate the output format for every input string
        output = [{LABEL_LIST[0]: p[0],
                   LABEL_LIST[1]: p[1],
                   LABEL_LIST[2]: p[2],
                   LABEL_LIST[3]: p[3],
                   LABEL_LIST[4]: p[4],
                   LABEL_LIST[5]: p[5],
                   } for p in result]

        return output

    def _predict(self, test_examples):
        """Predict the class probabilities using the BERT model."""

        logger.info("***** Running prediction *****")
        logger.info("  Num examples = %d", len(test_examples))
        logger.info("  Batch size = %d", self.eval_batch_size)

        all_logits = None

        for step, batch in enumerate(self.test_dataloader):
            input_ids, input_mask, segment_ids = batch
            input_ids = input_ids.to(self.device)
            input_mask = input_mask.to(self.device)
            segment_ids = segment_ids.to(self.device)

            # Compute the logits
            with torch.no_grad():
                logits = self.model(input_ids, segment_ids, input_mask)
                logits = logits.sigmoid()

            # Save the logits
            if all_logits is None:
                all_logits = logits.detach().cpu().numpy()
            else:
                all_logits = np.concatenate((all_logits, logits.detach().cpu().numpy()), axis=0)

        # Return the predictions
        logger.info(f'Inference done for {len(test_examples)} examples in {time.time() - self.start_time} seconds.')
        return all_logits
