from neo4j import Driver
import polars as pl
from ollama import Client
import os
import numpy as np
from dataclasses import dataclass
from grag.prompts import QUERY


@dataclass
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
                "index": [],
                "text": [],
                "embed": [],
            },
            schema={
                "index": pl.UInt64,
                "text": pl.String,
                "embed": pl.Array(pl.Float64, embed_len),
            },
            # schema={"text": pl.String, "embed": pl.List(pl.Float64)},
        )
        if not os.path.exists(work_dir):
            os.mkdir(work_dir)

        if os.path.exists(self.save_file):
            self.vectors = pl.read_parquet(self.save_file)

    def insert(self, text: list[str] | pl.Series) -> None:
        res = self.client.embed(self.model, text)
        rows_len = self.vectors.shape[0]
        self.vectors = self.vectors.extend(
            pl.DataFrame(
                {
                    "index": pl.Series(range(rows_len, rows_len + len(text)), dtype=pl.UInt64),
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
                "index": self.vectors["index"],
                "cosine": vector.map_elements(
                    lambda other: embed.dot(np.array(other)),  # cosine similality
                    return_dtype=pl.Float64,
                ),
            }
        ).top_k(5, by=pl.col("cosine"))

        selected_text = self.vectors["text"].filter(
            self.vectors["index"].is_in(query_df["index"])
        )

        return selected_text.to_list()

    def save(self) -> None:
        self.vectors.write_parquet(self.save_file)

    def from_a_graph_db(self, db: Driver):
        records, _, _ = db.execute_query(QUERY["match_all"])
        ids: list[str] = [record["n.id"] for record in records]
        ids_series = pl.Series(ids, dtype=pl.String)
        ids_unique = ids_series.filter(
            ids_series.is_in(self.vectors["text"]).not_()
        ).to_list()

        self.insert(ids_unique)
        self.save()
