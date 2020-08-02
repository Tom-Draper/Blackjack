import pygame
import math
from collections import namedtuple
from cli_blackjack import Blackjack

pygame.init()  # Initialise pygame


class GUIBlackjack(Blackjack):

    # Window
    WIDTH = 1200
    HEIGHT = 1000

    # Buttons
    RADIUS = 50
    BTN_GAP = 40

    # Colours
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN = (0, 255, 0)  # Win message
    GREEN_BG = (53, 101, 77)  # Poker green backgroud
    BROWN = (180, 180, 180)  # 1 chip
    RED = (255, 0, 0)  # 5 chip and lose message
    BLUE = (0, 0, 255)  # 10 chip
    YELLOW = (150, 150, 0)  # 50 chip and draw message
    CHIP_BLACK = (220, 220, 220)  # 100 chip
    GREY = (84, 84, 84)  # Inactive button

    # Fonts
    GIGANTIC = pygame.font.SysFont('hack', 150)
    HUGE = pygame.font.SysFont('hack', 80)
    TITLE = pygame.font.SysFont('hack', 50)
    LARGER = pygame.font.SysFont('hack', 40)
    NORMAL = pygame.font.SysFont('hack', 20)
    
    GameStatus = namedtuple('GameStatus', 'round_over draw player_won winnings')

    def __init__(self, player_bank=1000):
        super().__init__(player_bank=1000)

        self.win = pygame.display.set_mode((self.WIDTH, self.HEIGHT))  # Set resolution with tuple
        pygame.display.set_caption("Blackjack")  # Title along the window bar
        
        # Restricted to one player game when using GUI
        self.player = self.people['player0']
        
        self.default_game_status = self.GameStatus(round_over=False, draw=None, player_won=None, winnings=0)
        self.game_status = None

        self.card_scale_factor = 0.2
        # Get typical card image size (for displaying cards centrally)
        self.card_size = self.getCardSize('2D')
        self.quit = False
        self.stand = False

        # Buttons
        self.buttons = {}  # Dict {name : (x,y)}
        self.action_btns_active = True
        self.bet_btns_active = True
        self.action_btns = ['Hit', 'Stand']
        self.bet_btns = ['1', '5', '10', '50', '100']
        
        # Gap between card piles when split
        self.split_gap = self.card_size[0]

    def getCardSize(self, card):
        image = pygame.image.load(f'resources/{card}.png')
        # Return the actual card image dimensions multipled by the scale factor 
        # used during game to display
        return tuple(map(lambda x: x*self.card_scale_factor, image.get_size()))

    def scaleImg(self, image, scale_factor):
        width, height = image.get_size()
        return pygame.transform.scale(image, (int(width*scale_factor), 
                                              int(height*scale_factor)))
    
    def setTimer(self, time):
        last = pygame.time.get_ticks()
        while True and not self.quit:
            now = pygame.time.get_ticks()
            if now - last >= time:
                break
            self.handleEvents()
            self.display()

    def enableAllButtons(self):
        self.action_btns_active = True
        self.bet_btns_active = True
    
    def disableAllButtons(self):
        self.action_btns_active = False
        self.bet_btns_active = False

    def cardPileWidth(self, no_cards, scale_factor):
        """Get width of a given number of cards when spread in a pile.
           Each subsequent card lies half overlapping the previous card.
           Top card is displayed fully.
           1 card -> width 1 card wide
           2 cards -> width 1.5 cards wide
           3 cards -> width = 2 cards wide.
        """
        return ((no_cards+1)/2) * ((self.card_size[0]))
    
    def playerBust(self, bust):
        if type(bust) is tuple:
            if bust[0] == True and bust[1] == True:
                return True
            else:
                return False
        return bust
            
    def buildHandValueString(self, dealer=False, player_id=0):
        no_hands = 1  # Assume single pile of cards (no split)
        if dealer:
            hand_value = self.people['dealer'].hand.hand_value
        else:
            hand_value = self.people[f'player{player_id}'].hand.hand_value
            if self.people[f'player{player_id}'].hand.split:
                no_hands = 2
        
        if no_hands == 1:
            # Add single hand value to list for generalised loop below
            hand_value = [hand_value]
        
        # Build hand value strings
        strings = []
        for i in range(no_hands):
            string = ''
            for idx, value in enumerate(hand_value[i]):
                string += str(value)
                if idx >= len(hand_value[i]) - 1:
                    string += ' '
                else:
                    string += ' or '
            strings.append(string)
        
        if not dealer:
            if self.people[f'player{player_id}'].hand.split:
                # Return hand value for both card piles
                return strings[0], strings[1] 
        # Return hand value for card pile
        return strings[0]



    def displayActionButtons(self):
        for i, btn in enumerate(self.action_btns):
            # Draw a circle
            # Iterate through positions left to right along the middle of the screen
            # Width = centre - (half the length of all buttons and gaps in between)
            #                + (gap between centre of two buttons)*(button number)
            
            # Draw button active or inactive
            if self.action_btns_active:
                btn_colour = self.BLACK
            else:
                btn_colour = self.GREY
            
            # Draw circle
            centre_pos = (int(self.WIDTH/2 
                              - ((self.RADIUS*2 + self.BTN_GAP) * (len(self.action_btns)-1)/2)
                              + (self.RADIUS*2 + self.BTN_GAP) * i),
                          int(self.HEIGHT/2))
            pygame.draw.circle(self.win, btn_colour, centre_pos, self.RADIUS, 3)
            
            # Draw text in centre of button
            text = self.NORMAL.render(self.action_btns[i], 1, btn_colour)
            self.win.blit(text, (int(centre_pos[0] - text.get_width()/2), 
                                 int(centre_pos[1] - text.get_height()/2)))
            
            # Add buttons centre positions to class dictionary
            self.buttons[btn] = centre_pos
    
    def displayBetButtons(self):
        btn_colours = [self.BROWN, self.RED, self.BLUE, self.YELLOW, self.BLACK]
        
        for i, btn in enumerate(self.bet_btns):
            if self.bet_btns_active:
                btn_colour = btn_colours[i]
                text_colour = self.BLACK
            else:
                btn_colour = self.GREY
                text_colour = self.GREY
            
            # Draw circle
            btn_range = (self.BTN_GAP*(len(self.bet_btns)-1))/2 - ((self.RADIUS*len(self.bet_btns))/2)
            # Iterate through positions top to bottom down the right side of the window
            centre_pos = (int(self.WIDTH - 100),
                          int(self.HEIGHT/2 
                              - ((self.RADIUS*2 + self.BTN_GAP) * (len(self.bet_btns)-1)/2)
                              + (self.RADIUS*2 + self.BTN_GAP) * i))
            pygame.draw.circle(self.win, btn_colour, centre_pos, self.RADIUS, 3)
            
            # Draw text in centre of button
            text = self.NORMAL.render(btn, 1, text_colour)
            self.win.blit(text, (int(centre_pos[0] - text.get_width()/2), 
                                 int(centre_pos[1] - text.get_height()/2)))
            
            # Add buttons centre positions to class dictionary
            self.buttons[btn] = centre_pos

    def displayButtons(self):
        self.displayActionButtons()
        self.displayBetButtons()
    
    def displayCardPile(self, cards, centre_pos):
        # Convert centre position to top left corner position
        pos = (centre_pos[0] - self.cardPileWidth(len(cards), self.card_scale_factor)/2,
               centre_pos[1] - self.card_size[1]/2)

        shift = 0  # Shift each subsequent card along to get spread effect
        for card in cards:
            image = pygame.image.load(card.path)
            image = self.scaleImg(image, self.card_scale_factor)
            self.win.blit(image, (int(pos[0] + shift), int(pos[1])))
            shift += (self.card_size[0])/2
    
    def displayCards(self, centre_pos, dealer=False, player_id=0):
        if dealer:
            cards = self.people['dealer'].hand.cards
        else:
            cards = self.people[f'player{player_id}'].hand.cards

        if len(cards) > 0:
            if type(cards[0]) is list:  # Hand has been split
                # Display both piles
                left_centre_pos = (centre_pos[0] - self.card_size[0], centre_pos[1])
                self.displayCardPile(cards[0], left_centre_pos)
                right_centre_pos = (centre_pos[0] + self.card_size[0], centre_pos[1])
                self.displayCardPile(cards[1], right_centre_pos)
            else:  # Normal hand
                self.displayCardPile(cards, centre_pos)
    
    def displayDealer(self):
        # Display cards
        centre_pos = (self.WIDTH/2, 250)
        self.displayCards(centre_pos, dealer=True)
        
        # Display bust
        if self.people['dealer'].hand.bust:
            text = self.HUGE.render('BUST', 1, self.RED)
            self.win.blit(text, (int(centre_pos[0] - text.get_width()/2),
                                 int(centre_pos[1] - text.get_height()/2)))
            
        # Display hand value
        hand_value_str = self.buildHandValueString(dealer=True)
        text = self.NORMAL.render(hand_value_str, 1, self.BLACK)
        self.win.blit(text, (int(centre_pos[0] - text.get_width()/2), int(centre_pos[1] + (self.card_size[1])/2 + 20)))
    
    def displayPlayer(self, player_id=0):
        player = self.people[f'player{player_id}']
        
        # Display cards
        centre_pos = (self.WIDTH/2, 800)
        self.displayCards(centre_pos)
        
        # TODO: REVIEW
        # Display bust
        if player.hand.split:
            if player.hand.bust[0]:
                text = self.HUGE.render('BUST', 1, self.RED)
                self.win.blit(text, (int(centre_pos[0] - text.get_width()/2 - self.split_gap), 
                                    int(centre_pos[1] - text.get_height()/2)))
            if player.hand.bust[1]:
                text = self.HUGE.render('BUST', 1, self.RED)
                self.win.blit(text, (int(centre_pos[0] - text.get_width()/2 + self.split_gap), 
                                    int(centre_pos[1] - text.get_height()/2)))
        else:
            if player.hand.bust:
                text = self.HUGE.render('BUST', 1, self.RED)
                self.win.blit(text, (int(centre_pos[0] - text.get_width()/2), 
                                    int(centre_pos[1] - text.get_height()/2)))
            
        # Display bank value
        bank_value = player.bank
        text = self.LARGER.render(f'£{bank_value}', 1, self.BLACK)
        self.win.blit(text, (int(100 - text.get_width()/2), 
                             int(self.HEIGHT - 100)))
        
        # Display winnings added to bank value
        if self.game_status.round_over:
            if self.game_status.winnings > 0:
                winnings_text = self.NORMAL.render(f'+{self.game_status.winnings}', 1, self.BLACK)
                self.win.blit(winnings_text, (int(100 - text.get_width()/2 + 130), 
                                              int(self.HEIGHT + winnings_text.get_height()/2 - 100)))
                
        # Display hand value
        if player.hand.split:
            left_hand_value_str, right_hand_value_str = self.buildHandValueString()
            left_text = self.NORMAL.render(left_hand_value_str, 1, self.BLACK)
            right_text = self.NORMAL.render(right_hand_value_str, 1, self.BLACK)
            self.win.blit(left_text, (int(centre_pos[0] - left_text.get_width()/2 - self.split_gap), 
                                      int(centre_pos[1] + (self.card_size[1])/2 + 20)))
            self.win.blit(right_text, (int(centre_pos[0] - right_text.get_width()/2 + self.split_gap), 
                                       int(centre_pos[1] + (self.card_size[1])/2 + 20)))
        else:
            hand_value_str = self.buildHandValueString()
            text = self.NORMAL.render(hand_value_str, 1, self.BLACK)
            self.win.blit(text, (int(centre_pos[0] - text.get_width()/2), 
                                 int(centre_pos[1] + (self.card_size[1])/2 + 20)))
        
        # Display bet value
        bet_value = player.hand.bet
        if bet_value != 0:
            text = self.NORMAL.render(f'£{bet_value}', 1, self.BLACK)
            self.win.blit(text, (int(centre_pos[0] - text.get_width()/2 + 200), 
                                 int(centre_pos[1])))
    
    def displayRoundOutcome(self):
        if self.game_status.round_over:
            centre_pos = (int(self.WIDTH/2), int(self.HEIGHT/2))
            if self.game_status.draw:
                text = self.GIGANTIC.render('DRAW', 1, self.YELLOW)
            elif self.game_status.player_won:
                text = self.GIGANTIC.render('YOU WIN', 1, self.GREEN)
            else:
                text = self.GIGANTIC.render('YOU LOSE', 1, self.RED)
            self.win.blit(text, (int(centre_pos[0] - text.get_width()/2), 
                                 int(centre_pos[1] - text.get_height()/2)))
    
    def display(self):
        # Window
        self.win.fill(self.GREEN_BG)

        # Title
        text = self.TITLE.render('Blackjack', 1, self.BLACK)
        self.win.blit(text, (int(self.WIDTH/2 - text.get_width()/2), 20))

        self.displayButtons()
        self.displayDealer()
        self.displayPlayer()
        # Display "you win", "draw" or "you lose"
        self.displayRoundOutcome()

        pygame.display.update()  # Update the display


    def canSplit(self):
        if len(self.player.hand.cards) == 2:
            player_cards = self.player.hand.cards
            card_values = [card.card_value for card in player_cards]
            # Possible to split if both cards are the same value
            return card_values[0] == card_values[1]
        return False

    def split(self):
        self.player.hand.split = True
        # Modify cards to indicate split
        card1, card2 = self.player.hand.cards[0], self.player.hand.cards[1]
        self.player.hand.cards = [[card1], [card2]]
        # Modify hand value to indivate split
        hand_value1, hand_value2 = card1.get_card_value(), card2.get_card_value()
        self.player.hand.hand_value = (tuple((hand_value1,)), tuple((hand_value2,)))
        # Modify bust to indicate split
        self.player.hand.bust = tuple((False, False))
        self.current_side = 'left'

    def handleEvents(self):
        handled = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Window close button pressed
                self.quit = True
                handled = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                m_x, m_y = pygame.mouse.get_pos()  # x,y pos of mouse
                for btn, pos in self.buttons.items():
                    d = math.sqrt((pos[0] - m_x)**2 + (pos[1] - m_y)**2)
                    if d < self.RADIUS:  # If click inside this button
                        # No longer possible to split after first action taken
                        if btn in self.action_btns and self.action_btns_active:
                            if 'Split' in self.action_btns:
                                self.action_btns.remove('Split')
                        if btn == 'Hit' and self.action_btns_active:
                            self.personDraws(side=self.current_side)
                            # Player no longer able to bet
                            self.bet_btns_active = False
                            break  # No other button needs to be checked
                        elif btn == 'Stand' and self.action_btns_active:
                            # If already split and now played stand on left card pile
                            if self.player.hand.split and self.current_side == 'left':
                                # Move to right card pile
                                self.current_side = 'right'
                            else:
                                self.stand = True
                                # Turn off all buttons while dealer plays
                                self.action_btns_active = False
                            self.bet_btns_active = False
                            break
                        elif btn == 'Split' and self.action_btns_active:
                            self.split()
                            break
                        elif btn.isdigit() and self.bet_btns_active:
                            self.player.placeBet(int(btn))
                            break
                handled = True
        return handled
    
    def checkWinners(self):
        """Checks each player and prints whether they have won or lost against
           the dealer."""
        
        # TODO : REVIEW
        if self.player.hand.split:
            results = []
            winnings = 0
            # Get result for both pile of cards
            for i in range(2):
                # Check left pile for win
                if (self.player.hand.hand_value[i] > self.people['dealer'].hand.hand_value or \
                            self.people['dealer'].hand.bust) and not self.player.hand.bust[0]:
                    # Record win
                    results.append('win')
                    winnings += self.player.hand.bet*2
                elif self.player.hand.hand_value[i] == self.people['dealer'].hand.hand_value or \
                            self.player.hand.bust and self.people['dealer'].hand.bust:
                    # Record draw
                    results.append('draw')
                    winnings += self.player.hand.bet
                else:
                    # Player lose
                    results.append('lose')
                
            # Calculate overall results and set game status for end screen
            if results[0] == 'win' or results[1] == 'win':  # One pile wins
                self.game_status = self.GameStatus(round_over=True, draw=False, player_won=True, winnings=winnings)
                self.collectWinnings(player_id=0)  
            elif results[0] == 'draw' or results[1] == 'draw':  # If two draws, or one draw and a loss 
                self.game_status = self.GameStatus(round_over=True, draw=True, player_won=None, winnings=winnings)
                self.collectWinnings(player_id=0, draw=True)
            else:  # Both lose
                self.game_status = self.GameStatus(round_over=True, draw=False, player_won=False, winnings=0)

        else:
            if (self.player.hand.hand_value > self.people['dealer'].hand.hand_value or \
                        self.people['dealer'].hand.bust) and not self.player.hand.bust:
                # Player win
                winnings = player.hand.bet*2
                self.game_status = self.GameStatus(round_over=True, draw=False, player_won=True, winnings=winnings)
                self.collectWinnings(player_id=0)
            elif self.player.hand.hand_value == self.people['dealer'].hand.hand_value or \
                        self.player.hand.bust and self.people['dealer'].hand.bust:
                # Draw
                winnings = player.hand.bet
                self.game_status = self.GameStatus(round_over=True, draw=True, player_won=None, winnings=winnings)
                self.collectWinnings(player_id=0, draw=True)
            else:
                # Player lose
                self.game_status = self.GameStatus(round_over=True, draw=False, player_won=False, winnings=0)

    def main(self):
        """One player GUI Blackjack game.
           Overrides the parent class playGame (command line version) method."""
        FPS = 60  # Max frames per second
        # Create a clock obeject to make sure our game runs at this FPS
        clock = pygame.time.Clock()
        game_count = 0
        
        while not self.quit:
            clock.tick(FPS)
            self.game_status = self.default_game_status
            
            # Disable buttons while set up
            self.disableAllButtons()
            self.display()
            
            # Dealer init
            self.personDraws(dealer=True)
            self.display()
            self.setTimer(1000)
            
            # Players init
            self.personDraws()
            self.setTimer(1000)
            self.personDraws()
            # Check if split is an option
            if self.canSplit():
                self.action_btns.append('Split')  # Add split button
            self.display()
            
            # Ensure all buttons active before play
            self.enableAllButtons()
            
            # Handle actions until player stands, busts or quits
            self.stand = False
            while (not self.stand and not self.playerBust(self.player.hand.bust)) and not self.quit:
                self.handleEvents()  # Update stand (if stand action selected)
                self.display()
                if self.calcBust():  # Update players hand bust status
                    self.action_btns_active = False  # Grey out action buttons if bust
                    self.setTimer(1000)
            
            # Dealer begins drawing
            if not self.allBust() and not self.quit:
                print('Dealer\n{}\n'.format(self.people['dealer']))

                # Dealer draws
                wait_before_draw = 1500
                last = pygame.time.get_ticks()
                while self.dealerContinueDraw():
                    now = pygame.time.get_ticks()
                    if now - last >= wait_before_draw:
                        self.personDraws(dealer=True)
                        self.display()
                        last = now
                    self.handleEvents()
                
                # Update dealer bust status
                self.calcBust(dealer=True)
                self.setTimer(2000)  # Pause to view the result
            
            if not self.quit:
                # Set a new game status for a finished round
                self.checkWinners()
                self.display()
                self.setTimer(2000)  # Pause to view the result
                
                self.reset()  # Redraw new hands
                self.action_btns_active = True
                self.bet_btns_active = True
                game_count += 1

if __name__ == "__main__":
    game = GUIBlackjack()
    game.main()
    pygame.quit()
