import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { auth, db } from '../firebaseConfig';
import { createUserWithEmailAndPassword } from 'firebase/auth';
import { doc, setDoc } from 'firebase/firestore';

function Signup() {
    const [email, setEmail] = useState<string>('');
    const [password, setPassword] = useState<string>('');
    const [userId, setUserId] = useState<string>('');
    const [error, setError] = useState<string>('');
    const [showPopup, setShowPopup] = useState<boolean>(false); // Track popup visibility

    const navigate = useNavigate();

    const handleSignup = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        try {
            const userCredential = await createUserWithEmailAndPassword(auth, email, password);
            const user = userCredential.user;

            // Use the Firebase Authentication UID as the document ID
            await setDoc(doc(db, 'users', user.uid), {
                email: user.email,
                createdAt: new Date().toISOString(),
                customUserId: userId, // Store the custom user ID as part of the document
            });

            // Show success popup and redirect after a delay
            setShowPopup(true);
            setTimeout(() => navigate('/login'), 2000); // Redirect after 2 seconds
        } catch (err) {
            setError((err as Error).message); // Type casting the error
        }
    };

    return (
        <div className="min-h-screen bg-black flex flex-col items-center justify-center relative">
            <header className="text-center p-4">
                <h1 className="text-4xl font-bold text-green-300 mb-4">Sign Up</h1>
                <form
                    onSubmit={handleSignup}
                    className="flex flex-col gap-4 text-white"
                >
                    <input
                        type="text"
                        placeholder="Custom User ID"
                        value={userId}
                        onChange={(e) => setUserId(e.target.value)}
                        className="px-4 py-2 rounded bg-gray-800 text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                        required
                    />
                    <input
                        type="email"
                        placeholder="Email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="px-4 py-2 rounded bg-gray-800 text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                        required
                    />
                    <input
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="px-4 py-2 rounded bg-gray-800 text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                        required
                    />
                    <button
                        type="submit"
                        className="px-6 py-2 bg-green-500 text-white rounded hover:bg-green-600 transition"
                    >
                        Sign Up
                    </button>
                </form>
                {error && <p className="text-red-500 mt-2">{error}</p>}
            </header>

            {showPopup && (
                <div className="absolute inset-0 flex items-start justify-center bg-black bg-opacity-50">
                    <div
                        className="bg-white rounded-lg shadow-lg p-6 w-80 text-center mt-[10vh]"
                    >
                        <h2 className="text-2xl font-bold text-green-500 mb-4">Account Created!</h2>
                        <p className="text-gray-500 mt-2">Redirecting to login...</p>
                    </div>
                </div>
            )}

        </div>
    );
}

export default Signup;
