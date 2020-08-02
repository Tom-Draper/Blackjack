import random
import time
from itertools import count


class Card():
    def __init__(self, card_code):
        self.card_code = card_code
        self.path = f'resources/{card_code}.png'
        self.card_value = self.get_card_value()
    
    def get_card_value(self):
        """Takes a card and returns it's numerical value."""
        card_values = {
            **dict.fromkeys(['2C', '2D', '2H', '2S'], 2), 
            **dict.fromkeys(['3C', '3D', '3H', '3S'], 3),
            **dict.fromkeys(['4C', '4D', '4H', '4S'], 4),
            **dict.fromkeys(['5C', '5D', '5H', '5S'], 5),
            **dict.fromkeys(['6C', '6D', '6H', '6S'], 6),
            **dict.fromkeys(['7C', '7D', '7H', '7S'], 7),
            **dict.fromkeys(['8C', '8D', '8H', '8S'], 8),
            **dict.fromkeys(['9C', '9D', '9H', '9S'], 9),
            **dict.fromkeys(['10C', '10D', '10H', '10S',
                             'JC', 'JD', 'JH', 'JS',
                             'KC', 'KD', 'KH', 'KS',
                             'QC', 'QD', 'QH', 'QS'], 10),
        }
        
        if self.card_code in ['AC', 'AD', 'AH', 'AS']:
            return (1, 11)  # Possible values for an Ace
        else:
            return card_values[self.card_code]
    
    def __str__(self):
        return self.card_code


class Hand:
    def __init__(self):
        self.bet = 0
        self.cards = []  # List of card objects
        self.hand_value = (0,)  # Tuple containing possible values of this hand
        self.bust = False
        self.split = False
    
    def placeBet(self, bet):
        self.bet = bet
    
    def add_to_hand_value(self, card, side=None):
        """Add the value of the input card to the current hand value."""
        card_value = card.card_value
        
        hand_values = None
        if self.split and side != None:
            if side == 'left':
                hand_values = self.hand_value[0]
            elif side == 'right':
                hand_values = self.hand_value[1]
        else:
            hand_values = self.hand_value
        
        if hand_values is not None:
            new_hand_value = set()  # Collect unique hand values
            if type(card_value) is tuple:  # If more than one card value (drawn Ace)
                # Add each card value to each current hand value
                # E.g. hand value can be 6 or 16 due to holding an Ace
                #      new card value could be 1 or 10 (an Ace)
                #      new hand value would be 7, 16, 17 or 26
                for hand_value in hand_values:
                    for value in card_value:
                        new_hand_value.add(hand_value + value)
            else:
                for hand_value in hand_values:
                    new_hand_value.add(hand_value + card_value)
                    
            # Save result as tuple
            if self.split and side != None:
                if side == 'left':
                    self.hand_value = tuple((tuple(new_hand_value), self.hand_value[1]))
                elif side == 'right':
                    self.hand_value = tuple((self.hand_value[0], tuple(new_hand_value)))
            else:
                self.hand_value = tuple(new_hand_value) 
    
    def calc_hand_value(self):
        """Calculate the value of the entire hand from scratch."""
        if self.split:
            self.hand_value = ((0,), (0,))
            for card in self.cards[0]:
                self.add_to_hand_value(card, side='left')
            for card in self.cards[1]:
                self.add_to_hand_value(card, side='right')
        else:
            self.hand_value = (0,)
            for card in self.cards:
                self.add_to_hand_value(card)
    
    def __str__(self):
        string = ''
        
        if self.split:
            for i in range(2):
                # Add each card in hand to string
                if len(self.cards[i]) == 0:
                    string += 'None '
                else:
                    for card in self.cards[i]:
                        string += f'{card} '
                
                # Add hand value(s) separates by spaces
                hand_value = ''
                for idx, value in enumerate(self.hand_value[i]):
                    hand_value += f'{value}'
                    if idx < len(self.hand_value[i]) - 1:
                        hand_value += ' or '
                # Add the current hand total to string
                string += f'({hand_value})'
                if i == 0:
                    string += ' -//- '
        else:
            # Add each card in hand to string
            if len(self.cards) == 0:
                string += 'None '
            else:
                for card in self.cards:
                    string += f'{card} '
            
            # Add hand value(s) separates by spaces
            hand_value = ''
            for i, value in enumerate(self.hand_value):
                hand_value += f'{value}'
                if i < len(self.hand_value) - 1:
                    hand_value += ' or '
            # Add the current hand total to string
            string += f'({hand_value})'
            
        return string


class Person:
    def __init__(self):
        self.hand = Hand()
    
    def draw(self, available_cards, side=None):
        """Draws a random cardand adds it to the hand."""
        # vvv TESTING
        available_cards =  ['10C', '10D', '10H', '10S',
                             'JC', 'JD', 'JH', 'JS',
                             'KC', 'KD', 'KH', 'KS',
                             'QC', 'QD', 'QH', 'QS']
        # ^^^ TESTING
        card_code = random.choice(available_cards)
        card = Card(card_code)
        
        if self.hand.split:
            if side == 'left':
                self.hand.cards[0].append(card)
            elif side == 'right':
                self.hand.cards[1].append(card)
            else:
                raise ValueError('If hand has been split, provide a side to draw to.')
        else:
            self.hand.cards.append(card)  # Add card to hand
            
        self.hand.add_to_hand_value(card, side)  # Update hand total
        self.tidyHandValue()
    
    def tidyHandValue(self):
        """Remove any excess hand values over 21."""
        # Remove any bust hand values if more than one hand value option exists
        
        # if self.hand.split:
        #     hand_values = self.hand.hand_value
        # else:
        #     hand_values = [self.hand.hand_value]

        # pile_hand_values = []
        # for hand_value in hand_values:
        #     if len(hand_value) > 1:  # If only one value, keep it even if bust
        #         new_hand_value = []
        #         for value in hand_value:
        #             if value == 21:
        #                 new_hand_value = [21]  # Overwrite hand value, only keep 21
        #                 break
        #             elif value <= 21:  # Potential hand value if under 21
        #                 new_hand_value.append(value)
                        
        #         # Update player's hand value
        #         pile_hand_values.append(tuple(new_hand_value))
        #     else:
        #         # Keep old hand value
        #         pile_hand_values.append(hand_value)
            
        # self.hand.hand_value = tuple(pile_hand_values)
        # print(self.hand.hand_value)
        if self.hand.split:
            new_hand_value = []
            if len(self.hand.hand_value[0]) > 1:
                for hand_value in self.hand.hand_value[0]:
                    if hand_value == 21:
                        new_hand_value = [21]  # Overwrite hand value, only keep 21
                        break
                    elif hand_value <= 21:
                        new_hand_value.append(hand_value)
            
            if len(self.hand.hand_value[1]) > 1:
                for hand_value in self.hand.hand_value[1]:
                    if hand_value == 21:
                        new_hand_value = [21]  # Overwrite hand value, only keep 21
                        break
                    elif hand_value <= 21:
                        new_hand_value.append(hand_value)

            if len(self.hand.hand_value[0]) > 1 or len(self.hand.hand_value[1]) > 1:
                # Update player's hand value
                self.hand.hand_value = tuple(new_hand_value)
        else:
            if len(self.hand.hand_value) > 1:
                new_hand_value = []
                for hand_value in self.hand.hand_value:
                    if hand_value == 21:
                        new_hand_value = [21]  # Overwrite hand value, only keep 21
                        break
                    elif hand_value <= 21:
                        new_hand_value.append(hand_value)
                        
                # Update player's hand value
                self.hand.hand_value = tuple(new_hand_value)
    
    def reset(self):
        self.hand = Hand()
    
    def __str__(self):
        return f'Hand: {self.hand}'

class Player(Person):
    _ids = count(0)
    
    def __init__(self, bank):
        super().__init__()
        
        self.id = next(self._ids)
        self.bank = bank

    def placeBet(self, bet):
        if self.bank - bet < 0:
            print('Insufficient funds')
        else:
            self.hand.bet += bet
            self.bank -= bet
    
    def __str__(self):
        return f'Player {self.id + 1} -> ' + super().__str__() + f', Bank: {self.bank}'

class Dealer(Person):
    def __init(self):
        super().__init__()
    
    def __str__(self):
        return 'Dealer -> ' + super().__str__()


class Blackjack:
    def __init__(self, no_players=1, player_bank=1000):
        self.cards = self.refillDeck()
        self.no_players = no_players
        
        # People dict holds {name : person_object}
        self.people = {}
        # Add the dealer
        self.people['dealer'] = Dealer()
        # Add each player
        for i in range(self.no_players):
            self.people[f'player{i}'] = Player(player_bank)
            
        self.current_side = None  # If split, hit on left pile then right

    
    def refillDeck(self):
        """Return a refilled deck of cards list."""
        return ['2C', '2D', '2H', '2S', '3C', '3D', '3H', '3S',
                '4C', '4D', '4H', '4S', '5C', '5D', '5H', '5S',
                '6C', '6D', '6H', '6S', '7C', '7D', '7H', '7S',
                '8C', '8D', '8H', '8S', '9C', '9D', '9H', '9S',
                '10C', '10D', '3H', '10S', 'AC', 'AD', 'AH', 'AS',
                'JC', 'JD', 'JH', 'JS', 'KC', 'KD', 'KH', 'KS', 
                'QC', 'QD', 'QH', 'QS']
    
    def calcBust(self, dealer=False, player_id=0):
        """Checks whether a given players hand has bust (hand value exceeded 21)."""
        if dealer:
            player = self.people['dealer']
        else:
            player = self.people[f'player{player_id}']
            
            if player.hand.split:
                # For checking if left pile has JUST bust and need to move to right pile
                original = player.hand.bust
                left_bust = True
                for hand_value in player.hand.hand_value[0]:
                    if hand_value <= 21:
                        left_bust = False
                # If calc bust has already been run after split selected and bust has been converted to tuple 
                if type(original) is tuple:
                    # Check if left pile has JUST gone bust
                    if original[0] == False and left_bust:
                        self.current_side = 'right'  # Move to right pile
                right_bust = True
                for hand_value in player.hand.hand_value[1]:
                    if hand_value <= 21:
                        right_bust = False
                player.hand.bust = tuple((left_bust, right_bust))
                return left_bust and right_bust  # Bust if both piles bust
            
        bust = True
        # Check if there is a possible hand value under 21
        for hand_value in player.hand.hand_value:
            if hand_value <= 21:
                bust = False
        player.hand.bust = bust
        return bust

    def dealerContinueDraw(self):
        """Checks if any possible hand values is still under 17.
           Determines whether the dealer should continue to draw"""
        if self.calcBust(dealer=True):
            return False
        
        # Check if any possible hand values are under 17
        for hand_value in self.people['dealer'].hand.hand_value:
            if hand_value < 17:
                return True
        
        return False
    
    def playerDraws(self, dealer=False, player_id=0, side=None, times=1):
        """Player draws input number of times."""
        if dealer:
            print('Dealer draws', end='')
            player = self.people['dealer']
        else:
            print(f'Player {player_id + 1} draws', end='')
            player = self.people[f'player{player_id}']
        
        # If drawing multiple times display multiple
        if times > 1:
            print(f' X{times}')
        else:
            print()
            
        for _ in range(times):
            if len(self.cards) == 0:
                self.refillDeck()
            player.draw(self.cards, side)
        
        print(player, '\n')  # Display plaeyr hand status
    
    def allBust(self):
        """Checks whether every player has bust (hand value exceeds 21)."""
        # Look for player who hasn't bust
        for i in range(self.no_players):
            if self.people[f'player{i}'].hand.bust == False:
                return False
        return True
    
    def divider(self):
        print('-------------\n')
    
    def collectWinnings(self, player_id=0, draw=False):
        placed_bet = self.people[f'player{player_id}'].hand.bet
        
        if draw:
            winnings = placed_bet
        else:
            winnings = placed_bet * 2
            
        # Add winnings to player bank
        self.people[f'player{player_id}'].bank += winnings
    
    def checkWinners(self):
        """Checks each player and prints whether they have won or lost against
           the dealer."""
        # Loop through each player2
        for i in range(self.no_players):
            player = self.people[f'player{i}']
            if player.hand.hand_value > self.people['dealer'].hand.hand_value or \
                    (self.people['dealer'].hand.bust and not player.hand.bust):
                print(f'** Player {i + 1} wins! **')
                self.collectWinnings(i)
            elif player.hand.hand_value == self.people['dealer'].hand.hand_value or \
                        player.hand.bust and self.people['dealer'].hand.bust:
                print('** Draw **')
                self.collectWinnings(i, draw=True)
            else:
                print(f'** Player {i + 1} loses **')
            print()
    
    def reset(self):
        for person in self.people.values():
            person.reset()
    
    def main(self):
        """Begins the game of command line Blackjack."""
        quit = False
        game_count = 1
        while not quit:
            print(f'-------- Game {game_count} begin --------\n')
            
            # Dealer init
            self.playerDraws(dealer=True)
            
            for i in range(self.no_players):
                self.divider()  # Print a divider
                
                # Players init
                self.playerDraws(player_id=i, times=2)
                
                # Place bet for this hand
                bet = input('> Enter bet: ')
                if bet == 'q':
                    quit = True
                    break
                if bet.isdigit():
                    bet = int(bet)
                else:
                    bet = 0
     
                # PLace bet for this hand
                self.people[f'player{i}'].placeBet(bet)
                
                # Players play
                while True:
                    choice = input('> Hit or stand: ')
                    print()

                    if choice == 'q':
                        quit = True
                        break
                    
                    if choice.lower() == 'hit' or choice.lower() == 'h':  # Draw
                        self.playerDraws(player_id=i)
                        
                        if self.checkBust(player_id=i):
                            print(f'** Player {i + 1} bust! **\n')
                            break
                    elif choice.lower() == "stand" or choice.lower() == "s":
                        break
                    else:
                        print('Please enter an option.')
                if quit:
                    break
            if quit:
                break
            
            # If every player hasn't bust, the dealer begins drawing
            if not self.allBust():
                print('Dealer\n{}\n'.format(self.people['dealer']))
                
                # Dealer draws
                while self.dealerContinueDraw():
                    time.sleep(1.5)
                    self.playerDraws(dealer=True)
                
                if self.bust(dealer=True):
                    print('** Dealer bust! **')
            
                self.checkWinners()
            
            self.reset()
            game_count += 1
            time.sleep(2)
    
    def __str__(self):
        string = 'GAME STATUS:\n'
        for person in self.people.values():
            string += f'{person}\n'
 
        # Print list of cards remaining
        string += f'Cards remaining: {self.cards}'
        
        return string

if __name__ == "__main__":
    game = Blackjack()
    game.main()
    pygame.quit()