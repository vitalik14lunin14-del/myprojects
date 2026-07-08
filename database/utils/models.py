from pydantic import BaseModel
from utils.hash_utils import hash_sha256

class Article(BaseModel):
    id: int
    title: str
    content: str

    def get_masked_data(self) -> dict:
        return {
            "id": hash_sha256(str(self.id)),
            "content": hash_sha256(self.content)
        }