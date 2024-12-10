import pygame
import requests
import os

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
hand_label_font = pygame.font.Font(None, 28) # Smaller font for hand labels in game over

# Deck of Cards API Base URL
API_BASE_URL = "https://deckofcardsapi.com/api/deck"

def download_card_image(image_url, filename):
    """Download a card image from the API."""
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
    else:
        raise Exception(f"Failed to download image from {image_url}")

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
        total = 0
        aces = 0
        for card in self.cards:
            rank = card['value']
            if rank.isdigit():
                total += int(rank)
            elif rank in ('JACK', 'QUEEN', 'KING'):
                total += 10
            elif rank == 'ACE':
                total += 11
                aces += 1
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total

    def is_bust(self):
        return self.value() > 21

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
                    img.fill((0,0,0))
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
        self.player_hands = [Hand() for _ in range(4)]  # 4 players
        self.dealer_hand = Hand()
        self.current_player = 0
        self.running = True
        self.game_over = False
        self.player_done = [False] * 4 # Track if players have finished their turns
        self.winners = []

    def deal_initial_cards(self):
        self.player_hands = [Hand() for _ in range(4)]
        self.dealer_hand = Hand()
        self.current_player = 0
        self.player_done = [False] * 4
        self.winners = []
        for _ in range(2):
            for i in range(4):
                self.player_hands[i].add_card(self.deck.draw_card())
            self.dealer_hand.add_card(self.deck.draw_card())
        self.game_over = False

    def next_player(self):
        self.player_done[self.current_player] = True
        while True:
            self.current_player = (self.current_player + 1) % 4
            if not self.player_done[self.current_player]:
                break
            if all(self.player_done):
                break;
    
    def play_dealer_turn(self):
        while self.dealer_hand.value() < 17:
            self.dealer_hand.add_card(self.deck.draw_card())

    def determine_winners(self):
        dealer_value = self.dealer_hand.value()
        player_values = [hand.value() for hand in self.player_hands]
        self.winners = []

        # Find players with 21
        players_with_21 = [i for i, value in enumerate(player_values) if value == 21]

        if players_with_21:
            if dealer_value == 21:
                self.winners = players_with_21 + ["dealer"] # Tie with dealer
            else:
                self.winners = players_with_21 # Players with 21 win
        else:
            # Find the closest to 21 without busting
            best_value = -1
            for i, value in enumerate(player_values):
                if best_value < value <= 21:
                    best_value = value

            if dealer_value > best_value and dealer_value <= 21:
                self.winners = ["dealer"]
            elif best_value > 0:
                self.winners = [i for i, value in enumerate(player_values) if value == best_value]

    def handle_events(self):
        """Handle user input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and not self.game_over and not self.player_done[self.current_player]:
                if event.key == pygame.K_h:  # Hit
                    self.player_hands[self.current_player].add_card(self.deck.draw_card())
                    if self.player_hands[self.current_player].is_bust():
                        self.next_player()
                elif event.key == pygame.K_s:  # Stand
                    self.next_player()

            # Handle restart button click
            if event.type == pygame.MOUSEBUTTONDOWN and self.game_over:
                if SCREEN_WIDTH - SIDEBAR_WIDTH + 25 <= event.pos[0] <= SCREEN_WIDTH - SIDEBAR_WIDTH + 175 and SCREEN_HEIGHT - 75 <= event.pos[1] <= SCREEN_HEIGHT - 25:
                    self.deal_initial_cards()

    def render_button(self):
        """Render the restart button."""
        x = SCREEN_WIDTH - SIDEBAR_WIDTH + 25
        y = SCREEN_HEIGHT - 75
        mouse_pos = pygame.mouse.get_pos()
        color = BUTTON_HOVER_COLOR if x <= mouse_pos[0] <= x + 150 and y <= mouse_pos[1] <= y + 50 else BUTTON_COLOR
        pygame.draw.rect(screen, color, (x, y, 150, 50))
        button_text = font.render("Restart", True, BUTTON_TEXT_COLOR)
        text_rect = button_text.get_rect(center=(x + 75, y + 25))
        screen.blit(button_text, text_rect)

    def render_sidebar(self):
        """Render the sidebar with game information."""
        sidebar_rect = pygame.Rect(SCREEN_WIDTH - SIDEBAR_WIDTH, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(screen, SIDEBAR_COLOR, sidebar_rect)

        y_offset = 20

        if self.game_over:
            game_over_label = game_over_font.render("Game Over", True, FONT_COLOR)
            game_over_label_rect = game_over_label.get_rect(center=(SCREEN_WIDTH - SIDEBAR_WIDTH // 2, y_offset + 20))
            screen.blit(game_over_label, game_over_label_rect)
            y_offset += 60
            
            title_text = font.render("Game Info", True, FONT_COLOR)
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH - SIDEBAR_WIDTH // 2, y_offset))
            screen.blit(title_text, title_rect)
            y_offset += 40
            
            if self.winners:
                if "dealer" in self.winners:
                    if len(self.winners) > 1:
                        winners_text = font.render("Tie! Dealer", True, FONT_COLOR)
                        winners_text_rect = winners_text.get_rect(center=(SCREEN_WIDTH - SIDEBAR_WIDTH // 2, y_offset))
                        screen.blit(winners_text, winners_text_rect)
                        y_offset += 30

                        for winner in self.winners:
                            if winner != "dealer":
                                winner_text = font.render(f"& Player {winner+1} Win!", True, FONT_COLOR)
                                winner_text_rect = winner_text.get_rect(center=(SCREEN_WIDTH - SIDEBAR_WIDTH // 2, y_offset))
                                screen.blit(winner_text, winner_text_rect)
                                y_offset += 30
                    else:
                        winners_text = font.render("Dealer Wins!", True, FONT_COLOR)
                        winners_text_rect = winners_text.get_rect(center=(SCREEN_WIDTH - SIDEBAR_WIDTH // 2, y_offset))
                        screen.blit(winners_text, winners_text_rect)
                        y_offset += 30
                else:
                    winners_text = font.render("Winners:", True, FONT_COLOR)
                    winners_text_rect = winners_text.get_rect(center=(SCREEN_WIDTH - SIDEBAR_WIDTH // 2, y_offset))
                    screen.blit(winners_text, winners_text_rect)
                    y_offset += 30

                    for winner in self.winners:
                        winner_text = font.render(f"Player {winner + 1}", True, FONT_COLOR)
                        winner_text_rect = winner_text.get_rect(center=(SCREEN_WIDTH - SIDEBAR_WIDTH // 2, y_offset))
                        screen.blit(winner_text, winner_text_rect)
                        y_offset += 30
            else:
                no_winners_text = font.render("No Winners", True, FONT_COLOR)
                no_winners_text_rect = no_winners_text.get_rect(center=(SCREEN_WIDTH - SIDEBAR_WIDTH // 2, y_offset))
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
        dealer_value_label = hand_label_font.render(f"{self.dealer_hand.value() if self.dealer_hand.value() <= 21 else 'Bust'}", True, FONT_COLOR)
        screen.blit(dealer_value_label, (x_dealer, y_start + dealer_label.get_height() + 5))
        self.dealer_hand.render(x_dealer, y_start + dealer_label.get_height() + 5 + dealer_value_label.get_height() + 5, small=True)

        # Player hands
        for i, hand in enumerate(self.player_hands):
            y = y_start + (i + 1) * y_increment  # Adjust y position for each player
            player_label = hand_label_font.render(f"Player {i+1}'s Hand -", True, FONT_COLOR)
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
            if self.dealer_hand.cards:  # Check if the dealer's hand is not empty
                first_card = self.dealer_hand.cards[1]
                if first_card['value'].isdigit():
                    dealer_value = int(first_card['value'])
                elif first_card['value'] in ('JACK', 'QUEEN', 'KING'):
                    dealer_value = 10
                elif first_card['value'] == 'ACE':
                    dealer_value = 11  # Initial value for Ace

            dealer_value_label = font.render(f"Value: {dealer_value}", True, FONT_COLOR)
            screen.blit(dealer_value_label, (50, 100 + CARD_HEIGHT + 10))

            # Current Player's Hand
            player_label = font.render(f"Player {self.current_player + 1}'s Hand", True, FONT_COLOR)
            screen.blit(player_label, (50, 300))
            self.player_hands[self.current_player].render(50, 350)

            # Player Value
            player_value_label = font.render(f"Value: {self.player_hands[self.current_player].value()}", True, FONT_COLOR)
            screen.blit(player_value_label, (50, 350 + CARD_HEIGHT + 10))

        # Render Sidebar
        self.render_sidebar()

        if self.game_over:
            self.render_game_over_hands()

        pygame.display.flip()

    def play(self):
        """Main game loop."""
        self.deal_initial_cards()
        while self.running:
            self.handle_events()
            self.render()
            if all(self.player_done) and not self.game_over:
                self.play_dealer_turn()
                self.determine_winners()
                self.game_over = True
        pygame.quit()

# Run the game
if __name__ == "__main__":
    os.makedirs("cards", exist_ok=True)  # Ensure card folder exists
    game = Game()
    game.play()