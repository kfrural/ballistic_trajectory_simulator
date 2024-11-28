import React, { useState } from 'react';
import { SimulationData } from '../types/simulation';

interface InputFormProps {
    onSubmit: (inputs: SimulationData) => void;
}

const InputForm: React.FC<InputFormProps> = ({ onSubmit }) => {
    const [velocity, setVelocity] = useState<string>('0');
    const [angle, setAngle] = useState<string>('0');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSubmit({
            velocity: parseFloat(velocity),
            angle: parseFloat(angle),
        });
    };

    return (
        <form onSubmit={handleSubmit}>
            <input
                type="number"
                placeholder="Velocidade (m/s)"
                value={velocity}
                onChange={(e) => setVelocity(e.target.value)}
            />
            <input
                type="number"
                placeholder="Ângulo (°)"
                value={angle}
                onChange={(e) => setAngle(e.target.value)}
            />
            <button type="submit">Simular</button>
        </form>
    );
};

export default InputForm;
