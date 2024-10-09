import random
import matplotlib.pyplot as plt
import numpy as np

random.seed(42)
bet_values = [10,20,50,100]
bet_probs = [0.65,0.2,0.1,0.05]
play_values = ["hit", "stand"]


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


def create_deck(n=1):
    """Creates a standard deck of 52 cards."""
    suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
    ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
    deck = [(rank, suit) for suit in suits for rank in ranks]*n     # creates n decks
    random.shuffle(deck)                                            # shuffles n decks
    return deck

def deal_card(deck):
    """Deals a single card from the deck."""
    return deck.pop()

def calculate_value(hand):
    """Calculates the value of a hand in Blackjack."""
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

    # Adjust for Aces if needed
    while value > 21 and num_aces > 0:
        value -= 10
        num_aces -= 1

    return value

def play_game(start_money):
    """Plays a single game of Blackjack."""
    deck = create_deck(5)
    current_money = start_money
    history = [current_money]
    while current_money>0 and len(deck)>26:
        player_hand = []
        dealer_hand = []

        bet_amount = random.choices(bet_values, weights=bet_probs)[0]
        if bet_amount>current_money:
            while bet_amount>current_money:
                bet_amount = random.choices(bet_values, weights=bet_probs)[0]

        # Deal initial cards
        player_hand.append(deal_card(deck))
        player_hand.append(deal_card(deck))
        dealer_hand.append(deal_card(deck))
        dealer_hand.append(deal_card(deck))

        # Player's turn
        if calculate_value(player_hand)==21:
            current_money = current_money+bet_amount
            history.append(current_money)
        else:
            fin = False
            while not fin:
                choice = random.choices(play_values)[0]
                if choice == "hit":
                    player_hand.append(deal_card(deck))
                    if calculate_value(player_hand) > 21:
                        current_money = current_money-bet_amount
                        history.append(current_money)
                        fin = True
                else: # stand
                    fin = True
                     # Dealer's turn
                    while calculate_value(dealer_hand) < 17:
                        dealer_hand.append(deal_card(deck))
                    
                    player_value = calculate_value(player_hand)
                    dealer_value = calculate_value(dealer_hand)
                    if dealer_value > 21:
                        current_money+=bet_amount
                    elif dealer_value == player_value:
                        current_money+=0
                    elif dealer_value > player_value:
                        current_money-=bet_amount
                    else:   #idk i dont think this will happen
                        current_money+=bet_amount
                    history.append(current_money)
    return history
        

if __name__ == "__main__":
    start_money = 500
    histories = []
    episodes = 1000
    while episodes!=0:
        histories.append(play_game(start_money))
        episodes-=1
    plot_lines(histories)