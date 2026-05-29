from flask import Flask, request, jsonify
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'PLANT_ENTERPRISE_SECRET'

# ---------------- MOCK DB ----------------
users = []
plants = []
sensors = []

# ---------------- AUTH MIDDLEWARE ----------------
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token missing'}), 401

        try:
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except:
            return jsonify({'message': 'Token invalid'}), 401

        return f(*args, **kwargs)
    return decorated

# ---------------- AUTH ----------------
@app.route('/auth/register', methods=['POST'])
def register():
    data = request.json
    users.append(data)
    return jsonify({'message': 'User registered'})

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.json

    for u in users:
        if u['email'] == data['email']:
            token = jwt.encode({
                'user': u['email'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=6)
            }, app.config['SECRET_KEY'])

            return jsonify({'token': token})

    return jsonify({'message': 'Invalid credentials'}), 401

# ---------------- PLANTS ----------------
@app.route('/plants', methods=['GET'])
@token_required
def get_plants():
    return jsonify(plants)

@app.route('/plants', methods=['POST'])
@token_required
def add_plant():
    plants.append(request.json)
    return jsonify({'message': 'Plant added'})

@app.route('/plants/<int:plant_id>', methods=['DELETE'])
@token_required
def delete_plant(plant_id):
    global plants
    plants = [p for p in plants if p.get('id') != plant_id]
    return jsonify({'message': 'Plant deleted'})

# ---------------- SENSORS (IoT) ----------------
@app.route('/sensors/data', methods=['POST'])
def sensor_data():
    sensors.append(request.json)
    return jsonify({'message': 'Sensor data received'})

@app.route('/sensors', methods=['GET'])
@token_required
def get_sensors():
    return jsonify(sensors)

# ---------------- AI PREDICTION ----------------
@app.route('/ai/detect', methods=['POST'])
def ai_detect():
    data = request.json
    # fake AI logic
    result = 'healthy' if len(str(data)) % 2 == 0 else 'disease_detected'
    return jsonify({'result': result})

# ---------------- HEALTH ----------------
@app.route('/health')
def health():
    return jsonify({'status': 'Plant Enterprise API running'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
