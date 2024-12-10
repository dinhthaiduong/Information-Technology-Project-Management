from dataclasses import dataclass
from grag.prompts import PROMPT, QUERY
from grag.rag import GraphRag
from grag.utils import create_work_dir
from grag.vectrag import VectorRag
import os


@dataclass
class HybirdRag:
    def __init__(
        self,
        graph_rag: GraphRag,
        *,
        vector_model: str = "all-minilm:l6-v2",
        embed_len: int = 384,
    ) -> None:
        self.graph_rag: GraphRag = graph_rag
        self.vector_rag: VectorRag = VectorRag(
            graph_rag.work_dir, model=vector_model, embed_len=embed_len
        )

        create_work_dir(self.graph_rag.work_dir)
        if not os.path.exists(graph_rag.work_dir + "entities.parquet"):
            self.vector_rag.from_a_graph_db(graph_rag.db)

    async def chat(self, question: str) -> tuple[str, list[str]]:
        chat_res = await self.graph_rag.chat_create_entity_type(question)
        entities = self.graph_rag.get_entities_from_chat_no_filter(chat_res)

        output = []
        vector_entities: list[str] = []
        queries = []

        queries_type = []
        for entity in entities:
            if entity[0] == "entity":
                for en in self.vector_rag.query(entity[2]):
                    en_c = '"' + en.capitalize() + '"'
                    vector_entities.append(en_c)
            else:
                queries_type.append(
                    QUERY["match_type"].format(type=entity[1].capitalize())
                )

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
        # print(output)
        # print(queries, queries_type)
        print("text recive docs len: ", len(output_nearest))
        print(chat_res, entities)

        prompt = PROMPT["CHAT"].format(
            question=question, received="\n".join(output_nearest)
        )

        ans = await self.graph_rag.client.chat([{"role": "user", "content": prompt}])
        return (ans, output_nearest)

    def reload_vector_store(self):
        self.vector_rag.from_a_graph_db(self.graph_rag.db)
