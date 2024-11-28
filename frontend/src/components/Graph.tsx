import React from 'react';
import { Line } from 'react-chartjs-2';
import { GraphData } from '../types/simulation';

interface GraphProps {
    data: GraphData;
}

const Graph: React.FC<GraphProps> = ({ data }) => {
    const chartData = {
        labels: data.time,
        datasets: [
            {
                label: 'Trajetória',
                data: data.positions.map((p) => p.y),
                borderColor: 'rgba(75,192,192,1)',
                fill: false,
            },
        ],
    };

    return <Line data={chartData} />;
};

export default Graph;
