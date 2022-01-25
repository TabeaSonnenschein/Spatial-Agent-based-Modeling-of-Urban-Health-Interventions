import transformers
import os

os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Literature\WOS_ModalChoice_Ref\CrossrefResults")


MAX_LEN = 128
TRAIN_BATCH_SIZE = 32
VALID_BATCH_SIZE = 8
EPOCHS = 60
BASE_MODEL_PATH = 'bert-base-cased'
MODEL_PATH = 'C:/Users/Tabea/Documents/PhD EXPANSE/Written Paper/02- Behavioural Model paper/model.bin'
TRAINING_FILE = "manually_labeled/labeled_articles_joined_IOB.csv"
TOKENIZER = transformers.BertTokenizer.from_pretrained(
    BASE_MODEL_PATH,
    do_lower_case=False
)
