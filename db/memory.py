# emmey.py
import os
from langgraph.store.postgres import PostgresStore
from langgraph.checkpoint.postgres import PostgresSaver

DB_URI = os.environ.get("DB_URL")

# Create and enter manually
store_ctx = PostgresStore.from_conn_string(DB_URI)
store = store_ctx.__enter__()

checkpointer_ctx = PostgresSaver.from_conn_string(DB_URI)
checkpointer = checkpointer_ctx.__enter__()

__all__ = ["store", "checkpointer", "store_ctx", "checkpointer_ctx"]
