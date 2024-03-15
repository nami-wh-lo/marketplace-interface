from .config import settings


def get_chunks(ids, values, limit=settings.WB_ITEMS_REFRESH_LIMIT):
    chunks_ids = [ids[i : i + limit] for i in range(0, len(ids), limit)]
    chunks_values = [values[i : i + limit] for i in range(0, len(values), limit)]
    return chunks_ids, chunks_values
