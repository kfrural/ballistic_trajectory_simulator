# ballistic_trajectory_simulator
A web-based simulator for calculating and visualizing the trajectory of projectiles based on initial velocity, angle, and air resistance. It provides interactive charts and PDF reports for ballistic analysis.

 # Simulador de Trajetória Balística (Militar/Engenharia)

    Descrição: Um app que simula a trajetória de projéteis com base em variáveis como velocidade inicial, ângulo de disparo, e resistência do ar.
    Por que chama atenção?:
        Demonstra habilidades em física aplicada e programação.
        Útil em simulações militares ou estudos acadêmicos.
    Tecnologias:
        Front-end: React.js (com gráficos usando D3.js ou Chart.js).
        Back-end (opcional): Python (Flask) para cálculos avançados.
    Extras:
        Adicione animações para a trajetória no canvas.
        Permita salvar relatórios em PDF.


A seguir, um guia detalhado para executar o projeto do **Simulador de Trajetória Balística**:

---

### **1. Planejamento do Projeto**
**Objetivo**: Criar uma aplicação web interativa que simula a trajetória de projéteis usando equações físicas.  
**Entradas do Usuário**:
- Velocidade inicial (m/s).  
- Ângulo de disparo (graus).  
- Resistência do ar (opcional).  
- Gravidade (padrão: 9.8 m/s²).  

**Saídas**:
- Gráfico da trajetória do projétil.
- Tempo total no ar, altura máxima e alcance horizontal.
- Relatórios em PDF (opcional).  

---

### **2. Equações Fundamentais**
**Sem resistência do ar**:  
- **Posição horizontal (x)**:  
  \( x(t) = v_0 \cdot \cos(\theta) \cdot t \)  
- **Posição vertical (y)**:  
  \( y(t) = v_0 \cdot \sin(\theta) \cdot t - \frac{1}{2} \cdot g \cdot t^2 \)  

**Com resistência do ar**:  
- Mais complexas (uso de métodos numéricos como Runge-Kutta).  

**Variáveis calculadas**:
- **Altura máxima**:  
  \( H = \frac{(v_0 \cdot \sin(\theta))^2}{2g} \)  
- **Alcance máximo (R)**:  
  \( R = \frac{v_0^2 \cdot \sin(2\theta)}{g} \)  
- **Tempo total (T)**:  
  \( T = \frac{2 \cdot v_0 \cdot \sin(\theta)}{g} \)  

---

### **3. Estrutura do Projeto**
**Front-end**:  
- Framework: **React.js**.  
- Biblioteca para gráficos: **Chart.js** ou **D3.js**.  

**Back-end** (opcional):  
- Framework: **Flask** (Python).  
- Cálculos físicos, com ou sem resistência do ar.  

**Extras**:  
- Exportação de gráficos: **jsPDF** para relatórios PDF.  

---

### **4. Passo a Passo para Implementação**

#### **Front-end (React.js)**  
1. **Configuração do Projeto**:  
   ```bash
   npx create-react-app simulador-balistico
   cd simulador-balistico
   npm install chart.js jspdf
   ```

2. **Estrutura do App**:
   - **`App.js`**: Contém o formulário para entrada de dados e visualização do gráfico.
   - **`components/Graph.js`**: Renderiza o gráfico da trajetória.  

3. **Entrada de Dados**:  
   Um formulário para capturar velocidade inicial, ângulo e resistência do ar:
   ```jsx
   function InputForm({ onSubmit }) {
       const [velocity, setVelocity] = React.useState(0);
       const [angle, setAngle] = React.useState(0);

       const handleSubmit = (e) => {
           e.preventDefault();
           onSubmit({ velocity: parseFloat(velocity), angle: parseFloat(angle) });
       };

       return (
           <form onSubmit={handleSubmit}>
               <input type="number" placeholder="Velocidade (m/s)" onChange={(e) => setVelocity(e.target.value)} />
               <input type="number" placeholder="Ângulo (°)" onChange={(e) => setAngle(e.target.value)} />
               <button type="submit">Simular</button>
           </form>
       );
   }
   ```

4. **Gráficos com Chart.js**:  
   ```jsx
   import { Line } from 'react-chartjs-2';

   function Graph({ data }) {
       const chartData = {
           labels: data.time, // e.g., [0, 0.1, 0.2, ...]
           datasets: [
               {
                   label: 'Trajetória',
                   data: data.positions, // [{x: 0, y: 0}, {x: 1, y: 2}, ...]
                   borderColor: 'rgba(75,192,192,1)',
                   fill: false,
               },
           ],
       };

       return <Line data={chartData} />;
   }
   ```

#### **Back-end (Python/Flask)**  
1. **Configuração do Projeto**:  
   ```bash
   mkdir backend
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install flask
   ```

2. **API Flask**:  
   Crie um endpoint para processar os cálculos:  
   ```python
   from flask import Flask, request, jsonify
   import math

   app = Flask(__name__)

   @app.route('/simulate', methods=['POST'])
   def simulate():
       data = request.json
       v0 = data['velocity']
       angle = math.radians(data['angle'])
       g = 9.8

       positions = []
       t = 0
       while True:
           x = v0 * math.cos(angle) * t
           y = v0 * math.sin(angle) * t - 0.5 * g * t**2
           if y < 0:
               break
           positions.append({'x': x, 'y': y})
           t += 0.1

       return jsonify({'positions': positions, 'time': [i * 0.1 for i in range(len(positions))]})

   if __name__ == '__main__':
       app.run(debug=True)
   ```

#### **Integração Front-end e Back-end**  
1. **Conectar API ao Front-end**:  
   Instale Axios no front-end:  
   ```bash
   npm install axios
   ```

   Use Axios para enviar dados:  
   ```jsx
   import axios from 'axios';

   function App() {
       const [graphData, setGraphData] = React.useState(null);

       const handleSimulation = async (inputs) => {
           const response = await axios.post('http://127.0.0.1:5000/simulate', inputs);
           setGraphData(response.data);
       };

       return (
           <>
               <InputForm onSubmit={handleSimulation} />
               {graphData && <Graph data={graphData} />}
           </>
       );
   }
   ```

---

### **5. Extras e Melhorias**
- **Animações no Canvas**: Use o elemento `<canvas>` para renderizar a trajetória animada.  
- **Exportação em PDF**: Integre o `jsPDF` para exportar os gráficos gerados.  
- **Hospedagem**:
  - Front-end: **Netlify** ou **Vercel**.
  - Back-end: **Render** ou **Heroku**.

Se precisar de mais detalhes ou ajuda com partes específicas, avise! 🚀
