from grag.prompts import PROMPT, QUERY
from grag.rag import GraphRag
from grag.vectrag import VectorRag
from grag.utils import get_index_or
import os


class HybirdRag:
    def __init__(
        self,
        graph_rag: GraphRag,
        *,
        vector_model: str = "all-minilm:l6-v2",
        vector_save_file: str = "entities.parquet",
    ) -> None:
        self.graph_rag: GraphRag = graph_rag
        self.vector_rag: VectorRag = VectorRag(
            graph_rag.work_dir, save_file=vector_save_file, model=vector_model
        )
        if not os.path.exists(graph_rag.work_dir + vector_save_file):
            self.vector_rag.from_a_graph_db(graph_rag.db)

    async def chat(self, question: str) -> str:
        chat_res = await self.graph_rag.chat_create_entities(question)
        entities = self.graph_rag.get_entites_from_chat_res(chat_res)

        output = []
        vector_entities: list[str] = []

        for entity in entities:
            if entity[0] != "entity":
                continue
            for en in self.vector_rag.query(entity[2]):
                en_c = '"' + en + '"'
                vector_entities.append(en_c)

        query = QUERY["match_list"].format(ids=",".join(vector_entities))
        records, _, _ = self.graph_rag.db.execute_query(query)

        output.append(records[0]["e.description"])

        for record in records:
            output.append(record["r.description"])
            output.append(record["e2.description"])

        prompt = PROMPT["CHAT"].format(question=question, received="\n".join(output))
        print(prompt)

        return await self.graph_rag.client.chat([{"role": "user", "content": prompt}])

    def reload_vector_store(self):
        self.vector_rag.from_a_graph_db(self.graph_rag.db)
