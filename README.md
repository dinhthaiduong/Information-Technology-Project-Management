# Information-Technology-Project-Management

Install all requiremene package:

pip install -r requirements.txt

Run a .py with streamlit:

streamlit run <namefile.py>


## Install all required packages:
```bash
uv sync
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
uv python eval/create_eval_data.py
uv python eval/ragcheck.py
```


