import { useState } from 'react';
import './index.css'; // Ensure Tailwind is imported here

function App() {
  const [counter, setCounter] = useState(0);

  const handleClick = () => {
    setCounter(prev => prev + 1);
  };

  return (
    <div className="min-h-screen bg-black flex flex-col items-center justify-center">
      <header className="text-center p-4">
        <h1 className="text-4xl font-bold text-blue-300 mb-4">
          Hello, Tailwind + React!
        </h1>
        <p className="text-gray-300">
          This is your starter boilerplate using Vite, React, and Tailwind!
        </p>
        <p className="text-lg text-gray-200 mt-4">Counter: {counter}</p>
      </header>
      <button
        className="mt-8 px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition"
        onClick={handleClick}
      >
        Click Me
      </button>
    </div>
  );
}

export default App;
