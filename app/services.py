import math
from concurrent.futures import ThreadPoolExecutor

from app import db1, db2, app
from app.models import VectorEntity

MAX_WORKERS = app.config['MAX_WORKERS']


def insert_vector(db, data):
    result = db.vectors.insert_one(data)
    return str(result.inserted_id)


def parallel_insert_vectors(vector_entity, max_workers=MAX_WORKERS):
    chunk_size = math.ceil(len(vector_entity.vector) / max_workers)
    vector_chunks = [vector_entity.vector[i:i + chunk_size] for i in range(0, len(vector_entity.vector), chunk_size)]

    logs = []

    def task(db, chunk, rank):
        partial_entity = {
            'uuid': vector_entity.uuid,
            'vector_chunk': chunk,
            'label': vector_entity.label,
            'chunk_id': rank
        }
        db_name = "db1" if db == db1 else "db2"
        logs.append(f"Worker {rank} writing chunk to {db_name}: {chunk}")
        return insert_vector(db, partial_entity)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for i, chunk in enumerate(vector_chunks):
            db = db1 if i % 2 == 0 else db2
            futures.append(executor.submit(task, db, chunk, i))

        results = [f.result() for f in futures]

    return results, logs, max_workers


def parallel_get_vector_chunks(uuid, max_workers=MAX_WORKERS):
    def task(db):
        return list(db.vectors.find({'uuid': uuid}))

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future1 = executor.submit(task, db1)
        future2 = executor.submit(task, db2)

        chunks1 = future1.result()
        chunks2 = future2.result()

    full_vector = chunks1 + chunks2
    full_vector.sort(key=lambda x: x['chunk_id'])
    combined_vector = [item for chunk in full_vector for item in chunk['vector_chunk']]
    return combined_vector


def get_all_vectors():
    vectors1 = list(db1.vectors.find())
    vectors2 = list(db2.vectors.find())

    # Remove '_id' field and transform the data to match VectorEntity model
    for vector in vectors1 + vectors2:
        vector.pop('_id', None)

    # Combine vector chunks into a full vector
    combined_vectors = {}
    for vector in vectors1 + vectors2:
        uuid = vector['uuid']
        if uuid not in combined_vectors:
            combined_vectors[uuid] = {
                'uuid': uuid,
                'vector': [],
                'label': vector['label'],
            }
        combined_vectors[uuid]['vector'].extend(vector['vector_chunk'])

    return [VectorEntity(**v) for v in combined_vectors.values()]


def delete_vector(uuid):
    db1.vectors.delete_many({'uuid': uuid})
    db2.vectors.delete_many({'uuid': uuid})
