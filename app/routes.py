from flask import request, jsonify, render_template, current_app

from app import app, db1, db2
from app.models import VectorEntity
from app.services import get_all_vectors, parallel_insert_vectors, delete_vector, parallel_get_vector_chunks

max_workers = app.config['MAX_WORKERS']

def get_db_status(db):
    try:
        db.command('ping')
        return "Online"
    except Exception:
        return "Offline"

@app.route('/')
def index():
    return render_template('index.html', max_workers=max_workers)

@app.route('/api/system-info', methods=['GET'])
def system_info():
    db1_status = get_db_status(db1)
    db2_status = get_db_status(db2)
    return jsonify({
        'max_workers': max_workers,
        'db1_status': db1_status,
        'db2_status': db2_status
    }), 200

@app.route('/api/set-max-workers', methods=['POST'])
def set_max_workers():
    global max_workers
    data = request.get_json()
    if 'max_workers' in data and isinstance(data['max_workers'], int):
        max_workers = data['max_workers']
        current_app.config['MAX_WORKERS'] = max_workers
        return jsonify({"max_workers": max_workers}), 200
    else:
        return jsonify({"error": "Invalid input"}), 400

@app.route('/api/vectors', methods=['GET'])
def get_vectors():
    vectors, time_taken = get_all_vectors()
    return jsonify([vector.dict() for vector in vectors], time_taken), 200

@app.route('/api/vectors', methods=['POST'])
def add_vector():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400
    vector_entity = VectorEntity(**data)
    results, logs, used_workers, time_taken = parallel_insert_vectors(vector_entity, max_workers=max_workers)
    if results:
        return jsonify({"uuid": vector_entity.uuid, "logs": logs, "used_workers": used_workers, "time_taken": time_taken}), 201
    else:
        return jsonify({"error": "Insertion failed"}), 500

@app.route('/api/vectors/<uuid>', methods=['GET'])
def get_vector(uuid):
    full_vector, time_taken = parallel_get_vector_chunks(uuid, max_workers=max_workers)
    if full_vector:
        return jsonify({"uuid": uuid, "vector": full_vector, "time_taken": time_taken}), 200
    else:
        return jsonify({"error": "Vector not found or retrieval failed"}), 404

@app.route('/api/vectors/<uuid>', methods=['DELETE'])
def remove_vector(uuid):
    delete_vector(uuid)
    return '', 204
