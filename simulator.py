import random
import matplotlib.pyplot as plt
import numpy as np

# Function to plot the lines
def plot_lines(data):
    plt.figure(figsize=(10, 6))
    # Calculate differences between first and last values
    differences = [lst[-1] - lst[0] for lst in data]
    min_diff = np.min(differences)
    max_diff = np.max(differences)
    median_diff = np.median(differences)
    std_diff = np.std(differences)

    # Normalize differences for colormap
    norm = plt.Normalize(min(differences), max(differences))
    colors = plt.cm.plasma(norm(differences))

    for idx, values in enumerate(data):
        plt.plot(values, color=colors[idx])

    stats_text = (
        f"Most Loss: {min_diff:.2f}\n"
        f"Most Profit: {max_diff}\n"
        f"Median Profit: {median_diff}\n"
        f"Std Dev: {std_diff:.2f}"
    )
    plt.text(0.05, 0.95, stats_text,
         transform=plt.gca().transAxes,
         fontsize=10,
         verticalalignment='top',
         bbox=dict(facecolor='white', alpha=0.5))

    plt.title('Line Graphs of '+str(len(data))+' episodes')
    plt.xlabel('Rounds Played')
    plt.ylabel('Money')
    plt.grid(True)
    plt.savefig("blackjack_random_returns.png", dpi=300, bbox_inches='tight')

class State:
    def __init__(self, player_sum, dealer_hand, running_count): #, remaining_decks):
        self.player_sum = player_sum
        self.dealer_hand = dealer_hand
        self.running_count = running_count
        # self.remaining_decks = remaining_decks    # we can add this also rounded to nearest 0.5
    
    # toString method
    def __str__(self):
        return f"[Player Sum: {self.player_sum}, Dealer Hand: {self.dealer_hand}, Running Count: {self.running_count}]"



class BlackjackGame:
    def __init__(self, start_money, num_decks=5):
        self.start_money = start_money
        self.current_money = start_money
        self.num_decks = num_decks
        self.deck = self.create_deck(num_decks)
        self.money_history = [start_money]
        self.running_count = 0
        self.history = []  # To store [s, a, r] tuples
        self.bet_values = [25, 50, 75, 100]
        self.bet_probs = [0.65, 0.2, 0.1, 0.05]
        self.play_values = ["hit", "stand"]
        self.final_states = ["win", "lose", "draw"]

    def create_deck(self, n=1):
        suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        deck = [(rank, suit) for suit in suits for rank in ranks] * n
        random.shuffle(deck)
        return deck

    def deal_card(self, update_count = False):
        new_card = self.deck.pop()
        if update_count:
            self.update_count(new_card)
        return new_card
    
    def update_count(self, card):
        rank = card[0]
        if rank in ["2", "3", "4", "5", "6"]:
            self.running_count += 1
        elif rank in ["10", "J", "Q", "K", "A"]:
            self.running_count -= 1
            
    def calculate_value(self, hand):
        value = 0
        num_aces = 0
        for card in hand:
            rank = card[0]
            if rank in ["J", "Q", "K"]:
                value += 10
            elif rank == "A":
                num_aces += 1
                value += 11
            else:
                value += int(rank)

        while value > 21 and num_aces > 0:
            value -= 10
            num_aces -= 1

        return value

    def get_bet_amount(self):
        # in the counting cards, bet amount is based on the count
        # for now it is random
        bet_amount = random.choices(self.bet_values, weights=self.bet_probs)[0]
        while bet_amount > self.current_money:
            bet_amount = random.choices(self.bet_values, weights=self.bet_probs)[0]
        return bet_amount

    def play_round(self):
        player_hand = []
        dealer_hand = []
        bet_amount = self.get_bet_amount()

        # Deal initial cards
        player_hand.append(self.deal_card(update_count=True))
        dealer_hand.append(self.deal_card(update_count=True))
        player_hand.append(self.deal_card(update_count=True))
        dealer_hand.append(self.deal_card(update_count=False))  # update count for dealer cards is updated later

        # Create initial state
        state = State(self.calculate_value(player_hand), self.calculate_value([dealer_hand[0]]), self.running_count)

        if self.calculate_value(player_hand) == 21: # player has blackjack
            if self.calculate_value(dealer_hand) == 21: # dealer also has blackjack
                reward = 0
            else: # dealer does not have blackjack
                reward = bet_amount*1.5
            self.update_count(dealer_hand[1])
            # next_state = State(self.calculate_value(player_hand), self.calculate_value(dealer_hand),self.running_count)
            next_state = "win" if reward > 0 else "draw"
            self.history.append((state, "stand", reward, next_state))
            self.current_money += reward
        else:
            while True:
                action = random.choice(self.play_values)
                if action == "hit":

                    state = State(self.calculate_value(player_hand), self.calculate_value([dealer_hand[0]]), 
                      self.running_count)
                    
                    player_hand.append(self.deal_card())
                    self.update_count(player_hand[-1])

                    if self.calculate_value(player_hand) > 21:
                        reward = -bet_amount
                        # next_state = State(self.calculate_value(player_hand), self.calculate_value(dealer_hand),self.running_count)
                        next_state = "lose"
                        self.history.append((state, action, reward, next_state))
                        self.current_money += reward
                        break
                    else:
                        reward = 0
                        # next_state = State(self.calculate_value(player_hand), self.calculate_value([dealer_hand[0]]),self.running_count)
                        next_state = "playing"
                        self.history.append((state, action, reward, next_state))
                else:  # stand
                    while self.calculate_value(dealer_hand) < 17:
                        dealer_hand.append(self.deal_card())
                        self.update_count(dealer_hand[-1])
                    
                    player_value = self.calculate_value(player_hand)
                    dealer_value = self.calculate_value(dealer_hand)
                    
                    if dealer_value > 21 or player_value > dealer_value:
                        reward = bet_amount
                    elif dealer_value > player_value:
                        reward = -bet_amount
                    else:
                        reward = 0
                    
                    # next_state = State(player_value, dealer_value, self.running_count)
                    next_state = "lose" if reward < 0 else "win" if reward > 0 else "draw"
                    self.history.append((state, action, reward, next_state))    # action is stand
                    self.current_money += reward
                    break

        self.money_history.append(self.current_money)

    def play_game(self):
        while self.current_money > 0 and len(self.deck) > 26:
            self.play_round()
        return self.money_history, self.history

    def reset(self):
        self.current_money = self.start_money
        self.deck = self.create_deck(self.num_decks)
        self.money_history = [self.start_money]
        self.history = []



if __name__ == "__main__":
    start_money = 150
    money_histories = []
    action_histories = []
    episodes = 1

    for _ in range(episodes):
        game = BlackjackGame(start_money)
        money_history, action_history = game.play_game()
        money_histories.append(money_history)
        action_histories.append(action_history)

    print("Action Histories: ")
    for action_history in action_histories:
        for action in action_history:
            print(str(action[0]), action[1], action[2], str(action[3]))
    plot_lines(money_histories)