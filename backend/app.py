from flask import Flask, request, jsonify, send_from_directory
from backend.order_tracker import OrderTracker
from backend.in_memory_storage import InMemoryStorage

app = Flask(__name__, static_folder='../frontend')
in_memory_storage = InMemoryStorage()
order_tracker = OrderTracker(in_memory_storage)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/api/orders', methods=['POST'])
def add_order_api():
    data = request.get_json(silent=True) or {}
    required = ['order_id', 'item_name', 'quantity', 'customer_id']
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400
    try:
        order_tracker.add_order(
            data['order_id'],
            data['item_name'],
            data['quantity'],
            data['customer_id'],
            data.get('status', 'pending'),
        )
        return jsonify(order_tracker.get_order_by_id(data['order_id'])), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/orders/<string:order_id>', methods=['GET'])
def get_order_api(order_id):
    try:
        return jsonify(order_tracker.get_order_by_id(order_id)), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@app.route('/api/orders/<string:order_id>/status', methods=['PUT'])
def update_order_status_api(order_id):
    data = request.get_json(silent=True) or {}
    new_status = data.get('new_status')
    if not new_status:
        return jsonify({"error": "Missing required field: new_status"}), 400
    try:
        order_tracker.update_order_status(order_id, new_status)
        return jsonify(order_tracker.get_order_by_id(order_id)), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@app.route('/api/orders', methods=['GET'])
def list_orders_api():
    status = request.args.get('status')
    if status:
        orders = order_tracker.list_orders_by_status(status)
    else:
        orders = order_tracker.list_all_orders()
    return jsonify(orders), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
