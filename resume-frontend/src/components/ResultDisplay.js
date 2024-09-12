// src/components/ResultDisplay.js
import React from 'react';

const ResultDisplay = ({ candidate }) => {
    return (
        <div className="container mt-5">
            <h2 className="text-center">Candidate Information</h2>
            <div className="mt-4">
                <ul className="list-group">
                    <li className="list-group-item"><strong>First Name:</strong> {candidate.first_name}</li>
                    <li className="list-group-item"><strong>Email:</strong> {candidate.email}</li>
                    <li className="list-group-item"><strong>Mobile Number:</strong> {candidate.mobile_number}</li>
                </ul>
            </div>
        </div>
    );
};

export default ResultDisplay;