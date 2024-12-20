import React, { useState, useEffect } from "react";

// Card and PlayerHand interfaces
interface Card {
    value: string;
    suit: string;
}

interface PlayerHand {
    cards: Card[];
    id: number;
}

// Dynamically import all card images from the assets directory
const cardImages = import.meta.glob("../assets/cards/*.png", { eager: true });

const Game: React.FC = () => {
    const suits = ["hearts", "diamonds", "clubs", "spades"];
    const ranks = [
        "Ace",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "Jack",
        "Queen",
        "King",
    ];

    // Game setup states
    const [numPlayers, setNumPlayers] = useState<number>(1);
    const [difficulty, setDifficulty] = useState<string>("easy");
    const [numDecks, setNumDecks] = useState<number>(1);

    // Game states
    const [dealerHand, setDealerHand] = useState<Card[]>([]);
    const [playerHands, setPlayerHands] = useState<PlayerHand[]>([]);
    const [currentPlayerIndex, setCurrentPlayerIndex] = useState<number>(0);
    const [showDealerCards, setShowDealerCards] = useState<boolean>(false);
    const [deck, setDeck] = useState<Card[]>([]);
    const [gameStarted, setGameStarted] = useState<boolean>(false);
    const [showResultsModal, setShowResultsModal] = useState<boolean>(false);
    const [resultsMessage, setResultsMessage] = useState<string>("");
    const [playerBustStatus, setPlayerBustStatus] = useState<boolean[]>([]); // Track if each player is busted
    const [playerStands, setPlayerStands] = useState<boolean[]>([]);

    useEffect(() => {
        // Create initial deck(s) when component mounts or numDecks changes
        setDeck(createDeck(numDecks));
    }, [numDecks]);

    function createDeck(decks: number): Card[] {
        let newDeck: Card[] = [];
        for (let d = 0; d < decks; d++) {
            suits.forEach((suit) => {
                ranks.forEach((value) => {
                    newDeck.push({ value, suit });
                });
            });
        }
        return shuffleDeck(newDeck);
    }

    function shuffleDeck(deck: Card[]): Card[] {
        const newDeck = [...deck];
        for (let i = newDeck.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [newDeck[i], newDeck[j]] = [newDeck[j], newDeck[i]];
        }
        return newDeck;
    }

    function dealCard(): Card {
        if (deck.length === 0) {
            // Reshuffle the deck if it's empty
            const newDeck = createDeck(numDecks);
            setDeck(newDeck);
            alert("Deck reshuffled!");
            return newDeck.pop()!;
        } else {
            const card = deck.pop();
            return card!;
        }
    }

    function calculateHandValue(hand: Card[]): number {
        let value = 0;
        let aces = 0;
        hand.forEach((card) => {
            if (["Jack", "Queen", "King"].includes(card.value)) {
                value += 10;
            } else if (card.value === "Ace") {
                value += 11;
                aces += 1;
            } else {
                value += parseInt(card.value, 10);
            }
        });
        while (value > 21 && aces > 0) {
            value -= 10;
            aces -= 1;
        }
        return value;
    }

    function startGame() {
        // Create player hands
        const initialPlayers: PlayerHand[] = [];
        for (let i = 1; i <= numPlayers; i++) {
            initialPlayers.push({ cards: [], id: i });
        }
        setPlayerHands(initialPlayers);

        // Reset bust status for each player
        setPlayerBustStatus(new Array(numPlayers).fill(false));
        setPlayerStands(new Array(numPlayers).fill(false));

        // Fresh deck
        const newDeck = createDeck(numDecks);
        setDeck(newDeck);

        setTimeout(() => {
            // Deal initial hands after deck is set
            const d1 = dealCard();
            const d2 = dealCard();
            setDealerHand([d1, d2]);

            const initialPlayerHands = initialPlayers.map((player) => ({
                ...player,
                cards: [dealCard(), dealCard()],
            }));
            setPlayerHands(initialPlayerHands);
            setShowDealerCards(false);
            setCurrentPlayerIndex(0);
            setGameStarted(true);
        }, 100);
    }

    function hit() {
        const newPlayerHands = [...playerHands];
        const card = dealCard();
        newPlayerHands[currentPlayerIndex].cards.push(card);
        setPlayerHands(newPlayerHands);

        const handValue = calculateHandValue(
            newPlayerHands[currentPlayerIndex].cards
        );
        if (handValue > 21) {
            // Update player bust status
            const newBustStatus = [...playerBustStatus];
            newBustStatus[currentPlayerIndex] = true;
            setPlayerBustStatus(newBustStatus);
            nextPlayer();
        }
    }

    function stand() {
        const newPlayerStands = [...playerStands];
        newPlayerStands[currentPlayerIndex] = true;
        setPlayerStands(newPlayerStands);
        nextPlayer();
    }

    function getDealerHitThreshold(): number {
        switch (difficulty) {
            case "medium":
                return 18;
            case "hard":
                return 19;
            default:
                return 17; // easy
        }
    }

    function nextPlayer() {
        if (currentPlayerIndex + 1 < playerHands.length) {
            setCurrentPlayerIndex(currentPlayerIndex + 1);
        } else {
            playDealerTurn();
        }
    }

    function playDealerTurn() {
        setShowDealerCards(true);
        const threshold = getDealerHitThreshold();
        let dealerVal = calculateHandValue(dealerHand);

        const dealToDealer = () => {
            if (dealerVal < threshold) {
                const card = dealCard();
                setDealerHand((prevHand) => {
                    const newHand = [...prevHand, card];
                    dealerVal = calculateHandValue(newHand);
                    return newHand;
                });
                setTimeout(dealToDealer, 1000); // Deal another card after a delay
            } else {
                setTimeout(() => showResults(), 1000);
            }
        };
        setTimeout(dealToDealer, 1000); // Start dealing after a delay
    }

    function showResults() {
        const dealerValue = calculateHandValue(dealerHand); // Calculate dealer's ENTIRE hand value
        let results = "";
        playerHands.forEach((player, index) => {
            const playerValue = calculateHandValue(player.cards);
            if (playerValue > 21) {
                results += `Player ${index + 1}: Busted!\n`;
            } else if (dealerValue > 21 || playerValue > dealerValue) {
                results += `Player ${index + 1}: Won!\n`;
            } else if (playerValue === dealerValue) {
                results += `Player ${index + 1}: Push!\n`;
            } else {
                results += `Player ${index + 1}: Lost!\n`;
            }
        });

        if (dealerValue > 21) {
            results += "Dealer: Busted!\n";
        } else {
            results += `Dealer: ${dealerValue}\n`; // Display dealer's final hand value
        }

        setResultsMessage(results);
        setShowResultsModal(true);
    }

    function resetGame() {
        setDealerHand([]);
        setPlayerHands([]);
        setShowDealerCards(false);
        setCurrentPlayerIndex(0);
        setDeck(createDeck(numDecks));
        setGameStarted(true);
        setShowResultsModal(false);
        setPlayerBustStatus(new Array(numPlayers).fill(false)); // Reset bust status
        setPlayerStands(new Array(numPlayers).fill(false));
        startGame();
    }

    function newTable() {
        setGameStarted(false);
        setShowResultsModal(false);
    }

    function getCardImage(card: Card): string {
        const rank = card.value.toLowerCase().replace(" ", "_");
        const suit = card.suit.toLowerCase().replace(" ", "_");
        return (
            cardImages[`../assets/cards/${rank}_of_${suit}.png`] as {
                default: string;
            }
        ).default;
    }

    const backCardImage =
        (cardImages["../assets/cards/back.png"] as { default: string })
            ?.default || "./cards/back.png";

    const tableContainerClasses =
        "relative w-full h-full flex-1 flex items-center justify-end p-8";
    const dealerPositionClasses =
        "absolute top-8 left-1/2 transform -translate-x-1/2 flex flex-col items-center";

    // Player positions: Arrange players in a horizontal row, evenly spaced
    const playerPositions: string[] = [
        "absolute top-1/4 left-1/4 transform -translate-x-1/2 flex flex-col items-center", // P1
        "absolute top-1/8 left-1/3 transform -translate-x-1/6 flex flex-col items-center", // P2
        "absolute top-1/8 right-1/3 transform -translate-x-1/2 flex flex-col items-center", // P3
        "absolute top-1/4 right-1/4 transform -translate-x-1/6 flex flex-col items-center", // P4
    ];

    return (
        <div className="min-h-screen bg-gradient-to-br from-green-700 to-green-900 text-white flex flex-col items-center relative font-sans">
            {/* Configuration Form */}
            {!gameStarted && (
                <div className="w-full max-w-md bg-white rounded-lg shadow-lg p-6 mt-10 text-gray-800">
                    <h2 className="text-2xl font-bold mb-4 text-center">
                        Game Setup
                    </h2>
                    <form
                        className="space-y-4"
                        onSubmit={(e) => {
                            e.preventDefault();
                            startGame();
                        }}
                    >
                        {/* Number of Players Dropdown */}
                        <div>
                            <label className="block font-semibold mb-1">
                                Number of Players
                            </label>
                            <select
                                value={numPlayers}
                                onChange={(e) =>
                                    setNumPlayers(parseInt(e.target.value, 10))
                                }
                                className="w-full border rounded p-2 bg-white text-gray-800"
                            >
                                {[1, 2, 3, 4].map((num) => (
                                    <option key={num} value={num}>
                                        {num}
                                    </option>
                                ))}
                            </select>
                        </div>

                        {/* Dealer Difficulty Dropdown */}
                        <div>
                            <label className="block font-semibold mb-1">
                                Dealer Difficulty
                            </label>
                            <select
                                value={difficulty}
                                onChange={(e) => setDifficulty(e.target.value)}
                                className="w-full border rounded p-2 bg-white text-gray-800"
                            >
                                <option value="easy">Easy (Dealer hits less than 17)</option>
                                <option value="medium">
                                    Medium (Dealer hits less than 18)
                                </option>
                                <option value="hard">
                                    Hard (Dealer hits less than 19)
                                </option>
                            </select>
                        </div>

                        {/* Number of Decks Dropdown */}
                        <div>
                            <label className="block font-semibold mb-1">
                                Number of Decks
                            </label>
                            <select
                                value={numDecks}
                                onChange={(e) => setNumDecks(parseInt(e.target.value, 10))}
                                className="w-full border rounded p-2 bg-white text-gray-800"
                            >
                                {[1, 2, 3].map((num) => (
                                    <option key={num} value={num}>
                                        {num}
                                    </option>
                                ))}
                            </select>
                        </div>

                        {/* Start Game Button */}
                        <button
                            type="submit"
                            className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 font-bold"
                        >
                            Start Game
                        </button>
                    </form>
                </div>
            )}

            {gameStarted && (
                <>
                    {/* Moved buttons to the bottom */}
                    <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 space-x-4 mt-6 z-10">
                        {/* Only show Hit button if it's the player's turn and they haven't busted or stood */}
                        {currentPlayerIndex < playerHands.length &&
                            !playerBustStatus[currentPlayerIndex] &&
                            !playerStands[currentPlayerIndex] && (
                                <button
                                    onClick={hit}
                                    className="px-6 py-3 bg-green-500 rounded-lg hover:bg-green-600 disabled:opacity-50 text-lg font-semibold shadow-md"
                                >
                                    Hit
                                </button>
                            )}
                        {/* Only show Stand button if it's the player's turn and they haven't busted */}
                        {currentPlayerIndex < playerHands.length &&
                            !playerBustStatus[currentPlayerIndex] && (
                                <button
                                    onClick={stand}
                                    className="px-6 py-3 bg-yellow-500 rounded-lg hover:bg-yellow-600 disabled:opacity-50 text-lg font-semibold shadow-md"
                                >
                                    Stand
                                </button>
                            )}
                    </div>

                    <div className={tableContainerClasses}>
                        {/* Dealer */}
                        <div className={dealerPositionClasses}>
                            <h2 className="text-3xl font-bold mb-4 text-center uppercase">
                                Dealer
                            </h2>
                            <div className="flex space-x-2">
                                {dealerHand.map((card, index) => (
                                    <img
                                        key={index}
                                        src={
                                            showDealerCards || index === 0
                                                ? getCardImage(card)
                                                : backCardImage
                                        }
                                        alt={`${card.value} of ${card.suit}`}
                                        className="w-20 h-32 rounded-lg shadow-xl"
                                    />
                                ))}
                            </div>
                        </div>

                        {/* Players */}
                        {playerHands.map((player, index) => (
                            <div
                                key={player.id}
                                className={`${playerPositions[index % playerPositions.length]} z-0`}
                            >
                                <h2
                                    className={`text-2xl font-bold mb-3 ${currentPlayerIndex === index ? "text-yellow-300" : ""
                                        }`}
                                >
                                    Player {index + 1}
                                </h2>
                                <div className="flex space-x-2">
                                    {player.cards.map((card, i) => (
                                        <img
                                            key={i}
                                            src={getCardImage(card)}
                                            alt={`${card.value} of ${card.suit}`}
                                            className="w-20 h-32 rounded-lg shadow-xl"
                                        />
                                    ))}
                                </div>
                                {/* Indicate that player is busted or stood */}
                                {playerBustStatus[index] && (
                                    <div className="text-lg mt-2 text-red-600">Busted</div>
                                )}
                                {playerStands[index] && (
                                    <div className="text-lg mt-2 text-yellow-600">Stood</div>
                                )}
                                {/* Indicate current player's turn */}
                                {currentPlayerIndex === index &&
                                    !playerBustStatus[index] &&
                                    !playerStands[index] && (
                                        <div className="text-lg mt-2 text-yellow-300">
                                            Your Turn
                                        </div>
                                    )}
                            </div>
                        ))}
                    </div>

                    {/* Results Modal */}
                    {showResultsModal && (
                        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full flex justify-center items-center">
                            <div className="relative p-8 border w-96 shadow-lg rounded-xl bg-white text-gray-800">
                                <h3 className="text-2xl font-bold mb-4 text-center">
                                    Game Results
                                </h3>
                                <pre className="text-center whitespace-pre-wrap">
                                    {resultsMessage}
                                </pre>
                                <div className="mt-6 flex justify-center space-x-4">
                                    <button
                                        onClick={resetGame}
                                        className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 font-semibold shadow-md"
                                    >
                                        Restart Game
                                    </button>
                                    <button
                                        onClick={newTable}
                                        className="px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 font-semibold shadow-md"
                                    >
                                        New Table
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}
                </>
            )}
        </div>
    );
};

export default Game;