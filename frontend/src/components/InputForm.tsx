import React, { useState } from 'react';
import { SimulationData } from '../types/simulation';

interface InputFormProps {
    onSubmit: (inputs: SimulationData) => void;
}

const InputForm: React.FC<InputFormProps> = ({ onSubmit }) => {
    const [velocity, setVelocity] = useState<string>('250');
    const [angle, setAngle] = useState<string>('45');
    const [airResistance, setAirResistance] = useState<boolean>(false);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSubmit({
            velocity: parseFloat(velocity),
            angle: parseFloat(angle),
            airResistance: airResistance,
        });
    };

    const inputStyle: React.CSSProperties = {
        padding: '10px',
        margin: '5px',
        borderRadius: '4px',
        border: '1px solid #ccc',
        fontSize: '16px',
    };

    const buttonStyle: React.CSSProperties = {
        padding: '10px 20px',
        margin: '5px',
        backgroundColor: '#2196F3',
        color: 'white',
        border: 'none',
        borderRadius: '4px',
        cursor: 'pointer',
        fontSize: '16px',
    };

    const labelStyle: React.CSSProperties = {
        display: 'inline-block',
        marginRight: '10px',
        fontWeight: 'bold',
    };

    return (
        <form onSubmit={handleSubmit} style={{ 
            backgroundColor: '#f5f5f5', 
            padding: '20px', 
            borderRadius: '8px',
            display: 'flex',
            flexWrap: 'wrap',
            alignItems: 'center',
            gap: '10px'
        }}>
            <div>
                <label style={labelStyle}>Velocidade (m/s):</label>
                <input
                    type="number"
                    value={velocity}
                    onChange={(e) => setVelocity(e.target.value)}
                    style={inputStyle}
                    min="0"
                    max="1000"
                />
            </div>
            
            <div>
                <label style={labelStyle}>Ângulo (°):</label>
                <input
                    type="number"
                    value={angle}
                    onChange={(e) => setAngle(e.target.value)}
                    style={inputStyle}
                    min="0"
                    max="90"
                />
            </div>
            
            <div>
                <label style={{ ...labelStyle, marginRight: '5px' }}>
                    <input
                        type="checkbox"
                        checked={airResistance}
                        onChange={(e) => setAirResistance(e.target.checked)}
                        style={{ marginRight: '5px' }}
                    />
                    Com resistência do ar
                </label>
            </div>
            
            <button type="submit" style={buttonStyle}>
                Simular
            </button>
        </form>
    );
};

export default InputForm;