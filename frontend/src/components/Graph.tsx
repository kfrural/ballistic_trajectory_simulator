import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface GraphData {
  labels?: string[];
  datasets: {
    label: string;
    data: { x: number; y: number }[];
    borderColor: string;
    backgroundColor: string;
  }[];
  maxRange?: number;
  maxAltitude?: number;
  flightTime?: number;
}

interface GraphProps {
  data: GraphData;
}

const Graph: React.FC<GraphProps> = ({ data }) => {
  if (!data || !data.datasets || data.datasets.length === 0) {
    return <div>No data available</div>;
  }

  const chartData = {
    labels: data.labels || data.datasets[0]?.data.map((p) => p.x.toFixed(1)) || [],
    datasets: data.datasets.map((ds, index) => ({
      label: ds.label,
      data: ds.data.map((p) => p.y),
      borderColor: ds.borderColor || `hsl(${index * 120}, 70%, 50%)`,
      backgroundColor: ds.backgroundColor || 'transparent',
      fill: false,
      tension: 0.1,
    })),
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Trajetória Balística',
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: 'Tempo (s)',
        },
      },
      y: {
        title: {
          display: true,
          text: 'Posição (m)',
        },
      },
    },
  };

  return (
    <div style={{ height: '400px', width: '100%' }}>
      <Line data={chartData} options={options} />
    </div>
  );
};

export default Graph;