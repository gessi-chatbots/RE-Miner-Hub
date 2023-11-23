# Emotion Extraction de User Reviews usant Fine-Tuned GPT Model

Aquest sistema té com a objectiu adaptar un model GPT amb fine-tuning per a la tasca d'emotion extraction en app reviews  generades per usuaris.


## Estructura de fitxers

- **main.py**: Script principal per al procés d'emotion extraction.
- **data/**
  - **complete_dataset.jsonl**: Complet dataset de reviews usat al sistema.
  - **test_dataset.jsonl**: Dataset de reviews usat per testejar el model generat.
  - **test_dataset_content.txt**: Dataset de reviews usat per testejar el model generat en format `.txt`.
  - **training_dataset.jsonl**: Dataset de reviews usat per entrenar el model generat.
- **results/**
  - **chat_completion_result.json**: Resultats obtinguts de la *Chat Completion*.
  - **fine_tuning_job_result.json**: Objecte `fine-tuning.job` creat.
  - **training_metrics.csv**: Mètriques de l'entrenament del fine-tuning.
  

## Requeriments
  - Python 3.x
  - `OPENAI_API_KEY` al fitxer .env

## Instal·lació

1.  Clonar el repositori
```console
  git clone git@github.com:irenebertolin25/OpenAI.git
  cd OpenAI
  pip install -r requirements.txt
```
2. Instal·lar les dependències
```console
  pip install -r requirements.txt
```

## Ús

1. Executar l'script main
```console
  python main.py
```
2. Comprovar els 3 fitxers generats a la carpeta `results`.