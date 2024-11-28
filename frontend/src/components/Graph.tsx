// frontend/src/components/Graph.tsx
import React from 'react';
import { Line } from 'react-chartjs-2';
import { GraphData } from '../types/simulation';

interface GraphProps {
    data: GraphData;
}

const Graph: React.FC<GraphProps> = ({ data }) => {
    const chartData = {
        labels: data.time, // Ex: [0, 0.1, 0.2, ...]
        datasets: [
            {
                label: 'Trajetória',
                data: data.positions.map((p) => p.y), // Y - posição vertical do projétil
                borderColor: 'rgba(75,192,192,1)',
                fill: false,
            },
        ],
    };

    return <Line data={chartData} />;
};

export default Graph;
