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
hand_label_font = pygame.font.Font(None, 28)  # Smaller font for hand labels in game over

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
            self.remaining = data['remaining']  # Track remaining cards
        else:
            raise Exception("Failed to initialize the deck.")

    def draw_card(self):
        """Draw a card from the deck."""
        if self.remaining == 0:
            return None

        response = requests.get(f"{API_BASE_URL}/{self.deck_id}/draw/?count=1")
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                self.remaining = data['remaining']  # Update remaining cards
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
            if card is None:
                continue
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
        self.player_hands = [Hand() for _ in range(4)]  # 4 players
        self.dealer_hand = Hand()
        self.current_player = 0
        self.running = True
        self.game_over = False
        self.player_done = [False] * 4  # Track if players have finished their turns
        self.winners = []
        self.tie_breaker_needed = False
        self.tie_breaker_players = []
        self.tie_breaker_active = False

    def deal_initial_cards(self):
        self.player_hands = [Hand() for _ in range(4)]
        self.dealer_hand = Hand()
        self.current_player = 0
        self.player_done = [False] * 4
        self.winners = []
        for _ in range(2):
            for i in range(4):
                card = self.deck.draw_card()
                if card:
                    self.player_hands[i].add_card(card)
            card = self.deck.draw_card()
            if card:
                self.dealer_hand.add_card(card)
        self.game_over = False
        self.tie_breaker_needed = False
        self.tie_breaker_players = []

    def next_player(self):
        if not self.tie_breaker_active:
            # Normal game
            self.player_done[self.current_player] = True
            while True:
                self.current_player = (self.current_player + 1) % 4
                if not self.player_done[self.current_player]:
                    break
                if all(self.player_done):
                    break
        else:
            # Tie-breaker round
            current_index = self.tie_breaker_players.index(self.current_player)

            # Mark the current player as done
            self.player_done[self.current_player] = True

            # Find the next player in the tie-breaker list
            next_index = (current_index + 1) % len(self.tie_breaker_players)
            self.current_player = self.tie_breaker_players[next_index]

            # Check if all players in the tie-breaker are done
            if all(self.player_done[p] for p in self.tie_breaker_players if isinstance(p, int)):
                self.tie_breaker_active = False

    def play_dealer_turn(self):
        while self.dealer_hand.value() < 17:
            card = self.deck.draw_card()
            if card:
                self.dealer_hand.add_card(card)
            else:
                break

    def determine_winners(self):
        dealer_value = self.dealer_hand.value()
        player_values = [hand.value() for hand in self.player_hands]
        self.winners = []

        # Find players with 21
        players_with_21 = [i for i, value in enumerate(player_values) if value == 21]

        if players_with_21:
            if dealer_value == 21:
                self.winners = players_with_21 + ["dealer"]  # Tie with dealer
            else:
                self.winners = players_with_21  # Players with 21 win
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

        # Check for ties
        if len(self.winners) > 1:
            self.tie_breaker_needed = True
            self.tie_breaker_players = self.winners
            if "dealer" in self.winners:
                self.tie_breaker_players = ["dealer"] + [p for p in self.winners if p != "dealer"]
            self.winners = []

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if not self.game_over:
                    # Normal game play and tie-breaker round
                    if not self.player_done[self.current_player]:
                        if event.key == pygame.K_h:
                            card = self.deck.draw_card()
                            if card:
                                self.player_hands[self.current_player].add_card(card)
                            if self.player_hands[self.current_player].is_bust():
                                self.next_player()
                        elif event.key == pygame.K_s:
                            self.next_player()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_over and self.tie_breaker_needed:
                    # Check for "Play Tiebreaker" button click
                    if SCREEN_WIDTH - SIDEBAR_WIDTH + 25 <= event.pos[0] <= SCREEN_WIDTH - SIDEBAR_WIDTH + 175 and \
                            SCREEN_HEIGHT - 125 <= event.pos[1] <= SCREEN_HEIGHT - 75:
                        self.start_tie_breaker()
                    # Check for "Restart" button click
                    elif SCREEN_WIDTH - SIDEBAR_WIDTH + 25 <= event.pos[0] <= SCREEN_WIDTH - SIDEBAR_WIDTH + 175 and \
                            SCREEN_HEIGHT - 75 <= event.pos[1] <= SCREEN_HEIGHT - 25:
                        self.deal_initial_cards()
                elif self.game_over and not self.tie_breaker_needed:
                    # Handle restart button click
                    if SCREEN_WIDTH - SIDEBAR_WIDTH + 25 <= event.pos[0] <= SCREEN_WIDTH - SIDEBAR_WIDTH + 175 and \
                            SCREEN_HEIGHT - 75 <= event.pos[1] <= SCREEN_HEIGHT - 25:
                        self.deal_initial_cards()

    def render_button(self, text, x, y, width, height):
      """Render a button."""
      mouse_pos = pygame.mouse.get_pos()
      color = BUTTON_HOVER_COLOR if x <= mouse_pos[0] <= x + width and y <= mouse_pos[1] <= y + height else BUTTON_COLOR
      pygame.draw.rect(screen, color, (x, y, width, height))
      button_text = font.render(text, True, BUTTON_TEXT_COLOR)
      text_rect = button_text.get_rect(center=(x + width // 2, y + height // 2))
      screen.blit(button_text, text_rect)

    def render_sidebar(self):
        """Render the sidebar with game information."""
        sidebar_rect = pygame.Rect(SCREEN_WIDTH - SIDEBAR_WIDTH, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(screen, SIDEBAR_COLOR, sidebar_rect)

        y_offset = 20

        if self.game_over:
            if not self.tie_breaker_needed:
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
                            winners_text_rect = winners_text.get_rect(
                                center=(SCREEN_WIDTH - SIDEBAR_WIDTH // 2, y_offset))
                            screen.blit(winners_text, winners_text_rect)
                            y_offset += 30

                            for winner in self.winners:
                                if winner != "dealer":
                                    winner_text = font.render(f"& Player {winner + 1} Win!", True, FONT_COLOR)
                                    winner_text_rect = winner_text.get_rect(
                                        center=(SCREEN_WIDTH - SIDEBAR_WIDTH // 2, y_offset))
                                    screen.blit(winner_text, winner_text_rect)
                                    y_offset += 30
                        else:
                            winners_text = font.render("Dealer Wins!", True, FONT_COLOR)
                            winners_text_rect = winners_text.get_rect(
                                center=(SCREEN_WIDTH - SIDEBAR_WIDTH // 2, y_offset))
                            screen.blit(winners_text, winners_text_rect)
                            y_offset += 30
                    else:
                        winners_text = font.render("Winners:", True, FONT_COLOR)
                        winners_text_rect = winners_text.get_rect(center=(SCREEN_WIDTH - SIDEBAR_WIDTH // 2, y_offset))
                        screen.blit(winners_text, winners_text_rect)
                        y_offset += 30

                        for winner in self.winners:
                            winner_text = font.render(f"Player {winner + 1}", True, FONT_COLOR)
                            winner_text_rect = winner_text.get_rect(
                                center=(SCREEN_WIDTH - SIDEBAR_WIDTH // 2, y_offset))
                            screen.blit(winner_text, winner_text_rect)
                            y_offset += 30
                else:
                    no_winners_text = font.render("No Winners", True, FONT_COLOR)
                    no_winners_text_rect = no_winners_text.get_rect(
                        center=(SCREEN_WIDTH - SIDEBAR_WIDTH // 2, y_offset))
                    screen.blit(no_winners_text, no_winners_text_rect)
                    y_offset += 30

                self.render_button("Restart", SCREEN_WIDTH - SIDEBAR_WIDTH + 25, SCREEN_HEIGHT - 75, 150, 50)

            else:  # Tie breaker round
                y_offset = 20
                game_over_label = game_over_font.render("Tie Breaker Round", True, FONT_COLOR)
                game_over_label_rect = game_over_label.get_rect(
                    center=(SCREEN_WIDTH - SIDEBAR_WIDTH // 2, y_offset + 20))
                screen.blit(game_over_label, game_over_label_rect)
                y_offset += 60

                players_text = font.render("Players:", True, FONT_COLOR)
                players_text_rect = players_text.get_rect(center=(SCREEN_WIDTH - SIDEBAR_WIDTH // 2, y_offset))
                screen.blit(players_text, players_text_rect)
                y_offset += 30

                for player in self.tie_breaker_players:
                    if player == "dealer":
                        player_text = font.render("Dealer", True, FONT_COLOR)
                    else:
                        player_text = font.render(f"Player {player + 1}", True, FONT_COLOR)
                    player_text_rect = player_text.get_rect(center=(SCREEN_WIDTH - SIDEBAR_WIDTH // 2, y_offset))
                    screen.blit(player_text, player_text_rect)
                    y_offset += 30

                # Render "Play Tiebreaker" and "Restart" buttons
                self.render_button("Play Tiebreaker", SCREEN_WIDTH - SIDEBAR_WIDTH + 25, SCREEN_HEIGHT - 125, 150, 50)
                self.render_button("Restart", SCREEN_WIDTH - SIDEBAR_WIDTH + 25, SCREEN_HEIGHT - 75, 150, 50)

    def render_game_over_hands(self):
        """Renders all hands (small) after the game is over, stacked vertically."""
        y_start = 40
        y_increment = 150  # Vertical spacing between hands
        x_dealer = 50  # Define x_dealer here

        # Dealer's hand
        dealer_label = hand_label_font.render("Dealer's Hand -", True, FONT_COLOR)
        screen.blit(dealer_label, (x_dealer, y_start))
        dealer_value_label = hand_label_font.render(
            f"{self.dealer_hand.value() if self.dealer_hand.value() <= 21 else 'Bust'}", True, FONT_COLOR)
        screen.blit(dealer_value_label, (x_dealer, y_start + dealer_label.get_height() + 5))
        self.dealer_hand.render(x_dealer, y_start + dealer_label.get_height() + 5 + dealer_value_label.get_height() + 5,
                                small=True)

        # Player hands
        for i, hand in enumerate(self.player_hands):
            y = y_start + (i + 1) * y_increment  # Adjust y position for each player
            player_label = hand_label_font.render(f"Player {i + 1}'s Hand -", True, FONT_COLOR)
            screen.blit(player_label, (x_dealer, y))
            player_value_label = hand_label_font.render(
                f"{hand.value() if hand.value() <= 21 else 'Bust'}", True, FONT_COLOR)
            screen.blit(player_value_label, (x_dealer, y + player_label.get_height() + 5))
            hand.render(x_dealer, y + player_label.get_height() + 5 + player_value_label.get_height() + 5, small=True)

    def render_tie_breaker_hands(self):
        """Renders only the hands of players involved in the tie breaker."""
        y_start = 40
        y_increment = 150
        x_dealer = 50  # Define x_dealer here

        if "dealer" in self.tie_breaker_players:
            dealer_label = hand_label_font.render("Dealer's Hand -", True, FONT_COLOR)
            screen.blit(dealer_label, (x_dealer, y_start))
            dealer_value_label = hand_label_font.render(
                f"{self.dealer_hand.value() if self.dealer_hand.value() <= 21 else 'Bust'}", True, FONT_COLOR)
            screen.blit(dealer_value_label, (x_dealer, y_start + dealer_label.get_height() + 5))
            self.dealer_hand.render(x_dealer, y_start + dealer_label.get_height() + 5 + dealer_value_label.get_height() + 5,
                                    small=True)

        for i, player in enumerate(self.tie_breaker_players):
            if player != "dealer":
                y = y_start + (
                    self.tie_breaker_players.index("dealer") if "dealer" in self.tie_breaker_players else 0) * y_increment + (
                            i) * y_increment
                player_label = hand_label_font.render(f"Player {player + 1}'s Hand -", True, FONT_COLOR)
                screen.blit(player_label, (x_dealer, y))
                player_value_label = hand_label_font.render(
                    f"{self.player_hands[player].value() if self.player_hands[player].value() <= 21 else 'Bust'}",
                    True, FONT_COLOR)
                screen.blit(player_value_label, (x_dealer, y + player_label.get_height() + 5))
                self.player_hands[player].render(x_dealer,
                                                 y + player_label.get_height() + 5 + player_value_label.get_height() + 5,
                                                 small=True)

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
            if not self.tie_breaker_needed:
                self.render_game_over_hands()
            else:
                self.render_tie_breaker_hands()

        pygame.display.flip()

    def start_tie_breaker(self):
        self.tie_breaker_active = True
        self.game_over = False
        self.current_player = self.tie_breaker_players[0]  # Start with the first player in the tie-breaker list
        self.player_done = [False] * 4

        # Reset all player hands
        self.player_hands = [Hand() for _ in range(4)]

        # Deal new hands only to players involved in the tie-breaker
        self.dealer_hand = Hand()
        for p in self.tie_breaker_players:
            if isinstance(p, int):
                card = self.deck.draw_card()
                if card:
                    self.player_hands[p].add_card(card)
                card = self.deck.draw_card()
                if card:
                    self.player_hands[p].add_card(card)
            elif p == "dealer":
                card = self.deck.draw_card()
                if card:
                    self.dealer_hand.add_card(card)
                card = self.deck.draw_card()
                if card:
                    self.dealer_hand.add_card(card)

        # Mark players not in the tiebreaker as done
        for i in range(4):
          if i not in self.tie_breaker_players:
            self.player_done[i] = True

    def play_tie_breaker(self):
        # Dealer's turn in tie breaker (if involved)
        if "dealer" in self.tie_breaker_players:
            self.play_dealer_turn()

        # Play tie breaker round for players
        while any(not self.player_done[p] for p in self.tie_breaker_players if isinstance(p, int)):
            self.handle_events()
            self.render()

        # Determine the winner after the tie breaker
        dealer_value = self.dealer_hand.value() if "dealer" in self.tie_breaker_players else -1
        player_values = {p: self.player_hands[p].value() for p in self.tie_breaker_players if isinstance(p, int)}

        # Handle busts (values over 21)
        if dealer_value > 21:
            dealer_value = -1
        for k, v in player_values.items():
            if v > 21:
                player_values[k] = -1

        # Find the best value among non-busted players
        best_value = max(player_values.values(), default=-1)

        # Determine the winner(s)
        if dealer_value > best_value:
            self.winners = ["dealer"]
        elif best_value > -1:
            self.winners = [p for p in player_values if player_values[p] == best_value]
            if dealer_value == best_value:
                self.winners.append("dealer")  # Tie with dealer if values are equal
        else:
            self.winners = ["dealer"]

        self.tie_breaker_needed = False
        self.tie_breaker_active = False
        self.game_over = True

    def play(self):
        """Main game loop."""
        self.deal_initial_cards()
        while self.running:
            self.handle_events()
            self.render()
            if all(self.player_done) and not self.game_over and not self.tie_breaker_needed and not self.tie_breaker_active:
                self.play_dealer_turn()
                self.determine_winners()
                self.game_over = True
            if self.tie_breaker_needed and not self.tie_breaker_active:
                self.render()
        pygame.quit()

# Run the game
if __name__ == "__main__":
    os.makedirs("cards", exist_ok=True)  # Ensure card folder exists
    game = Game()
    game.play()