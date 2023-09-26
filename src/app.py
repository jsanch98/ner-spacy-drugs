import json
import logging
import spacy

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)


def lambda_handler(event, context):
    text = json.loads(event['body'])['text']
    LOGGER.info(f'Going to process text {text}')
    trained_nlp = spacy.load("./model-best")

    doc = trained_nlp(text)

    entities = []
    for ent in doc.ents:
        entities.append(
            ent.text.lower()
        )
    unique_entities = list(set(entities))
    result = list(
        map(lambda ent: {'entity': ent, 'label': 'DRUG'}, unique_entities))

    LOGGER.info(f'result {result}')

    headers = {
        "Access-Control-Allow-Origin": "*",  # Permitir cualquier origen
        "Access-Control-Allow-Headers": "Content-Type", 
        "Access-Control-Allow-Methods": "OPTIONS, POST, GET"
    }

    return {
        "statusCode": 200,
        "headers": headers,
        "body": json.dumps({"entities": result}),
    }
