from dataclasses import dataclass
from grag.prompts import PROMPT, QUERY
from grag.rag import GraphRag
from grag.vectrag import VectorRag
import os

@dataclass
class HybirdRag:
    def __init__(
        self,
        graph_rag: GraphRag,
        *,
        vector_model: str = "all-minilm:l6-v2",
    ) -> None:
        self.graph_rag: GraphRag = graph_rag
        self.vector_rag: VectorRag = VectorRag(graph_rag.work_dir, model=vector_model)
        if not os.path.exists(graph_rag.work_dir + "entities.parquet"):
            self.vector_rag.from_a_graph_db(graph_rag.db)

    async def chat(self, question: str) -> tuple[str, list[str]]:
        chat_res = await self.graph_rag.chat_create_entity_type(question)
        entities = self.graph_rag.get_entites_from_chat_res(chat_res)

        output = []
        vector_entities: list[str] = []
        queries = []

        queries_type = []
        for entity in entities:
            if entity[0] == "entity":
                for en in self.vector_rag.query(entity[2]):
                    en_c = '"' + en + '"'
                    vector_entities.append(en_c)
            elif entity[0] == "type":
                queries_type.append(QUERY["match_type"].format(type=entity[1].capitalize()))

        queries.append(QUERY["match_list"].format(ids=",".join(vector_entities)))

        for query in queries:
            records, _, _ = self.graph_rag.db.execute_query(query)

            if len(records) > 0:
                output.append(records[0]["e.description"])

            for record in records:
                output.append(record["r.description"])
                output.append(record["e2.description"])

        for query in queries_type:
            records, _, _ = self.graph_rag.db.execute_query(query)

            if len(records) > 0:
                output.append(records[0].get("e.description", ""))

            for record in records:
                output.append(record["r.description"])
                output.append(record["e2.description"])

        output_nearest = self.vector_rag.similality(question, output, 50)
        print("text recide docs len: ", len(output_nearest))

        prompt = PROMPT["CHAT"].format(question=question, received="\n".join(output_nearest))

        ans = await self.graph_rag.client.chat([{"role": "user", "content": prompt}])
        print(chat_res, entities)
        return (ans, output_nearest)

    def reload_vector_store(self):
        self.vector_rag.from_a_graph_db(self.graph_rag.db)
