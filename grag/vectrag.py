from collections.abc import Sequence
from neo4j import Driver
import polars as pl
from ollama import Client
import os
import numpy as np
from dataclasses import dataclass
from grag.prompts import QUERY
from grag.utils import create_work_dir
# from sentence_transformers import SentenceTransformer
# sentences = ["This is an example sentence", "Each sentence is converted"]
# model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')


@dataclass
class VectorRag:
    def __init__(
        self,
        work_dir: str,
        *,
        host: str = "http://localhost:11434",
        model: str = "all-minilm:l6-v2",
        save_file: str = "entities.parquet",
        embed_len: int = 384,
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
        create_work_dir(work_dir)

        if os.path.exists(self.save_file):
            self.vectors = pl.read_parquet(self.save_file)

    def insert(self, text: list[str] | pl.Series) -> None:
        res = self.client.embed(self.model, text)
        rows_len = self.vectors.shape[0]
        self.vectors = self.vectors.extend(
            pl.DataFrame(
                {
                    "index": pl.Series(
                        range(rows_len, rows_len + len(text)), dtype=pl.UInt64
                    ),
                    "text": text,
                    # "embed": res.embeddings,
                    # "embed": [np.array(embed) for embed in res.embeddings],
                    "embed": [
                        embed / np.linalg.norm(embed)
                        for embed in [np.array(embed) for embed in res.embeddings]
                    ],
                }
            )
        )

    def embed(self, text: Sequence[str]) -> Sequence[Sequence[float]]:
        return self.client.embed(self.model, text).embeddings

    def similality(
        self, text: str, corpus: Sequence[str], top_k: int = 10
    ) -> list[str]:
        corpus_embed = [np.array(embed) for embed in self.embed(corpus)]
        text_embed = np.array(self.embed([text])[0])

        return (
            pl.DataFrame(
                {
                    "text": corpus,
                    "cosine": [np.dot(text_embed, embed) for embed in corpus_embed],
                }
            )
            .top_k(top_k, by="cosine")["text"]
            .to_list()
        )

    def query(self, text: str, *,top_k: int=10) -> list[str]:
        embed = np.array(self.client.embed(self.model, text).embeddings)
        embed = embed / np.linalg.norm(embed)

        vector = self.vectors["embed"]
        query_df = pl.DataFrame(
            {
                "index": self.vectors["index"],
                "cosine": vector.map_elements(
                    lambda other: np.dot(embed, np.array(other)),  # cosine similality
                    return_dtype=pl.Float64,
                ),
            }
        ).top_k(top_k, by=pl.col("cosine"))

        selected_text = query_df.join(self.vectors, on="index").sort(
            by="cosine", descending=True
        )

        return selected_text["text"].to_list()

    def save(self) -> None:
        self.vectors.write_parquet(self.save_file)

    def from_a_graph_db(self, db: Driver):
        records, _, _ = db.execute_query(QUERY["match_all"])
        ids: list[str] = [record["n.id"] for record in records]
        ids_series = pl.Series(ids, dtype=pl.String)
        ids_unique = ids_series.filter(
            ids_series.is_in(self.vectors["text"]).not_()
        ).to_list()

        res = self.client.embed(self.model, ids_unique)

        rows_len = self.vectors.shape[0]
        self.vectors = pl.DataFrame(
            {
                "index": pl.Series(
                    range(rows_len, rows_len + len(ids_unique)), dtype=pl.UInt64
                ),
                "text": ids_unique,
                "embed": [
                    embed / np.linalg.norm(embed)
                    for embed in [np.array(embed) for embed in res.embeddings]
                ],
            }
        )
        self.save()
