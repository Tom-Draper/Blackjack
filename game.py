import random


class Hand():
    def __init__(self, available_cards):
        self.cards = []
        self.hand_value = (0,)  # Tuple containing possible values of this hand
    
    def update_hand_value(self):
        total = 0
        for card in self.cards:
            card_value = self.card_value(card)
            
            new_hand_value = []
            if type(card_value) is tuple:  # If more than one card value (drawn Ace)
                # Add each card value to each current hand value
                # E.g. hand value can be 6 or 16 due to holding an Ace
                #      new card value could be 1 or 10 (an Ace)
                #      new hand value would be 7, 16, 17 or 26
                for hand_value in self.hand_value:
                    for value in card_value:
                        new_hand_value.append(hand_value + value)
            else:
                for hand_value in self.hand_value:
                    new_hand_value.append(hand_value + card_value)
            
            self.hand_value = tuple(new_hand_value)  # Save result as tuple
    
    def card_value(self, card):
        card_values = {
            **dict.fromkeys(['2C', '2D', '2H', '2S'], 2), 
            **dict.fromkeys(['3C', '3D', '3H', '3S'], 3),
            **dict.fromkeys(['4C', '4D', '4H', '4S'], 4),
            **dict.fromkeys(['5C', '5D', '5H', '5S'], 5),
            **dict.fromkeys(['6C', '6D', '6H', '6S'], 6),
            **dict.fromkeys(['7C', '7D', '7H', '7S'], 7),
            **dict.fromkeys(['8C', '8D', '8H', '8S'], 8),
            **dict.fromkeys(['9C', '9D', '9H', '9S'], 9),
            **dict.fromkeys(['10C', '10D', '3H', '10S',
                             'JC', 'JD', 'JH', 'JS',
                             'KC', 'KD', 'KH', 'KS',
                             'QC', 'QD', 'QH', 'QS'], 10),
        }
        
        if card in ['AC', 'AD', 'AH', 'AS']:
            return (1, 11)
        else:
            return card_values[card]
    
    def __str__(self):
        string = ''
        # Print each card in hand
        for card in self.cards:
            string += '{} '.format(card)
        
        # Create sequence of hand values separates by spaces
        hand_value = ''
        for i, value in enumerate(self.hand_value):
            hand_value += '{}'.format(value)
            if i < len(self.hand_value) - 1:
                hand_value += ' or '
            
        string += '  (Total = {})'.format(hand_value)
            
        return string


class Player():
    def __init__(self, available_cards):
        self.hand = Hand(available_cards)
        
        self.draw(available_cards)
        self.draw(available_cards)
        
        self.hand.update_hand_value()
    
    def draw(self, available_cards):
        self.hand.cards.append(random.choice(available_cards))
    
    def __str__(self):
        return 'Hand: {}'.format(self.hand)
    

class Game():
    def __init__(self, no_players=1):
        self.cards = self.refill()
        self.no_players = no_players
        
        self.players = {}
        # Add the dealer
        self.players['dealer'] = Player(self.cards)
        # Add each player
        for i in range(self.no_players):
            self.players['player{}'.format(i)] = Player(self.cards)
    
    def refill(self):
        return ['2C', '2D', '2H', '2S', '3C', '3D', '3H', '3S',
                '4C', '4D', '4H', '4S', '5C', '5D', '5H', '5S',
                '6C', '6D', '6H', '6S', '7C', '7D', '7H', '7S',
                '8C', '8D', '8H', '8S', '9C', '9D', '9H', '9S',
                '10C', '10D', '3H', '10S', 'AC', 'AD', 'AH', 'AS',
                'JC', 'JD', 'JH', 'JS', 'KC', 'KD', 'KH', 'KS', 
                'QC', 'QD', 'QH', 'QS']
    
    def playGame(self):
        pass
    
    def __str__(self):
        # Print dealer
        string = 'Dealer - {}\n'.format(self.players['dealer'])
        # Print each player
        for i in range(self.no_players):
            string += 'Player{} - {}\n'.format(i+1, self.players['player{}'.format(i)])
        string += 'Cards remaining: {}'.format(self.cards)
        
        return string

game = Game()
print(game)