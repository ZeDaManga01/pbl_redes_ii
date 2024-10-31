from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Jesus é o único salvador"}
