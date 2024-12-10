import pygame
import requests
import os
import math

# Initialize PyGame
pygame.init()

# Constants
CARD_WIDTH, CARD_HEIGHT = 100, 150
SMALL_CARD_WIDTH, SMALL_CARD_HEIGHT = 75, 100
SCREEN_WIDTH, SCREEN_HEIGHT = 1250, 800
SIDEBAR_WIDTH = 200
BACKGROUND_COLOR = (34, 139, 34)
FONT_COLOR = (255, 255, 255)
BUTTON_COLOR = (0, 0, 0)
BUTTON_HOVER_COLOR = (50, 50, 50)
BUTTON_TEXT_COLOR = (255, 255, 255)
SIDEBAR_COLOR = (100, 100, 100)

# PyGame setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Blackjack Game")
font = pygame.font.Font(None, 36)
game_over_font = pygame.font.Font(None, 30)  # Smaller font for "Game Over"
hand_label_font = pygame.font.Font(None, 28)  # Smaller font for hand labels in game over

# Deck of Cards API Base URL
API_BASE_URL = "https://deckofcardsapi.com/api/deck"

# --- Blackjack Strategy Table ---
BASIC_STRATEGY = {
    # Hard Totals
    (5): {2: 'H', 3: 'H', 4: 'H', 5: 'H', 6: 'H', 7: 'H', 8: 'H', 9: 'H', 10: 'H', 'A': 'H'},
    (6): {2: 'H', 3: 'H', 4: 'H', 5: 'H', 6: 'H', 7: 'H', 8: 'H', 9: 'H', 10: 'H', 'A': 'H'},
    (7): {2: 'H', 3: 'H', 4: 'H', 5: 'H', 6: 'H', 7: 'H', 8: 'H', 9: 'H', 10: 'H', 'A': 'H'},
    (8): {2: 'H', 3: 'H', 4: 'H', 5: 'H', 6: 'H', 7: 'H', 8: 'H', 9: 'H', 10: 'H', 'A': 'H'},
    (9): {2: 'H', 3: 'D', 4: 'D', 5: 'D', 6: 'D', 7: 'H', 8: 'H', 9: 'H', 10: 'H', 'A': 'H'},
    (10): {2: 'D', 3: 'D', 4: 'D', 5: 'D', 6: 'D', 7: 'D', 8: 'D', 9: 'D', 10: 'H', 'A': 'H'},
    (11): {2: 'D', 3: 'D', 4: 'D', 5: 'D', 6: 'D', 7: 'D', 8: 'D', 9: 'D', 10: 'D', 'A': 'H'},
    (12): {2: 'H', 3: 'H', 4: 'S', 5: 'S', 6: 'S', 7: 'H', 8: 'H', 9: 'H', 10: 'H', 'A': 'H'},
    (13): {2: 'S', 3: 'S', 4: 'S', 5: 'S', 6: 'S', 7: 'H', 8: 'H', 9: 'H', 10: 'H', 'A': 'H'},
    (14): {2: 'S', 3: 'S', 4: 'S', 5: 'S', 6: 'S', 7: 'H', 8: 'H', 9: 'H', 10: 'H', 'A': 'H'},
    (15): {2: 'S', 3: 'S', 4: 'S', 5: 'S', 6: 'S', 7: 'H', 8: 'H', 9: 'H', 10: 'H', 'A': 'H'},
    (16): {2: 'S', 3: 'S', 4: 'S', 5: 'S', 6: 'S', 7: 'H', 8: 'H', 9: 'H', 10: 'H', 'A': 'H'},
    (17): {2: 'S', 3: 'S', 4: 'S', 5: 'S', 6: 'S', 7: 'S', 8: 'S', 9: 'S', 10: 'S', 'A': 'S'},
    (18): {2: 'S', 3: 'S', 4: 'S', 5: 'S', 6: 'S', 7: 'S', 8: 'S', 9: 'S', 10: 'S', 'A': 'S'},
    (19): {2: 'S', 3: 'S', 4: 'S', 5: 'S', 6: 'S', 7: 'S', 8: 'S', 9: 'S', 10: 'S', 'A': 'S'},
    (20): {2: 'S', 3: 'S', 4: 'S', 5: 'S', 6: 'S', 7: 'S', 8: 'S', 9: 'S', 10: 'S', 'A': 'S'},
    (21): {2: 'S', 3: 'S', 4: 'S', 5: 'S', 6: 'S', 7: 'S', 8: 'S', 9: 'S', 10: 'S', 'A': 'S'},

    # Soft Totals
    ('A', 2): {2: 'H', 3: 'H', 4: 'H', 5: 'D', 6: 'D', 7: 'H', 8: 'H', 9: 'H', 10: 'H', 'A': 'H'},
    ('A', 3): {2: 'H', 3: 'H', 4: 'H', 5: 'D', 6: 'D', 7: 'H', 8: 'H', 9: 'H', 10: 'H', 'A': 'H'},
    ('A', 4): {2: 'H', 3: 'H', 4: 'D', 5: 'D', 6: 'D', 7: 'H', 8: 'H', 9: 'H', 10: 'H', 'A': 'H'},
    ('A', 5): {2: 'H', 3: 'H', 4: 'D', 5: 'D', 6: 'D', 7: 'H', 8: 'H', 9: 'H', 10: 'H', 'A': 'H'},
    ('A', 6): {2: 'H', 3: 'D', 4: 'D', 5: 'D', 6: 'D', 7: 'H', 8: 'H', 9: 'H', 10: 'H', 'A': 'H'},
    ('A', 7): {2: 'S', 3: 'Ds', 4: 'Ds', 5: 'Ds', 6: 'Ds', 7: 'S', 8: 'S', 9: 'H', 10: 'H', 'A': 'H'},
    ('A', 8): {2: 'S', 3: 'S', 4: 'S', 5: 'S', 6: 'S', 7: 'S', 8: 'S', 9: 'S', 10: 'S', 'A': 'S'},
    ('A', 9): {2: 'S', 3: 'S', 4: 'S', 5: 'S', 6: 'S', 7: 'S', 8: 'S', 9: 'S', 10: 'S', 'A': 'S'},

    # Pairs
    ('A', 'A'): {2: 'P', 3: 'P', 4: 'P', 5: 'P', 6: 'P', 7: 'P', 8: 'P', 9: 'P', 10: 'P', 'A': 'P'},
    (2, 2): {2: 'P', 3: 'P', 4: 'P', 5: 'P', 6: 'P', 7: 'P', 8: 'H', 9: 'H', 10: 'H', 'A': 'H'},
    (3, 3): {2: 'P', 3: 'P', 4: 'P', 5: 'P', 6: 'P', 7: 'P', 8: 'H', 9: 'H', 10: 'H', 'A': 'H'},
    (4, 4): {2: 'H', 3: 'H', 4: 'H', 5: 'P', 6: 'P', 7: 'H', 8: 'H', 9: 'H', 10: 'H', 'A': 'H'},
    (5, 5): {2: 'D', 3: 'D', 4: 'D', 5: 'D', 6: 'D', 7: 'D', 8: 'D', 9: 'D', 10: 'H', 'A': 'H'},
    (6, 6): {2: 'P', 3: 'P', 4: 'P', 5: 'P', 6: 'P', 7: 'H', 8: 'H', 9: 'H', 10: 'H', 'A': 'H'},
    (7, 7): {2: 'P', 3: 'P', 4: 'P', 5: 'P', 6: 'P', 7: 'P', 8: 'H', 9: 'H', 10: 'H', 'A': 'H'},
    (8, 8): {2: 'P', 3: 'P', 4: 'P', 5: 'P', 6: 'P', 7: 'P', 8: 'P', 9: 'P', 10: 'P', 'A': 'P'},
    (9, 9): {2: 'P', 3: 'P', 4: 'P', 5: 'P', 6: 'P', 7: 'S', 8: 'P', 9: 'P', 10: 'S', 'A': 'S'},
    (10, 10): {2: 'S', 3: 'S', 4: 'S', 5: 'S', 6: 'S', 7: 'S', 8: 'S', 9: 'S', 10: 'S', 'A': 'S'},
}
# --- End Blackjack Strategy Table ---

# --- Helper functions ---

def download_card_image(image_url, filename):
    """Download a card image from the API."""
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
    else:
        raise Exception(f"Failed to download image from {image_url}")

def get_card_value(card):
    """Get the numerical value of a card."""
    rank = card['value']
    if rank.isdigit():
        return int(rank)
    elif rank in ('JACK', 'QUEEN', 'KING'):
        return 10
    elif rank == 'ACE':
        return 11  # Initially count Ace as 11
    return 0

def calculate_hand_value(hand):
    """Calculate the total value of a hand."""
    total = sum(get_card_value(card) for card in hand.cards)
    aces = sum(1 for card in hand.cards if card['value'] == 'ACE')

    # Adjust for Aces if necessary
    while total > 21 and aces:
        total -= 10
        aces -= 1

    return total

# --- End Helper functions ---

class Deck:
    def __init__(self):
        """Initialize the deck by shuffling via the API."""
        response = requests.get(f"{API_BASE_URL}/new/shuffle/")
        if response.status_code == 200:
            data = response.json()
            self.deck_id = data['deck_id']
        else:
            raise Exception("Failed to initialize the deck.")

    def draw_card(self):
        """Draw a card from the deck."""
        response = requests.get(f"{API_BASE_URL}/{self.deck_id}/draw/?count=1")
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                return data['cards'][0]
            else:
                return None
        else:
            raise Exception("Failed to draw a card.")

# Hand class
class Hand:
    def __init__(self):
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

    def value(self):
        return calculate_hand_value(self)

    def is_bust(self):
        return self.value() > 21
    
    def can_split(self):
        return len(self.cards) == 2 and self.cards[0]['value'] == self.cards[1]['value']

    def render(self, x, y, hidden=False, small=False):
        """Render the hand of cards."""
        card_width = SMALL_CARD_WIDTH if small else CARD_WIDTH
        card_height = SMALL_CARD_HEIGHT if small else CARD_HEIGHT

        for i, card in enumerate(self.cards):
            if hidden and i == 0:
                # Render a face-down card
                filename = "cards/back.png"
                if not os.path.exists(filename):
                    img = pygame.Surface((card_width, card_height))
                    img.fill((0, 0, 0))
                else:
                    img = pygame.image.load(filename)

            else:
                filename = f"cards/{card['code']}.png"
                if not os.path.exists(filename):
                    download_card_image(card['image'], filename)
                img = pygame.image.load(filename)

            img = pygame.transform.scale(img, (card_width, card_height))
            screen.blit(img, (x + i * (card_width // 2 if small else card_width + 10), y))

class Game:
    def __init__(self):
        self.deck = Deck()
        self.players_hands = [[] for _ in range(4)]  # Allow multiple hands per player for splitting
        self.dealer_hand = Hand()
        self.current_player = 0
        self.current_hand_index = 0
        self.running = True
        self.game_over = False
        self.player_done = [False] * 4  # Track if players have finished their turns
        self.winners = []
        self.round_end_countdown = None

    def deal_initial_cards(self):
        self.players_hands = [[Hand()] for _ in range(4)]
        self.dealer_hand = Hand()
        self.current_player = 0
        self.current_hand_index = 0
        self.player_done = [False] * 4
        self.winners = []
        self.round_end_countdown = None

        for _ in range(2):
            for i in range(4):
                self.players_hands[i][0].add_card(self.deck.draw_card())
            self.dealer_hand.add_card(self.deck.draw_card())
        self.game_over = False

    def next_hand(self):
        """Move to the next hand/player."""
        if self.current_hand_index < len(self.players_hands[self.current_player]) - 1:
            self.current_hand_index += 1
            self.reset_round_countdown()
        else:
            self.next_player()

    def next_player(self):
        """Move to the next player."""
        self.player_done[self.current_player] = True
        while True:
            self.current_player = (self.current_player + 1) % 4
            self.current_hand_index = 0
            if not self.player_done[self.current_player]:
                break
            if all(self.player_done):
                break

    def dealer_turn(self):
        """Dealer's turn logic."""
        dealer_value = self.dealer_hand.value()
        while True:
            # Get visible dealer card
            try:
                visible_dealer_card = self.dealer_hand.cards[1]['value']
                # Convert face cards to numerical values for BASIC_STRATEGY
                if visible_dealer_card in ('JACK', 'QUEEN', 'KING'):
                    visible_dealer_card = 10
                elif visible_dealer_card == 'ACE':
                    visible_dealer_card = 'A'  
            except:
                visible_dealer_card = 0

            # Use BASIC_STRATEGY for dealer's AI
            player_hand = self.dealer_hand
            action = get_best_action(player_hand, visible_dealer_card, dealer_value)
            
            if action == 'H':
                self.dealer_hand.add_card(self.deck.draw_card())
            elif action == 'S':
                break
            
            dealer_value = self.dealer_hand.value()
            
            if dealer_value >= 17 or action == 'S':  # Simplified condition, consider refining it further
                break
            if dealer_value > 21:
                break

    def determine_winners(self):
        """Determine the winner(s) based on hand values."""
        dealer_value = self.dealer_hand.value()
        self.winners = []
        tie_players = []  # Store players who tie with the dealer

        for i, player_hands in enumerate(self.players_hands):
            player_wins = False  # Track if any of the player's hands win
            for hand in player_hands:
                player_value = hand.value()
                if player_value > 21:
                    continue  # Hand is busted, goes to next hand
                elif dealer_value > 21:
                    player_wins = True  # Dealer busted, player hand wins
                elif player_value > dealer_value:
                    player_wins = True
                elif player_value == dealer_value:
                    tie_players.append(i)  # Player ties with the dealer
            
            if player_wins:
                self.winners.append(i)

        # If any player ties with the dealer, handle the tie condition
        if tie_players and not self.winners:  # Only handle ties if no outright winner
            if dealer_value <= 21:
                self.winners = ["dealer"] + tie_players
            else:
                self.winners = tie_players

        elif not self.winners and dealer_value <= 21:
            self.winners = ["dealer"]
                
    def handle_events(self):
        """Handle user input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and not self.game_over and not self.player_done[self.current_player]:
                current_hand = self.players_hands[self.current_player][self.current_hand_index]
                if event.key == pygame.K_h:  # Hit
                    current_hand.add_card(self.deck.draw_card())
                    self.reset_round_countdown()
                    if current_hand.is_bust():
                        self.next_hand()
                elif event.key == pygame.K_s:  # Stand
                    self.next_hand()
                elif event.key == pygame.K_d and len(current_hand.cards) == 2:  # Double Down
                    current_hand.add_card(self.deck.draw_card())
                    self.next_hand()
                elif event.key == pygame.K_p and current_hand.can_split():  # Split
                    new_hand = Hand()
                    new_hand.add_card(current_hand.cards.pop())
                    self.players_hands[self.current_player].insert(self.current_hand_index + 1, new_hand)
                    # Deal one card to each split hand
                    current_hand.add_card(self.deck.draw_card())
                    new_hand.add_card(self.deck.draw_card())
                    self.reset_round_countdown()
                    if current_hand.cards[0]['value'] == 'ACE': #Check if it is a split ace then no more cards
                        self.next_hand()

            # Handle restart button click
            if event.type == pygame.MOUSEBUTTONDOWN and self.game_over:
                if SCREEN_WIDTH - SIDEBAR_WIDTH + 25 <= event.pos[0] <= SCREEN_WIDTH - SIDEBAR_WIDTH + 175 and SCREEN_HEIGHT - 75 <= event.pos[1] <= SCREEN_HEIGHT - 25:
                    self.deal_initial_cards()

    def render_button(self):
        """Render the restart button."""
        x = SCREEN_WIDTH - SIDEBAR_WIDTH + 25
        y = SCREEN_HEIGHT - 75
        mouse_pos = pygame.mouse.get_pos()
        color = (
            BUTTON_HOVER_COLOR
            if x <= mouse_pos[0] <= x + 150 and y <= mouse_pos[1] <= y + 50
            else BUTTON_COLOR
        )
        pygame.draw.rect(screen, color, (x, y, 150, 50))
        button_text = font.render("Restart", True, BUTTON_TEXT_COLOR)
        text_rect = button_text.get_rect(center=(x + 75, y + 25))
        screen.blit(button_text, text_rect)

    def render_sidebar(self):
        """Render the sidebar with game information."""
        sidebar_rect = pygame.Rect(
            SCREEN_WIDTH - SIDEBAR_WIDTH, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT
        )
        pygame.draw.rect(screen, SIDEBAR_COLOR, sidebar_rect)

        y_offset = 20

        if self.game_over:
            game_over_label = game_over_font.render("Game Over", True, FONT_COLOR)
            game_over_label_rect = game_over_label.get_rect(
                center=(SCREEN_WIDTH - SIDEBAR_WIDTH // 2, y_offset + 20)
            )
            screen.blit(game_over_label, game_over_label_rect)
            y_offset += 60

            title_text = font.render("Game Info", True, FONT_COLOR)
            title_rect = title_text.get_rect(
                center=(SCREEN_WIDTH - SIDEBAR_WIDTH // 2, y_offset)
            )
            screen.blit(title_text, title_rect)
            y_offset += 40

            if self.winners:
                if "dealer" in self.winners:
                    if len(self.winners) > 1:
                        winners_text = font.render("Tie!", True, FONT_COLOR)
                        winners_text_rect = winners_text.get_rect(
                            center=(SCREEN_WIDTH - SIDEBAR_WIDTH // 2, y_offset)
                        )
                        screen.blit(winners_text, winners_text_rect)
                        y_offset += 30
                        dealer_text = font.render("Dealer", True, FONT_COLOR)
                        dealer_text_rect = dealer_text.get_rect(
                            center=(SCREEN_WIDTH - SIDEBAR_WIDTH // 2, y_offset)
                        )
                        screen.blit(dealer_text, dealer_text_rect)
                        y_offset += 30

                        for winner in self.winners:
                            if winner != "dealer":
                                winner_text = font.render(
                                    f"& Player {winner+1}", True, FONT_COLOR
                                )
                                winner_text_rect = winner_text.get_rect(
                                    center=(
                                        SCREEN_WIDTH - SIDEBAR_WIDTH // 2,
                                        y_offset,
                                    )
                                )
                                screen.blit(winner_text, winner_text_rect)
                                y_offset += 30
                    else:
                        winners_text = font.render("Dealer Wins!", True, FONT_COLOR)
                        winners_text_rect = winners_text.get_rect(
                            center=(SCREEN_WIDTH - SIDEBAR_WIDTH // 2, y_offset)
                        )
                        screen.blit(winners_text, winners_text_rect)
                        y_offset += 30
                else:
                    winners_text = font.render("Winners:", True, FONT_COLOR)
                    winners_text_rect = winners_text.get_rect(
                        center=(SCREEN_WIDTH - SIDEBAR_WIDTH // 2, y_offset)
                    )
                    screen.blit(winners_text, winners_text_rect)
                    y_offset += 30

                    for winner in self.winners:
                        winner_text = font.render(f"Player {winner + 1}", True, FONT_COLOR)
                        winner_text_rect = winner_text.get_rect(
                            center=(SCREEN_WIDTH - SIDEBAR_WIDTH // 2, y_offset)
                        )
                        screen.blit(winner_text, winner_text_rect)
                        y_offset += 30
            else:
                no_winners_text = font.render("No Winners", True, FONT_COLOR)
                no_winners_text_rect = no_winners_text.get_rect(
                    center=(SCREEN_WIDTH - SIDEBAR_WIDTH // 2, y_offset)
                )
                screen.blit(no_winners_text, no_winners_text_rect)
                y_offset += 30

            self.render_button()

    def render_game_over_hands(self):
        """Renders all hands (small) after the game is over, stacked vertically."""
        y_start = 40
        y_increment = 150  # Vertical spacing between hands

        # Dealer's hand
        x_dealer = 50
        dealer_label = hand_label_font.render("Dealer's Hand -", True, FONT_COLOR)
        screen.blit(dealer_label, (x_dealer, y_start))
        dealer_value_label = hand_label_font.render(
            f"{self.dealer_hand.value() if self.dealer_hand.value() <= 21 else 'Bust'}",
            True,
            FONT_COLOR,
        )
        screen.blit(
            dealer_value_label,
            (x_dealer, y_start + dealer_label.get_height() + 5),
        )
        self.dealer_hand.render(
            x_dealer,
            y_start
            + dealer_label.get_height()
            + 5
            + dealer_value_label.get_height()
            + 5,
            small=True,
        )

        # Player hands
        for i, player_hands in enumerate(self.players_hands):
            for j, hand in enumerate(player_hands):
                y = y_start + (i + 1) * y_increment + j * 75  # Adjust y for each player and hand
                if j == 0:
                    player_label = hand_label_font.render(f"Player {i + 1}'s Hand -", True, FONT_COLOR)
                else:
                    player_label = hand_label_font.render(f"Player {i + 1}'s Hand ({j + 1}) -", True, FONT_COLOR)
                screen.blit(player_label, (x_dealer, y))
                player_value_label = hand_label_font.render(f"{hand.value() if hand.value() <= 21 else 'Bust'}", True, FONT_COLOR)
                screen.blit(player_value_label, (x_dealer, y + player_label.get_height() + 5))
                hand.render(x_dealer, y + player_label.get_height() + 5 + player_value_label.get_height() + 5, small=True)

    def render(self):
        """Render the game."""
        screen.fill(BACKGROUND_COLOR)

        if not self.game_over:
            # Dealer's Hand (only show one card initially)
            dealer_label = font.render("Dealer's Hand", True, FONT_COLOR)
            screen.blit(dealer_label, (50, 50))
            self.dealer_hand.render(50, 100, hidden=True)

            # Dealer Value (only count the visible card)
            dealer_value = 0
            if self.dealer_hand.cards:
                # Count value of the second card which is the visible one
                dealer_value = get_card_value(self.dealer_hand.cards[1])

            dealer_value_label = font.render(f"Value: {dealer_value}", True, FONT_COLOR)
            screen.blit(dealer_value_label, (50, 100 + CARD_HEIGHT + 10))

            # Current Player's Hand
            current_hand = self.players_hands[self.current_player][self.current_hand_index]
            if len(self.players_hands[self.current_player]) > 1:
                player_label = font.render(f"Player {self.current_player + 1}'s Hand ({self.current_hand_index+1})", True, FONT_COLOR)
            else:
                player_label = font.render(f"Player {self.current_player + 1}'s Hand", True, FONT_COLOR)

            screen.blit(player_label, (50, 300))
            current_hand.render(50, 350)

            # Player Value
            player_value_label = font.render(f"Value: {current_hand.value()}", True, FONT_COLOR)
            screen.blit(player_value_label, (50, 350 + CARD_HEIGHT + 10))

            # Check if it is the players first turn to auto-stand the player
            if self.current_hand_index == 0 and len(current_hand.cards) == 2 and self.round_end_countdown == None:
                    self.reset_round_countdown()

            if self.round_end_countdown is not None:
                remaining_time = int(self.round_end_countdown - pygame.time.get_ticks() / 1000)
                countdown_text = font.render(f"Time Left: {remaining_time}", True, FONT_COLOR)
                countdown_rect = countdown_text.get_rect(center=(SCREEN_WIDTH - SIDEBAR_WIDTH // 2, 600))
                screen.blit(countdown_text, countdown_rect)
                if remaining_time <= 0:
                    self.next_hand()
                    self.round_end_countdown = None
        else:
            self.render_game_over_hands()

        # Render Sidebar
        self.render_sidebar()

        pygame.display.flip()

    def reset_round_countdown(self):
        self.round_end_countdown = pygame.time.get_ticks() / 1000 + 5  # 5 seconds
        
    def play(self):
        """Main game loop."""
        self.deal_initial_cards()
        while self.running:
            self.handle_events()
            self.render()

            all_players_done = all(self.player_done)
            
            if not self.game_over and all_players_done:
                # Dealer's turn and determine winners
                self.dealer_turn()
                self.determine_winners()
                self.game_over = True
                pygame.time.delay(500)  # Brief pause
            elif not self.game_over:
                current_hand = self.players_hands[self.current_player][self.current_hand_index]
                current_hand_value = current_hand.value()

                # Check if the hand value has changed
                if current_hand_value >= 21 or len(current_hand.cards) >= 5:
                    self.next_hand()  # Move to the next hand/player if necessary
                

        pygame.quit()

    def get_best_action(hand, dealer_card_value, hand_value):
        """
        Determine the best action for the player based on their hand, the dealer's up card,
        and the basic strategy table.
        """

        # Convert face cards to numerical values for BASIC_STRATEGY
        if dealer_card_value in ('JACK', 'QUEEN', 'KING'):
            dealer_card_value = 10
        elif dealer_card_value == 'ACE':
            dealer_card_value = 'A'

        # Check if the hand is a pair
        if len(hand.cards) == 2:
            card1 = hand.cards[0]['value']
            card2 = hand.cards[1]['value']
            if card1 == card2:
                # Convert face cards to numerical values for BASIC_STRATEGY
                if card1 in ('JACK', 'QUEEN', 'KING'):
                    card1 = card2 = 10
                elif card1 == 'ACE':
                    card1 = card2 = 'A'
                pair = (card1, card2)
                if pair in BASIC_STRATEGY:
                    return BASIC_STRATEGY[pair].get(dealer_card_value, 'H')

        # Check if the hand is a soft total
        if any(card['value'] == 'ACE' for card in hand.cards):
            soft_total = None
            for card in hand.cards:
                if card['value'] != 'ACE':
                    # Convert face cards to numerical values for BASIC_STRATEGY
                    if card['value'] in ('JACK', 'QUEEN', 'KING'):
                        card_value = 10
                    elif card['value'] == 'ACE':
                        card_value = 'A'
                    else:
                        card_value = card['value']

                    soft_total = ('A', int(card_value) if isinstance(card_value, int) or card_value.isdigit() else card_value)
                    break
            if soft_total in BASIC_STRATEGY:
                action = BASIC_STRATEGY[soft_total].get(dealer_card_value, 'H')
                if action == 'Ds' and len(hand.cards) != 2:
                    return 'S'  # Special case: Ds should actually be 'S' after the initial deal
                else:
                    return action

        # Hard Totals
        if hand_value in BASIC_STRATEGY:
            action = BASIC_STRATEGY[hand_value].get(dealer_card_value, 'H')
            return action
        else:
            return 'S' if hand_value >= 17 else 'H'

# Run the game
if __name__ == "__main__":
    os.makedirs("cards", exist_ok=True)  # Ensure card folder exists
    game = Game()
    game.play()
