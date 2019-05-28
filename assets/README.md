# Asset Details

## Model files

The original pre-trained model files are from the [BERT](https://github.com/google-research/bert) repository, where they are available under [Apache 2.0](https://github.com/google-research/bert/blob/master/LICENSE). This pre-trained model was then finetuned on the [Toxic Comment Classification Dataset](https://www.kaggle.com/c/jigsaw-toxic-comment-classification-challenge/data).

_Note: the finetuned model files are hosted on [IBM Cloud Object Storage](http://max-assets.s3.us.cloud-object-storage.appdomain.cloud/max-toxic-comment-classifier/1.0/assets.tar.gz)._

## Test Examples

The `test_examples.csv` comma-separated-values file contains a fraction of the test set of the [Toxic Comment Classification Dataset](https://www.kaggle.com/c/jigsaw-toxic-comment-classification-challenge/data) ([CC0](https://creativecommons.org/share-your-work/public-domain/cc0/)). In the first column, the comment is listed. In the following columns, a binary value (0 or 1) indicates whether the comment is toxic, severe toxic, obscene, a threat, an insult, and/or a case of identity hate.

A json-formatted representation of the first 10 examples can be found in `test_10_examples_input.json`. The expected output was saved in `test_10_examples_output.json`.
