from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from src.graphql.schema import schema

# App FastAPI
app = FastAPI(title="API con GraphQL y Firestore")

# Crear router GraphQL
graphql_app = GraphQLRouter(schema)

# Montar en FastAPI
app.include_router(graphql_app, prefix="/graphql")