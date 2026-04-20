export interface SimulationData {
    velocity: number;
    angle: number;
    airResistance?: boolean;
}

export interface GraphData {
    labels: string[];
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