import React, { useState } from 'react';
import axios from 'axios';
import InputForm from './components/InputForm';
import Graph from './components/Graph';
import { SimulationData, GraphData } from './types/simulation';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const App: React.FC = () => {
    const [graphData, setGraphData] = useState<GraphData | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSimulation = async (inputs: SimulationData) => {
        setLoading(true);
        setError(null);
        try {
            const response = await axios.post(`${API_URL}/api/v1/simulate`, {
                v0: inputs.velocity,
                elevation: inputs.angle,
                include_drag: inputs.airResistance,
                include_wind: inputs.airResistance,
            });
            console.log('Response:', response.data);
            
            const data = response.data;
            const graphData: GraphData = {
                labels: data.points?.map((p: any) => p.time.toString()) || [],
                datasets: [
                    {
                        label: 'Posição X (m)',
                        data: data.points?.map((p: any) => ({ x: p.time, y: p.x })) || [],
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.5)',
                    },
                    {
                        label: 'Posição Y (m)',
                        data: data.points?.map((p: any) => ({ x: p.time, y: p.y })) || [],
                        borderColor: 'rgb(255, 99, 132)',
                        backgroundColor: 'rgba(255, 99, 132, 0.5)',
                    },
                ],
                maxRange: data.max_range,
                maxAltitude: data.max_altitude,
                flightTime: data.flight_time,
            };
            setGraphData(graphData);
        } catch (err: any) {
            console.error('Erro ao simular:', err);
            setError(err.response?.data?.message || err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
            <h1>Simulador de Trajetória Balística</h1>
            <p style={{ color: '#666' }}>Backend: {API_URL}</p>
            
            {error && (
                <div style={{ color: 'red', padding: '10px', background: '#ffe6e6', borderRadius: '4px', marginBottom: '10px' }}>
                    Erro: {error}
                </div>
            )}
            
            <InputForm onSubmit={handleSimulation} />
            
            {loading && <p>Calculando...</p>}
            
            {graphData && (
                <div style={{ marginTop: '20px' }}>
                    <div style={{ display: 'flex', gap: '20px', marginBottom: '20px' }}>
                        <div style={{ padding: '10px', background: '#e3f2fd', borderRadius: '4px' }}>
                            <strong>Alcance máximo:</strong> {graphData.maxRange?.toFixed(2)} m
                        </div>
                        <div style={{ padding: '10px', background: '#e8f5e9', borderRadius: '4px' }}>
                            <strong>Altitude máxima:</strong> {graphData.maxAltitude?.toFixed(2)} m
                        </div>
                        <div style={{ padding: '10px', background: '#fff3e0', borderRadius: '4px' }}>
                            <strong>Tempo de voo:</strong> {graphData.flightTime?.toFixed(2)} s
                        </div>
                    </div>
                    <Graph data={graphData} />
                </div>
            )}
        </div>
    );
};

export default App;
