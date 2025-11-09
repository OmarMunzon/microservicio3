from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from fastapi.middleware.cors import CORSMiddleware

from src.graphql.schema import schema

# App FastAPI
app = FastAPI(title="API con GraphQL y Firestore")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],    
)

# Crear router GraphQL
graphql_app = GraphQLRouter(schema)

# Montar en FastAPI
app.include_router(graphql_app, prefix="/graphql")
