from neo4j import Driver
import polars as pl
from ollama import Client
import os
import numpy as np

from grag.prompts import QUERY


class VectorRag:
    def __init__(
        self,
        work_dir: str,
        *,
        host: str = "http://localhost:11434",
        model: str = "all-minilm:l6-v2",
        embed_len: int = 384,
        save_file: str = "vector_store.parquet",
    ) -> None:
        self.work_dir: str = work_dir
        self.model: str = model
        self.client: Client = Client(host=host)
        self.save_file: str = work_dir + save_file
        self.embed_len: int = embed_len
        self.vectors: pl.DataFrame = pl.DataFrame(
            {
                "text": [],
                "embed": [],
            },
            schema={"text": pl.String, "embed": pl.Array(pl.Float64, embed_len)},
            # schema={"text": pl.String, "embed": pl.List(pl.Float64)},
        )
        if not os.path.exists(work_dir):
            os.mkdir(work_dir)

        if os.path.exists(self.save_file):
            self.vectors = pl.read_parquet(self.save_file)

    def insert(self, text: list[str]) -> None:
        res = self.client.embed(self.model, text)

        self.vectors = self.vectors.extend(
            pl.DataFrame(
                {
                    "text": text,
                    "embed": [
                        embed / np.linalg.norm(embed)
                        for embed in [np.array(embed) for embed in res.embeddings]
                    ],
                }
            )
        )

    def query(self, text: str) -> list[str]:
        embed = np.array(self.client.embed(self.model, text).embeddings)

        vector = self.vectors["embed"]
        query_df = pl.DataFrame(
            {
                "text": self.vectors["text"],
                "cosine": vector.map_elements(
                    lambda other: embed.dot(np.array(other)),  # cosine similality
                    return_dtype=pl.Float64,
                ),
            }
        ).top_k(5, by=pl.col("cosine"))
        return query_df["text"].to_list()

    def save(self) -> None:
        self.vectors.write_parquet(self.save_file)

    def from_a_graph_db(self, db: Driver):
        records, _, _ = db.execute_query(QUERY["match_all"])
        ids: list[str] = [record["n.id"] for record in records]
        self.insert(ids)
        self.save()
