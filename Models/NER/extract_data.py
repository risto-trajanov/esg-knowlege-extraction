import json
import random
import os
import pandas as pd
from collections import Counter

def get_relations_from_label_studio_data(file_name:str):
    """Extracts REBEL style relation data from Labels Studio json format.

    Args:
        file_name (str): File Location of JSON file from Label Stdudio.

    Returns:
        list: List of all the relations extracted from label studio.
    """
    documents = []
    relations_my = []
    id_entity = {}
    entities = []
    triplets = []
    # Open the JSONL file for reading
    with open(file_name, 'r') as jsonl_file:
        # Iterate over the lines in the file
        data = json.load(jsonl_file)
        # print(data['annotations'])
        for item in data:
            document = {}
            print(item['id'])
            doc_id = random.randint(1, 1000000)
            document['doc_id'] = doc_id
            document['uri'] = item['id']
            text = item['data']['text']
            document['text'] = text
            title = ' '.join(text.split(' ')[:5])
            document['title'] = title

            # Parse each line as a JSON object
            for entry in item['annotations']:
                for res in entry['result']:
                    try:
                        entity = {}
                        boundaries = []
                        if res['type'] == 'labels':
                            uri = res['id']
                            value = res['value']
                            surfaceform = value['text']
                            boundaries.append(value['start'])
                            boundaries.append(value['end'])
                            entity['uri'] = uri
                            entity['surfaceform'] = surfaceform
                            entity['boundaries'] = boundaries
                            entity['annotator'] = 'Me'

                            id_entity[uri] = entity
                            entities.append(entity)

                        elif res['type'] == 'relation':
                            triplet = {}
                            from_id = res['from_id']
                            to_id = res['to_id']
                            surfaceform = res['labels'][0]
                            predicate = {}
                            uri_pred_len = min(len(from_id), len(to_id))
                            sample_list = random.sample(from_id+to_id, k=uri_pred_len)
                            # Join the list of characters into a single string
                            sample_string = ''.join(sample_list)

                            predicate['uri'] = sample_string
                            predicate['annotator'] = 'Me'
                            predicate['surfaceform'] = surfaceform
                            predicate['boundaries'] = None

                            relations_my.append(surfaceform)

                            if res['direction'] == 'right':
                                triplet['subject'] = id_entity[from_id]
                                triplet['object'] = id_entity[to_id]
                                triplet['predicate'] = predicate

                                triplets.append(triplet)
                            else:
                                print(res)
                    except Exception as e:
                        print(res)
                        print(e)
                        break
            
            document['entities'] = entities
            document['triples'] = triplets
            documents.append(document)
        return documents
       
def get_entites_from_label_studio_data(file_name:str, format:str):
    if format == 'scipy':
        return get_entites_spacy(file_name)

def get_entites_spacy(file_name):
    """Extract the entities for NER traineing from Label Studio json data format for scipy fine tuning.

    Args:
        file_name (str): JSON File location.

    Returns:
        list: Extracted entites in the format [(text, {"entities":[(start, end, label)]})]
    """
    documents = []
    # Open the JSONL file for reading
    with open(file_name, 'r', encoding='utf-8') as jsonl_file:
        # Iterate over the lines in the file
        data = json.load(jsonl_file)
        for item in data:
            text = item['data']['text']

            entities = []
            # Parse each line as a JSON object
            for entry in item['annotations']:
                for res in entry['result']:
                    try:
                        boundaries = []
                    
                        if res['type'] == 'labels':
                            value = res['value']
                            from_name = res['from_name']
                            ner = from_name.split('-')[1]
                            if ner == 'General':
                                continue
                            boundaries.append(value['start'])
                            boundaries.append(value['end'])
                            entities.append((boundaries[0], boundaries[1], ner))
                    except Exception as e:
                        print(res)
                        print(e)
                        break
            
            documents.append({'text': text, 'entities': entities})
    return documents

def get_relations(file_name:str):
    relations_my = []
    # Open the JSONL file for reading
    with open(file_name, 'r') as jsonl_file:
        # Iterate over the lines in the file
        for line in jsonl_file:
            # Parse each line as a JSON object
            # print(line)
            data = json.loads(line)

            for entry in data['triples']:
                relations_my.append(entry['predicate']['surfaceform'])

    return relations_my

def save_documents_to_jsonl(file_name:str, documents:list):
    with open(file_name, "a") as f:
        # write each object as a line in the file
        for obj in documents:
            json.dump(obj, f)
            f.write('\n')

def fix_boundaries(file_name:str):
    documents = []
    # Open the JSONL file for reading
    with open(file_name, 'r') as jsonl_file:
        # Iterate over the lines in the file
        for line in jsonl_file:
            # Parse each line as a JSON object
            data = json.loads(line)
            text = data['text']
            starting_point = 0
            entities = []
            for entry in data['entities']:
                substring = entry['surfaceform']
                
                start_index = text.find(substring)
                # if (start_index < starting_point) & (start_index != -1):
                #     temp_start = text[starting_point:].find(substring)
                #     print(temp_start)
                #     print(start_index)
                #     end_index = temp_start + len(substring)
                #     print(text[temp_start+starting_point:end_index])
                
                if start_index == -1:
                    continue
                end_index = start_index + len(substring)
                starting_point = end_index
                
                if start_index != entry['boundaries'][0]:
                    entry['boundaries'] = [start_index, end_index]
                
                entities.append(entry)

            data['entities'] = entities
            documents.append(data)
    return documents

def transform_txt_to_json(folder:str, dest_json:str):
    files = os.listdir(folder)
    for file in files:        
        if file.endswith('.txt'):
            with open(folder + file) as f:
                json_data = json.load(f)
            with open(dest_json, "a") as f:
                json.dump(json_data, f)
                f.write('\n')

def update_relations_count(relations_file:str, new_relations):
    relations_counter = Counter(new_relations)
    relations_counter_df = pd.DataFrame.from_dict(relations_counter, orient='index')
    relations_df = pd.read_csv(relations_file, header = None, sep='\t')
    relations = list(relations_df[0])
    relations_counter_df = relations_counter_df.reset_index()
    relations_counter_df.columns = ['word', 'count']
    relations_df.columns = ['word', 'count']
    relations_df_new = pd.concat([relations_counter_df, relations_df], axis=0)
    relations_df_new.to_csv(relations_file, sep='\t', header=False, index=False)