import { useState } from 'react';
import { auth } from './firebaseConfig';
import { signInWithEmailAndPassword, User } from 'firebase/auth'; // Import User type
import './index.css'; // Ensure Tailwind is imported here

function App() {
  const [email, setEmail] = useState<string>(''); // Added TypeScript typing
  const [password, setPassword] = useState<string>(''); // Added TypeScript typing
  const [error, setError] = useState<string>(''); // Added TypeScript typing
  const [user, setUser] = useState<User | null>(null); // Updated to use the User type

  const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      setUser(userCredential.user);
    } catch (err) {
      setError((err as Error).message); // Type casting the error
    }
  };

  return (
    <div className="min-h-screen bg-black flex flex-col items-center justify-center">
      <header className="text-center p-4">
        <h1 className="text-4xl font-bold text-blue-300 mb-4">Firebase Login</h1>
        {user ? (
          <p className="text-lg text-green-300">Welcome, {user.email}!</p>
        ) : (
          <>
            <form
              onSubmit={handleLogin}
              className="flex flex-col gap-4 text-white"
            >
              <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="px-4 py-2 rounded bg-gray-800 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="px-4 py-2 rounded bg-gray-800 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
              <button
                type="submit"
                className="px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition"
              >
                Login
              </button>
            </form>
            {error && <p className="text-red-500 mt-2">{error}</p>}
          </>
        )}
      </header>
    </div>
  );
}

export default App;
