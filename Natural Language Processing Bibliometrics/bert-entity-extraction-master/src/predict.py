import numpy as np
import os
import joblib
import torch
import pandas as pd

import config
import dataset
import engine
from model import EntityModel
from itertools import chain


if __name__ == "__main__":

    meta_data = joblib.load("meta.bin")
    enc_pos = meta_data["enc_pos"]
    enc_tag = meta_data["enc_tag"]

    num_pos = len(list(enc_pos.classes_))
    num_tag = len(list(enc_tag.classes_))

    device = torch.device("cuda")
    model = EntityModel(num_tag=num_tag, num_pos=num_pos)
    model.load_state_dict(torch.load(config.MODEL_PATH))
    model.to(device)

    sentence = """
       Of the 11 demographic/biological variables examined, evidence for consistent positive associations were found for employment
       status and home ownership ( those who were employed and those who owned their own home had higher levels of overall walking ).
       """
    tokenized_sentence = config.TOKENIZER.encode(sentence)

    sentence = sentence.split()
    print(sentence)
    print(tokenized_sentence)

    test_dataset = dataset.EntityDataset(
        texts=[sentence],
        pos=[[0] * len(sentence)],
        tags=[[0] * len(sentence)]
    )

    with torch.no_grad():
        data = test_dataset[0]
        for k, v in data.items():
            data[k] = v.to(device).unsqueeze(0)
        tag, pos, _ = model(**data)

        print(
            enc_tag.inverse_transform(
                tag.argmax(2).cpu().numpy().reshape(-1)
            )[:len(tokenized_sentence)]
        )
        print(
            enc_pos.inverse_transform(
                pos.argmax(2).cpu().numpy().reshape(-1)
            )[:len(tokenized_sentence)]
        )


    def flatten(listOfLists):
        "Flatten one level of nesting"
        return list(chain.from_iterable(listOfLists))

    def predict_labels(doc):
        labels = []
        tags = []
        sentenceid = []
        pos_tags = []
        for count, value in enumerate(dict.fromkeys(doc["Sentence #"])):
            subset = doc.iloc[doc.index[doc["Sentence #"] == value]]
            sentence = " ".join(str(item) for item in subset['Word'])
            tokenized_sentence = config.TOKENIZER.encode(sentence)
            input_ids = torch.tensor([tokenized_sentence]).cuda()
            tokens = tokenizer.convert_ids_to_tokens(input_ids.to('cpu').numpy()[0])
            sentence = sentence.split()
            test_dataset = dataset.EntityDataset(
                texts=[sentence],
                pos=[[0] * len(sentence)],
                tags=[[0] * len(sentence)]
            )

            with torch.no_grad():
                data = test_dataset[0]
                for k, v in data.items():
                    data[k] = v.to(device).unsqueeze(0)
                tag, pos, _ = model(**data)
                pred_tags = enc_tag.inverse_transform(
                        tag.argmax(2).cpu().numpy().reshape(-1)
                        )[1:len(tokenized_sentence)-1]
                tags.append(pred_tags)
                pred_pos = enc_pos.inverse_transform(
                        pos.argmax(2).cpu().numpy().reshape(-1)
                    )[1:len(tokenized_sentence)-1]
                pos_tags.append(pred_pos)
            labels.append(sentence)
            sentenceid.append([value] * len(pred_pos))
            print(len(sentence), len(pred_pos), len(pred_tags))
            print(sentence)
            print(pred_tags)
        # return pd.DataFrame({'Sentence': flatten(sentenceid), 'Word': flatten(labels), 'Tag': flatten(tags), 'POS': flatten(pos_tags)})
        return pd.DataFrame({'Sentence': flatten(sentenceid), 'Tag': flatten(tags), 'POS': flatten(pos_tags)})




    os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Literature\WOS_ModalChoice_Ref\CrossrefResults")
    listOfFiles = os.listdir(path=os.path.join(os.getcwd(), "xml_csvs"))
    for file in listOfFiles:
        doc_txt = pd.read_csv(os.path.join(os.getcwd(), ("xml_csvs/" + file)), encoding="latin1")
        d = predict_labels(doc_txt)
        print(d)
        d.to_csv(os.path.join(os.getcwd(), ("predict_labeled/" + file)), index=False)