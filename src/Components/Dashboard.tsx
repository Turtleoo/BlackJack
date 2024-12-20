import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { User, Flame, DollarSign, Trophy, X } from 'lucide-react';

// Dynamically import all cards from the assets/cards directory
const cardImages = import.meta.glob("../assets/cards/*.png", { eager: true });

// Mapping of card values to their respective balance increments
const cardValueMap: { [key: string]: number } = {
    ace: 1100,
    jack: 1000,
    queen: 1000,
    king: 1000,
    '2': 200,
    '3': 300,
    '4': 400,
    '5': 500,
    '6': 600,
    '7': 700,
    '8': 800,
    '9': 900,
    '10': 1000
};

const Dashboard = () => {
    const [currentCard, setCurrentCard] = useState<string | null>(null);
    const [balance, setBalance] = useState(1000);
    const [profileIcon, setProfileIcon] = useState<string | null>(null);
    const [dailyStreak, setDailyStreak] = useState(0);
    const [wins, setWins] = useState(0);
    const [losses, setLosses] = useState(0);
    const [notification, setNotification] = useState<string | null>(null);
    const navigate = useNavigate();

    useEffect(() => {
        const savedIcon = localStorage.getItem('profileIcon');
        if (savedIcon) {
            setProfileIcon(savedIcon);
        }

        const savedBalance = localStorage.getItem('balance');
        if (savedBalance) {
            setBalance(parseInt(savedBalance));
        }

        setDailyStreak(parseInt(localStorage.getItem('dailyStreak') || '0'));
        setWins(parseInt(localStorage.getItem('wins') || '0'));
        setLosses(parseInt(localStorage.getItem('losses') || '0'));
    }, []);

    const handleDrawCard = () => {
        // Extract all card image paths directly without using 'path' and exclude 'back' cards
        const cardPaths = Object.values(cardImages)
            .map((module) => (module as { default: string }).default)
            .filter((path) => !path.toLowerCase().includes('back')); // Exclude 'back' cards

        if (cardPaths.length === 0) {
            console.error("No card images found (excluding 'back' cards).");
            setNotification("Error: No cards available");
            setTimeout(() => setNotification(null), 3000);
            return;
        }

        const randomIndex = Math.floor(Math.random() * cardPaths.length);
        const drawnCard = cardPaths[randomIndex];
        setCurrentCard(drawnCard);

        console.log("Drawn Card Path:", drawnCard); // Debugging log

        // Extract the cardName from the filename based on the 'value_of_suit.png' pattern
        const cardNameMatch = drawnCard.match(/\/([^/]+)\.png$/);
        let cardName: string | undefined;

        if (cardNameMatch && cardNameMatch[1]) {
            const rawName = cardNameMatch[1];
            const splitName = rawName.split('_of_');
            if (splitName.length === 2) {
                cardName = splitName[0].toLowerCase(); // Extract the 'value' part
            } else {
                console.warn(`Filename "${rawName}" does not match the expected 'value_of_suit.png' pattern.`);
            }
        }

        console.log("Extracted Card Name:", cardName); // Debugging log

        if (!cardName) {
            console.error("Failed to parse card name from path:", drawnCard);
            setNotification("Error: Invalid card drawn");
            setTimeout(() => setNotification(null), 3000);
            return;
        }

        // Determine the balance increase based on cardName using the mapping
        const balanceIncrease = cardValueMap[cardName] || 0;

        if (balanceIncrease === 0) {
            console.warn("Unknown card name:", cardName);
            setNotification("Error: Unknown card drawn");
            setTimeout(() => setNotification(null), 3000);
            return;
        }

        // Update the balance
        setBalance(prevBalance => {
            const newBalance = prevBalance + balanceIncrease;
            localStorage.setItem('balance', newBalance.toString());
            return newBalance;
        });

        // Show notification
        setNotification(`+${balanceIncrease}`);
        setTimeout(() => setNotification(null), 3000);
    };

    const handleProfileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {
            const reader = new FileReader();
            reader.onloadend = () => {
                const base64String = reader.result as string;
                setProfileIcon(base64String);
                localStorage.setItem('profileIcon', base64String);
            };
            reader.readAsDataURL(file);
        }
    };

    return (
        <div className="min-h-screen bg-blackjack-bg flex flex-col items-center justify-start p-8 text-white relative">
            <div className="w-full max-w-4xl">
                <div className="flex justify-between items-center mb-8">
                    <h1 className="text-4xl font-bold text-blackjack-blue">Dashboard</h1>
                    <div className="flex items-center space-x-4">
                        <div className="flex items-center bg-blackjack-card rounded-full p-2">
                            <DollarSign className="text-blackjack-green mr-2" />
                            <span className="font-semibold">${balance}</span>
                        </div>
                        <div className="relative">
                            <input
                                type="file"
                                accept="image/*"
                                onChange={handleProfileUpload}
                                className="hidden"
                                id="profile-upload"
                            />
                            <label
                                htmlFor="profile-upload"
                                className="cursor-pointer"
                            >
                                {profileIcon ? (
                                    <img
                                        src={profileIcon}
                                        alt="Profile"
                                        className="w-12 h-12 rounded-full object-cover border-2 border-blackjack-blue"
                                    />
                                ) : (
                                    <div className="w-12 h-12 rounded-full bg-blackjack-card flex items-center justify-center">
                                        <User className="text-gray-400" />
                                    </div>
                                )}
                            </label>
                        </div>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                    <div className="bg-blackjack-card p-6 rounded-lg shadow-lg">
                        <h2 className="text-xl font-semibold mb-4 text-blackjack-blue">Stats</h2>
                        <div className="space-y-2">
                            <div className="flex items-center">
                                <Flame className="text-blackjack-orange mr-2" />
                                <span>Daily Streak: {dailyStreak} days</span>
                            </div>
                            <div className="flex items-center">
                                <Trophy className="text-blackjack-yellow mr-2" />
                                <span>Wins: {wins}</span>
                            </div>
                            <div className="flex items-center">
                                <X className="text-blackjack-red mr-2" />
                                <span>Losses: {losses}</span>
                            </div>
                        </div>
                    </div>

                    <div className="bg-blackjack-card p-6 rounded-lg shadow-lg flex flex-col items-center justify-center">
                        <button
                            onClick={handleDrawCard}
                            className="px-6 py-2 bg-blackjack-blue rounded-full hover:bg-blue-600 transition text-white font-semibold mb-4"
                        >
                            Draw a Card
                        </button>
                        {currentCard ? (
                            <img
                                src={currentCard}
                                alt="Playing Card"
                                className="w-32 h-48 object-contain rounded shadow-lg"
                            />
                        ) : (
                            <p className="text-gray-400">Click to draw a card!</p>
                        )}
                    </div>
                </div>

                <div className="flex justify-center">
                    <button
                        onClick={() => navigate("/game")}
                        className="px-8 py-3 bg-blackjack-green rounded-full hover:bg-green-600 transition text-white font-semibold text-lg"
                    >
                        Play Blackjack
                    </button>
                </div>
            </div>

            {notification && (
                <div className="fixed inset-0 flex items-center justify-center z-50 pointer-events-none">
                    <div className="animate-fade-in-out bg-blackjack-green text-white px-6 py-3 rounded-lg text-4xl font-bold shadow-lg">
                        {notification.startsWith('+') ? notification : `+${notification}`}
                    </div>
                </div>
            )}
        </div>
    );
};

export default Dashboard;
