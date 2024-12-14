from dataclasses import dataclass

from grag.prompts import PROMPT
from grag.query import QUERY
from grag.rag import GraphRag
from grag.utils import create_work_dir, get_index_or
from grag.vectrag import VectorRag
import os

@dataclass
class HybirdRag:
    def __init__(
        self,
        graph_rag: GraphRag,
        vector_rag: VectorRag,
        *,
        vector_model: str = "all-minilm:l6-v2",
        embed_len: int = 384,
    ) -> None:
        self.graph_rag: GraphRag = graph_rag
        self.entity_rag: VectorRag = VectorRag(
            graph_rag.work_dir,
            model=vector_model,
            embed_len=embed_len,
            save_file="entites_hybird.parquet",
        )
        self.doc_rag: VectorRag = vector_rag

        create_work_dir(self.graph_rag.work_dir)
        if not os.path.exists(graph_rag.work_dir + "entites_hybird.parquet"):
            self.entity_rag.from_a_graph_db(graph_rag.db)

    # def from_prev(graph_rag: GraphRag, vector_rag: VectorRag) -> None:
    #     self.graph_rag: GraphRag = graph_rag
    #     self.entity_rag: VectorRag = VectorRag(
    #         graph_rag.work_dir, model=vector_model, embed_len=embed_len
    #     )
    #     self.doc_rag: VectorRag = vector_rag
    #
    #     create_work_dir(self.graph_rag.work_dir)
    #     if not os.path.exists(graph_rag.work_dir + "entities.parquet"):
    #         self.entity_rag.from_a_graph_db(graph_rag.db)
    #
    async def chat(self, question: str) -> tuple[str, list[str]]:
        chat_res = await self.graph_rag.chat_create_entity_type(question)
        entities = self.graph_rag.get_entities_from_chat_no_filter(chat_res)

        output: set[str] = set()
        vector_entities: list[str] = []
        vector_types: set[str] = set()
        queries = []

        for entity in entities:
            if entity[0] == "entity":
                vector_types.add(entity[1].capitalize())
                if len(entity) < 2:
                    continue
                for en in self.entity_rag.query(entity[2]):
                    en_c = '"' + en.capitalize() + '"'
                    vector_entities.append(en_c)
            else:
                if len(entity) > 2:
                    vector_types.add(entity[1].capitalize())

        queries.append(QUERY["match_list"].format(ids=",".join(vector_entities)))

        for e_type in vector_types:
            queries.append(QUERY["match_type"].format(type=e_type))

        for query in queries:
            records, _, _ = self.graph_rag.db.execute_query(query)

            if len(records) > 0:
                output.add(records[0].get("e.description", ""))

            for record in records:
                output.add(record["r.description"])
                output.add(record["e2.description"])

        # for e_type in vector_types:
        #     query = QUERY["match_type"].format(type=e_type)
        #     records, _, _ = self.graph_rag.db.execute_query(query)
        #
        #     if len(records) > 0:
        #         output.append(records[0].get("e.description", ""))
        #
        #     for record in records:
        #         output.append(record["r.description"])
        #         output.append(record["e2.description"])

        output_nearest = self.entity_rag.similality(question, list(output), 50)

        output_prompt: set[str] = set(output_nearest)
        if len(output_nearest) > 1:
            output_prompt.add(self.doc_rag.query(output_nearest[0], top_k=1)[0])

        print("text recive docs len: ", len(output_prompt))

        prompt = PROMPT["CHAT"].format(question=question, received=".".join(output_prompt))
        print(prompt)
        ans = await self.graph_rag.client.chat([{"role": "user", "content": prompt}])
        return (ans, output_nearest)

    async def insert(self, input: list[str], *, batch: int = 4) -> None:
        _ = await self.graph_rag.insert_batch(input, batch=batch)
        self.doc_rag.insert(input)

    def reload_vector_store(self):
        self.entity_rag.from_a_graph_db(self.graph_rag.db)
