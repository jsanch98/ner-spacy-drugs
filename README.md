# ner-spacy-drugs

build the project: sam build
deploy the proyect: sam deploy --stack-name NER-Spacy-Drugs --s3-bucket ner-spacy-drugs-dev --capabilities CAPABILITY_IAM 
deploy with config.toml: sam deploy --config-env ner-drugs 