# Knowledge Extraction on ESG data

In this project, we aim to explore the task of relation extraction with knowledge graph for exploring the discrepancy between company reports and media coverage. The problem we aim to solve is the identification and extraction of relationships between different ESG (environmental, social, and governance) entities mentioned in textual descriptions of two types of text documents. This task can be critical for investors who want to understand what the company reports about their ESG impact and if the  media coverage sentiment aligns with their reports.

Our proposal for addressing this problem is to use a combination of natural language processing (NLP) techniques and knowledge graph construction to extract relations between different entities. We aim to leverage existing ontologies and taxonomies with our own fine-tuning to build a knowledge graph that represents the different entities and relationships. We will then use this knowledge graph to extract relations between entities mentioned in the texts.

## NER models:

https://huggingface.co/TrajanovRisto/en_ner_esg

https://huggingface.co/msr10/en_esg_ner

## Sentiment Model:

https://huggingface.co/TrajanovRisto/bert-esg

## Knowledge Extraction:

https://huggingface.co/Babelscape/rebel-large


