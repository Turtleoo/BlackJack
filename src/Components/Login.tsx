import { useState } from 'react';
import { useNavigate } from 'react-router-dom'; // Import useNavigate
import { auth } from '../firebaseConfig';
import { signInWithEmailAndPassword } from 'firebase/auth';

function Login() {
    const [email, setEmail] = useState<string>('');
    const [password, setPassword] = useState<string>('');
    const [error, setError] = useState<string>('');

    const navigate = useNavigate();

    const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        try {
            await signInWithEmailAndPassword(auth, email, password);
            navigate('/dashboard'); // Redirect to dashboard
        } catch (err) {
            setError((err as Error).message); // Type casting the error
        }
    };

    return (
        <div className="min-h-screen bg-black flex flex-col items-center justify-center">
            <header className="text-center p-4">
                <h1 className="text-4xl font-bold text-blue-300 mb-4">Firebase Login</h1>
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
                    <div className="flex justify-between">
                        <button
                            type="submit"
                            className="px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition"
                        >
                            Login
                        </button>
                        <button
                            type="button"
                            onClick={() => navigate('/signup')} // Navigate to sign-up page
                            className="px-6 py-2 bg-green-500 text-white rounded hover:bg-green-600 transition"
                        >
                            Sign Up
                        </button>
                    </div>
                </form>
                {error && <p className="text-red-500 mt-2">{error}</p>}
            </header>
        </div>
    );
}

export default Login;