from pydantic import BaseModel


class ProxyModel(BaseModel):
    host: str
    port: int

    def __str__(self):
        return f"{self.host}:{self.port}"