import React, { useState, useEffect } from 'react';
import axios from 'axios';

export default function ParkingForm() {
  const [day, setDay] = useState('');
  const [time, setTime] = useState('');
  const [location, setLocation] = useState('');
  const [result, setResult] = useState(null);
  const [days, setDays] = useState([]);
  const [times, setTimes] = useState([]);
  const [locations, setLocations] = useState([]);

  useEffect(() => {
    // Fetch dropdown options from Flask backend if endpoint is available
    axios.get('/api/options').then(res => {
      setDays(res.data.days);
      setTimes(res.data.times);
      setLocations(res.data.locations);
    }).catch(() => {
      // Fallback if endpoint doesn't exist
      setDays(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']);
      setTimes(['10:00', '12:00', '14:00', '16:00', '18:00']);
      setLocations(['Union Deck', 'West Deck', 'CRI Deck']);
    });
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('/predict', { day, time, location });
      setResult(response.data);
    } catch (error) {
      setResult({ error: 'Prediction failed. Check input and try again.' });
    }
  };

  return (
    <div className="max-w-md mx-auto p-4 bg-white rounded-2xl shadow-md">
      <h1 className="text-xl font-bold mb-4">🚗 Parking Availability Predictor</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block font-semibold">Day:</label>
          <select value={day} onChange={(e) => setDay(e.target.value)} className="w-full border rounded p-2">
            <option value="">Select a day</option>
            {days.map(d => <option key={d} value={d}>{d}</option>)}
          </select>
        </div>
        <div>
          <label className="block font-semibold">Time:</label>
          <input type="time" value={time} onChange={(e) => setTime(e.target.value)} className="w-full border rounded p-2" />
        </div>
        <div>
          <label className="block font-semibold">Parking Location:</label>
          <select value={location} onChange={(e) => setLocation(e.target.value)} className="w-full border rounded p-2">
            <option value="">Select a location</option>
            {locations.map(loc => <option key={loc} value={loc}>{loc}</option>)}
          </select>
        </div>
        <button type="submit" className="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600">Predict</button>
      </form>

      {result && (
        <div className="mt-6 p-4 bg-gray-100 rounded">
          {result.error ? (
            <p className="text-red-500">{result.error}</p>
          ) : (
            <>
              <p><strong>Availability:</strong> {result.availability} ({result.confidence}%)</p>
              <p><strong>Estimated Available Spaces:</strong> {result.spaces}</p>
            </>
          )}
        </div>
      )}
    </div>
  );
} 
