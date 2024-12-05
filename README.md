# Information-Technology-Project-Management

Install all requiremene package:

pip install -r requirements.txt

Run a .py with streamlit:

streamlit run <namefile.py>


## Install all required packages:
```bash
uv sync
```

## Add .env file
```sh
cp env.example .env
```

## Get text embedding model:
```sh
ollama pull all-minilm:l6-v2
ollama pull llama3.2 
```

## Activate virtual enviroment:
```sh
source .venv/bin/activate
```
For Window:

```sh
.venv/bin/activate.bat
```
## Start a neo4j server
```sh
docker compose up -d
```

## Run chat ui
```bash
streamlit run main.py
```

## Run evaluation:
```sh
python eval/create_eval_data.py
python eval/ragcheck_eval.py
python eval/ragas_eval.py
```


