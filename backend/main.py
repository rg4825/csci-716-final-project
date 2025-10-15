# file:         main.py
# description:  the main script file

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def test():
    return {"output": "hello world"}
