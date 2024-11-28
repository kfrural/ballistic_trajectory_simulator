// frontend/src/App.tsx
import React, { useState } from 'react';
import axios from 'axios';
import InputForm from './components/InputForm';
import Graph from './components/Graph';
import { SimulationData, GraphData } from './types/simulation';

const App: React.FC = () => {
    const [graphData, setGraphData] = useState<GraphData | null>(null);

    const handleSimulation = async (inputs: SimulationData) => {
        try {
            const response = await axios.post('http://127.0.0.1:5000/simulate', inputs);
            setGraphData(response.data);
        } catch (error) {
            console.error('Erro ao simular:', error);
        }
    };

    return (
        <div>
            <InputForm onSubmit={handleSimulation} />
            {graphData && <Graph data={graphData} />}
        </div>
    );
};

export default App;
