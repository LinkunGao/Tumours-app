from pydantic import BaseModel


class Masks(BaseModel):
    caseId: str
    masks: list


class Mask(BaseModel):
    caseId: str
    sliceId: int
    mask: list
