import re
from ollama import Client as Ollama

from openai import OpenAI
from .prompts import PROMPT, QUERY
import os
import json
from neo4j import Driver, GraphDatabase
from .utils import RagMode, extract_verbs, get_index_or

regrex_input = re.compile(r"\[(.*)\]", re.DOTALL)


def vaild_entity(entity: list[str]) -> bool:
    if len(entity) < 3:
        return False
    if entity[0] == "relationship" and len(entity) < 4:
        return False

    return True


class ModelAddapter:
    def __init__(self, model: str, *, host: str = "http://localhost:11434") -> None:
        provider, model = model.split("/")
        self.provider: str = provider
        self.model: str = model
        if provider == "ollama":
            self.client: OpenAI | Ollama = Ollama(host)
        elif provider == "openai":
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        else:
            raise ValueError("invaid provider")

    def chat(self, text: str, *, stream: bool = False) -> str:
        if self.provider == "ollama":
            chat_res = self.client.chat(
                model=self.model,
                messages=[{"role": "user", "content": text}],
                stream=stream,
            )
            return chat_res.message.content or ""
        elif self.provider == "openai":
            chat_res = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": text}],
                stream=stream,
            )

            return chat_res.choices[0].message.content or ""
        return ""


def hashing_entity(entity: list[str]) -> str:
    if entity[0] == "relationship":
        return str(hash(entity[1] + entity[2] + entity[3]))
    return str(hash(entity[2]))


def is_entity(entity: list[str]) -> bool:
    return entity[0] == "entity"


def is_relationship(entity: list[str]) -> bool:
    return entity[0] == "relationship"


def save_to_dict_concat(entities_vk: dict[str, list[str]], entity: list[str]):
    hash_entity = hashing_entity(entity)
    if hash_entity in entities_vk:
        if is_entity(entity) and len(entity) > 3:
            entity[0] = "relationship"
            entity[1] = entity[2]
            new_hash = hashing_entity(entity)
            entities_vk[new_hash] = entity
        elif len(entity) > 4:
            entities_vk[hash_entity][3] += entity[3]
    else:
        entities_vk[hash_entity] = entity


class GraphRag:
    def __init__(
        self,
        work_dir: str,
        model: str,
        db_uri: str,
        auth: tuple[str, str],
        *,
        mode: RagMode = RagMode.QUERY,
        host: str = "http://localhost:11434",
    ) -> None:
        self.client: ModelAddapter = ModelAddapter(model=model, host=host)
        self.model: str = model
        self.work_dir: str = work_dir
        self.db: Driver = GraphDatabase.driver(db_uri, auth=auth)
        self.entities_vk: dict[str, list[str]] = dict()
        self.on_wait_entities: list[list[str]] = []
        self.lookup_exsist_db: set[str] = set()
        self.mode: RagMode = mode

        if self.mode == RagMode.QUERY:
            return

        if os.path.exists(work_dir + "kv_entity_relationship.json"):
            with open(work_dir + "kv_entity_relationship.json", "r", encoding='utf-8') as save_f:
                self.entities_vk = json.load(save_f) or {}
                save_f.close()

        if os.path.exists(self.work_dir + "saved-db.txt"):
            with open(self.work_dir + "saved-db.txt", "r") as saved_entity_f:
                self.lookup_exsist_db = set(
                    [line.strip("\n") for line in saved_entity_f.readlines()]
                )
                saved_entity_f.close()

    def create_entities(self, text: str) -> list[list[str]]:
        chat_res_content = self.client.chat(
            PROMPT["EXTRACT_ENTITY_RELATIONSHIP"].format(input_text=text)
        )

        entities = regrex_input.findall(chat_res_content)
        output = []

        for entity in entities:
            entity_list = entity.split("\n")
            for entity in entity_list:
                entites = re.findall(r"\((.*)\)", entity)
                for entity in entites:
                    splited = re.findall(r'"([^"]*)"', entity)
                    output.append([a for a in splited])

        return list(filter(vaild_entity, output))

    def save_entities(self, entities: list[list[str]]) -> None:
        if not os.path.exists(self.work_dir):
            os.mkdir(self.work_dir)

        entity_rela_key = open(self.work_dir + "entity_relationship_key.jsonl", "a")
        for en in entities:
            _ = entity_rela_key.write(json.dumps(en, ensure_ascii=False) + "\n")
            save_to_dict_concat(self.entities_vk, en)

        entity_rela_key.close()

    def insert(self, input: str):
        entities = self.create_entities(input)
        self.on_wait_entities.extend(entities)
        self.save_entities(entities)

    def chat(self, question: str):
        entities = self.create_entities(question)
        output = []
        for entity in entities:
            if not is_entity(entity):
                continue

            records, _, _ = self.db.execute_query(
                QUERY["match"].format(
                    e=entity[1].capitalize(),
                    id=entity[2],
                )
            )

            if len(records) == 0:
                continue
            output.append(records[0]["e.description"])

            for record in records:
                output.append(record["r.description"])
                output.append(record["e2.description"])

        prompt = PROMPT["CHAT"].format(question=question, received="\n".join(output))
        return self.client.chat(prompt)

    def recover(self):
        remover_file = open(self.work_dir + "entity_relationship_key.jsonl")
        entities: list[list[str]] = [
            json.loads(line) for line in remover_file.readlines()
        ]
        remover_file.close()

        self.on_wait_entities.extend(entities)

    def create_queries(self, entity: list[str]) -> list[str]:
        query = []
        if entity[0] == "entity":
            query.append(
                QUERY["entity"].format(
                    type=entity[1].capitalize(),
                    name=entity[2],
                    description=get_index_or(entity, 3, ""),
                )
            )

        elif entity[0] == "relationship":
            relations = extract_verbs(entity[3])

            query.append(
                QUERY["relationship"].format(
                    e1=entity[2],
                    e2=entity[1],
                    relation=relations,
                    description=get_index_or(entity, 3, ""),
                    keywords=get_index_or(entity, 4, ""),
                )
            )

        return query

    def write_to_db(self) -> int:
        query_log_file = open(self.work_dir + "query.log", "a")
        lookup_set = self.lookup_exsist_db
        new_written: list[str] = []

        count = 0
        for entity in self.on_wait_entities:
            key = hashing_entity(entity)
            if key in self.lookup_exsist_db:
                continue

            lookup_set.add(key)
            new_written.append(key)

            count += 1
            queries = self.create_queries(entity)
            for query in queries:
                _ = query_log_file.write(query)
                _ = self.db.execute_query(query)

        saved_entity = open(self.work_dir + "saved-db.txt", "a")
        for new in new_written:
            _ = saved_entity.write(new + "\n")

        saved_entity.close()

        self.on_wait_entities = []
        query_log_file.close()
        entities_vk_file = open(self.work_dir + "kv_entity_relationship.json", "w")
        json.dump(self.entities_vk, entities_vk_file, ensure_ascii=False)
        entities_vk_file.close()
        return count
