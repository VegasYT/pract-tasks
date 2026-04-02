from pydantic import BaseModel


class CalcQueryParams(BaseModel):
    a: float
    b: float


class CalcResponse(BaseModel):
    result: float
