import os
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM
from neo4j import GraphDatabase

load_dotenv()

# Initialize LLM client
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")
llm = OllamaLLM(model=OLLAMA_MODEL, format="json")

# Initialize Neo4j client
NEO4J_URI = os.environ.get("NEO4J_URI")
NEO4J_USER = os.environ.get("NEO4J_USER")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD")

neo4j_driver = None
if NEO4J_URI and NEO4J_USER and NEO4J_PASSWORD:
    neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def get_neo4j_session(**kwargs):
    """Get a Neo4j session for graph database operations."""
    if neo4j_driver is None:
        raise RuntimeError(
            "Neo4j driver is not configured. Check NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD."
        )
    return neo4j_driver.session(**kwargs)


def get_db_session():
    """Lazy import and get a database session to avoid eager connection at import time."""
    from app.core.database import SessionLocal
    return SessionLocal()


def get_db_engine():
    """Lazy import and get the database engine to avoid eager connection at import time."""
    from app.core.database import engine
    return engine
