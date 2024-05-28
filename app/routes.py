from flask import request, jsonify, render_template, current_app

from app import app
from app.models import VectorEntity
from app.services import get_all_vectors, parallel_insert_vectors, delete_vector, parallel_get_vector_chunks


@app.route('/')
def index():
    current_app.logger.debug('Attempting to render index.html')
    return render_template('index.html')


@app.route('/api/vectors', methods=['GET'])
def get_vectors():
    vectors = get_all_vectors()
    return jsonify([vector.dict() for vector in vectors]), 200


@app.route('/api/vectors', methods=['POST'])
def add_vector():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400
    vector_entity = VectorEntity(**data)
    results = parallel_insert_vectors(vector_entity)
    if results:
        return jsonify({"uuid": vector_entity.uuid}), 201
    else:
        return jsonify({"error": "Insertion failed"}), 500


@app.route('/api/vectors/<uuid>', methods=['GET'])
def get_vector(uuid):
    full_vector = parallel_get_vector_chunks(uuid)
    if full_vector:
        return jsonify({"uuid": uuid, "vector": full_vector}), 200
    else:
        return jsonify({"error": "Vector not found or retrieval failed"}), 404


@app.route('/api/vectors/<uuid>', methods=['DELETE'])
def remove_vector(uuid):
    delete_vector(uuid)
    return '', 204
