# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS  # Para lidar com CORS
import math

app = Flask(__name__)
CORS(app)  # Permite requisições de qualquer origem

@app.route('/simulate', methods=['POST'])
def simulate():
    data = request.json
    v0 = data['velocity']
    angle = math.radians(data['angle'])  # Converte o ângulo para radianos
    g = 9.8  # Gravidade (m/s²)

    # Cálculos para a trajetória
    positions = []
    t = 0
    while True:
        x = v0 * math.cos(angle) * t
        y = v0 * math.sin(angle) * t - 0.5 * g * t**2
        if y < 0:
            break
        positions.append({'x': x, 'y': y})
        t += 0.1  # Intervalo de tempo para o próximo ponto

    # Retorna os resultados da simulação
    return jsonify({'positions': positions, 'time': [i * 0.1 for i in range(len(positions))]})

if __name__ == '__main__':
    app.run(debug=True)
