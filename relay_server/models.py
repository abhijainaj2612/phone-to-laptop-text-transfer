from pydantic import BaseModel, Field


class PairRequest(BaseModel):
    code: str = Field(pattern=r"^\d{6}$")


class TextRequest(BaseModel):
    text: str = Field(min_length=1)


class DeliveryAck(BaseModel):
    type: str
    message_id: str
    status: str
