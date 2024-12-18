from accelerate.utils import tqdm
from grag.hybridrag import HybirdRag
from grag.rag import GraphRag
from grag.utils import RagMode, batchs
from grag.vectrag import VectorRag


class RagAsync:
    def __init__(
        self, work_dir: str, model: str, db_uri: str, db_auth: tuple[str, str]
    ) -> None:
        self.graph_rag: GraphRag = GraphRag(
            work_dir,
            model,
            db_uri=db_uri,
            db_auth=db_auth,
            mode=RagMode.Create,
        )
        self.vector_rag: VectorRag = VectorRag(work_dir, save_file="docrag.parquet")
        self.hybrid_rag: HybirdRag = HybirdRag(self.graph_rag, self.vector_rag)
        self.on_updated: bool = False

    async def insert(self, chunks: list[str], async_client: int = 4) -> None:
        self.on_updated = True
        total_batchs = list(batchs(chunks, async_client))
        for idx, chunk in enumerate(tqdm(total_batchs)):
            _ = await self.hybrid_rag.insert(chunk, batch=async_client + 1)

            inserted = self.hybrid_rag.graph_rag.write_to_db()
            self.hybrid_rag.doc_rag.save()
            print("Insert ", str(inserted), " value")

    async def chat(self, input: str) -> tuple[str, list[str]]:
        return await self.hybrid_rag.chat(input)

    def update_db(self):
        self.hybrid_rag.reload_vector_store()
        self.hybrid_rag.doc_rag.save()
        self.hybrid_rag.labels_rag.save()
