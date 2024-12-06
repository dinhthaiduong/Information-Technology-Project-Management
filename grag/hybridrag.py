from grag.prompts import PROMPT, QUERY
from grag.rag import GraphRag
from grag.vectrag import VectorRag
import os


class HybirdRag:
    def __init__(
        self, graph_rag: GraphRag, vector_save_file: str = "entities.quarquet"
    ) -> None:
        self.graph_rag: GraphRag = graph_rag
        self.vector_rag: VectorRag = VectorRag(
            graph_rag.work_dir, save_file=vector_save_file
        )
        if not os.path.exists(graph_rag.work_dir + vector_save_file):
            self.vector_rag.from_a_graph_db(graph_rag.db)

    def chat(self, question: str) -> str:
        entities = self.graph_rag.create_entities(question)

        output = []
        vector_entities = [
            (entity[1], self.vector_rag.query(entity[2])[0])
            for entity in entities
            if entity[0] == "entity"
        ]
        for entity in vector_entities:
            records, _, _ = self.graph_rag.db.execute_query(
                QUERY["match"].format(
                    e=entity[0].capitalize(),
                    id=entity[1],
                )
            )

            if len(records) == 0:
                continue

            output.append(records[0]["e.description"])

            for record in records:
                output.append(record["r.description"])
                output.append(record["e2.description"])

        prompt = PROMPT["CHAT"].format(question=question, received="\n".join(output))

        return self.graph_rag.client.chat(prompt)

        pass
