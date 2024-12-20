from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def index():
    return "API do Simulador está funcionando! Acesse a rota '/simulate' para simular."

@app.route('/simulate', methods=['POST'])
def simulate():
    data = request.json
    # Simulação do cálculo baseado nos dados fornecidos
    velocity = data.get('velocity')
    angle = data.get('angle')
    air_resistance = data.get('airResistance', 0)  # Valor padrão se não for fornecido

    # Exemplo de retorno com dados fictícios
    response = {
        "positions": [{"x": 0, "y": 0}, {"x": 10, "y": 5}, {"x": 20, "y": 0}],
        "time": [0, 1, 2],
    }
    return jsonify(response)

@app.route('/favicon.ico')
def favicon():
    return '', 204  # Responde com "Sem conteúdo"

# Adicione o bloco main
if __name__ == "__main__":
    app.run(debug=True)
