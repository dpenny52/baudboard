from fastapi import FastAPI
from routers import boards, columns, cards

app = FastAPI()

app.include_router(boards.router)
app.include_router(columns.router)
app.include_router(cards.router)