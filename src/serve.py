import uvicorn
from pydantic import BaseModel
from fastapi import FastAPI


class Item(BaseModel):
    name: str
    x: float


app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Welcome!"}


@app.post("/api/v1/predict/")
async def predict(item: Item):
    return item


if __name__ == "__main__":
    uvicorn.run("serve:app", host="0.0.0.0")
