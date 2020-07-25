import pygame
from collections import namedtuple
from game import Blackjack

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
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    GREEN_BG = (53, 101, 77)  # Poker green
    YELLOW = (150, 150, 0)
    BROWN = (180, 180, 180)

    # Fonts
    GIGANTIC = pygame.font.SysFont('hack', 150)
    HUGE = pygame.font.SysFont('hack', 80)
    TITLE = pygame.font.SysFont('hack', 50)
    LARGER = pygame.font.SysFont('hack', 40)
    NORMAL = pygame.font.SysFont('hack', 20)
    
    GameStatus = namedtuple('GameStatus', 'round_over draw player_won winnings')

    def __init__(self, player_bank=1000):
        super().__init__(player_bank=1000)

        self.win = pygame.display.set_mode(
            (self.WIDTH, self.HEIGHT))  # Set resolution with tuple
        pygame.display.set_caption("Blackjack")  # Title along the window bar

        # Get typical card image size (for displaying cards centrally)
        self.cardSize = self.getCardSize('2D')

        self.buttons = {}  # Dict {name : (x,y)}
        self.quit = False

    def getCardSize(self, card):
        image = pygame.image.load('resources/{}.png'.format(card))
        return image.get_size()

    def scaleImg(self, image, scale_factor):
        width, height = image.get_size()
        return pygame.transform.scale(image, (int(width*scale_factor), int(height*scale_factor)))

    def cardPileWidth(self, no_cards, scale_factor):
        """Get width of a given number of cards when spread in a pile.
           Each subsequent card lies half overlapping the previous card.
           Top card is displayed fully.
           1 card -> width 1 card wide
           2 cards -> width 1.5 cards wide
           3 cards -> width = 2 cards wide.
        """
        return ((no_cards+1)/2) * ((self.cardSize[0]*scale_factor))

    def buildHandValueString(self, dealer=False, player_id=0):
        if dealer:
            hand_value = self.people['dealer'].hand.hand_value
        else:
            hand_value = self.people['player{}'.format(player_id)].hand.hand_value
        
        string = ''
        for i, value in enumerate(hand_value):
            string += str(value)
            if i >= len(hand_value)-1:
                string += ' '
            else:
                string += ' or '
        
        return string

    def displayCards(self, centre_pos, scale_factor, dealer=False, player_id=0):
        if dealer:
            cards = self.people['dealer'].hand.cards
        else:
            cards = self.people['player{}'.format(player_id)].hand.cards

        # Convert centre position to top left corner position
        pos = (centre_pos[0] - self.cardPileWidth(len(cards), scale_factor)/2,
               centre_pos[1] - ((self.cardSize[1]*scale_factor)/2))

        shift = 0  # Shift each subsequent card along to get spread effect
        for card in cards:
            image = pygame.image.load('resources/{}.png'.format(card))
            image = self.scaleImg(image, scale_factor)
            self.win.blit(image, (pos[0] + shift, pos[1]))
            shift += (self.cardSize[0]*scale_factor)/2

    def displayButtons(self):
        # Central buttons
        btns = ['Hit', 'Stand']
        for i, btn in enumerate(btns):
            # Draw a circle
            # Iterate through positions left to right along the middle of the screen
            # Width = centre - (half the length of all buttons and gaps in between) 
            #                + (gap between centre of two buttons)*(button number) 
            centre_pos = (int(self.WIDTH/2 
                              - ((self.RADIUS*2 + self.BTN_GAP) * (len(btns)-1)/2)
                              + (self.RADIUS*2 + self.BTN_GAP) * i),
                          int(self.HEIGHT/2))
            pygame.draw.circle(self.win, self.BLACK,
                               centre_pos, self.RADIUS, 3)
            
            
            # Draw text in centre of button
            text = self.NORMAL.render(btns[i], 1, self.BLACK)
            self.win.blit(text, (centre_pos[0] - text.get_width()/2, 
                                 centre_pos[1] - text.get_height()/2))
            self.buttons[btn[i]] = (centre_pos[0] - text.get_width()/2, 
                                    centre_pos[1] - text.get_height()/2)
        
        # Bet buttons
        bet_btns = ['1', '5', '10', '50', '100']
        btn_colours = [self.BROWN, self.RED, self.BLUE, self.YELLOW, self.BLACK]
        for i, btn in enumerate(bet_btns):
            # Draw a circle
            btn_range = (self.BTN_GAP*(len(btns)-1)) / \
                2 - ((self.RADIUS*len(btns))/2)
            # Iterate through positions top to bottom down the right side of the window
            centre_pos = (int(self.WIDTH - 100),
                          int(self.HEIGHT/2 
                              - ((self.RADIUS*2 + self.BTN_GAP) * (len(bet_btns)-1)/2)
                              + (self.RADIUS*2 + self.BTN_GAP) * i))
            pygame.draw.circle(self.win, btn_colours[i],
                               centre_pos, self.RADIUS, 3)
            # Draw text in centre of button
            text = self.NORMAL.render(bet_btns[i], 1, self.BLACK)
            self.win.blit(text, (centre_pos[0] - text.get_width()/2, 
                                 centre_pos[1] - text.get_height()/2))
            self.buttons[bet_btns[i]] = (centre_pos[0] - text.get_width()/2, 
                                         centre_pos[1] - text.get_height()/2)

    def display(self, game_status):
        # ----- Window -----
        self.win.fill(self.GREEN_BG)

        # ----- Title -----
        text = self.TITLE.render('Blackjack', 1, self.BLACK)
        self.win.blit(text, (self.WIDTH/2 - text.get_width()/2, 20))

        # ----- Buttons ------
        self.displayButtons()

        # ----- Dealer -----
        card_scale_factor = 0.2
        # Display cards
        centre_pos = (self.WIDTH/2, 250)
        self.displayCards(centre_pos, card_scale_factor, dealer=True)
        # Display bust
        if self.people['dealer'].hand.bust:
            text = self.HUGE.render('{}'.format('BUST'), 1, self.RED)
            self.win.blit(text, (centre_pos[0] - text.get_width()/2, centre_pos[1] - text.get_height()/2))
        # Display hand value
        hand_value_str = self.buildHandValueString(dealer=True)
        text = self.NORMAL.render('{}'.format(hand_value_str), 1, self.BLACK)
        self.win.blit(text, (centre_pos[0] - text.get_width()/2, 
                             centre_pos[1] + (self.cardSize[1]*card_scale_factor)/2 + 20))
        
        # ----- Player ------
        player = self.people['player0']
        
        centre_pos = (self.WIDTH/2, 800)
        self.displayCards(centre_pos, card_scale_factor)
        # Display bust
        if player.hand.bust:
            text = self.HUGE.render('{}'.format('BUST'), 1, self.RED)
            self.win.blit(text, (centre_pos[0] - text.get_width()/2, centre_pos[1] - text.get_height()/2))
        # Display bank value
        bank_value = player.bank
        text = self.LARGER.render('£{}'.format(bank_value), 1, self.BLACK)
        self.win.blit(text, (100 - text.get_width()/2, 
                             self.HEIGHT - 100))
        # Display winnings added to bank value
        if game_status.round_over:                            
            if game_status.winnings > 0:
                winnings_text = self.NORMAL.render('+{}'.format(game_status.winnings), 1, self.BLACK)
                self.win.blit(winnings_text, (100 - text.get_width()/2 + 130, 
                                              self.HEIGHT + winnings_text.get_height()/2 - 100))
        # Display hand value
        hand_value_str = self.buildHandValueString()
        text = self.NORMAL.render('{}'.format(hand_value_str), 1, self.BLACK)
        self.win.blit(text, (centre_pos[0] - text.get_width()/2, 
                             centre_pos[1] + (self.cardSize[1]*card_scale_factor)/2 + 20))
        # Display bet value
        bet_value = player.hand.bet
        if bet_value != 0:
            text = self.NORMAL.render('£{}'.format(bet_value), 1, self.BLACK)
            self.win.blit(text, (centre_pos[0] - text.get_width()/2 + 200, 
                                 centre_pos[1]))
        
        # Display "you win", "draw" or "you lose"
        if game_status.round_over:
            centre_pos = (int(self.WIDTH/2), int(self.HEIGHT/2))
            if game_status.draw:
                text = self.GIGANTIC.render('DRAW', 1, self.YELLOW)
            elif game_status.player_won:
                text = self.GIGANTIC.render('YOU WIN', 1, self.GREEN)
            else:
                text = self.GIGANTIC.render('YOU LOSE', 1, self.RED)
            self.win.blit(text, (centre_pos[0] - text.get_width()/2, 
                                 centre_pos[1] - text.get_height()/2))

        pygame.display.update()  # Update the display

    def handleEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Window close button pressed
                self.quit = True
                return True
            if event.type == pygame.MOUSEBUTTONDOWN:
                m_x, m_y = pygame.mouse.get_pos()  # x,y pos of mouse
                print(m_x, m_y)
                return True
        return False
    
    def checkWinners(self):
        """Checks each player and prints whether they have won or lost against
           the dealer."""

        player = self.people['player0']
        if player.hand.hand_value > self.people['dealer'].hand.hand_value or \
                (self.people['dealer'].hand.bust and not player.hand.bust):
            winnings = player.hand.bet*2
            game_status = self.GameStatus(round_over=True, draw=False, player_won=True, winnings=winnings)
            self.collectWinnings(player_id=0)
        elif player.hand.hand_value == self.people['dealer'].hand.hand_value or \
                    player.hand.bust and self.people['dealer'].hand.bust:
            winnings = player.hand.bet*2
            game_status = self.GameStatus(round_over=True, draw=True, player_won=None, winnings=winnings)
            self.collectWinnings(player_id=0, draw=True)
        else:
            game_status = self.GameStatus(round_over=True, draw=False, player_won=False, winnings=0)
         
        self.display(game_status)

    def main(self):
        """One player GUI Blackjack game.
           Overrides the parent class playGame (command line version) method."""
        FPS = 60  # Max frames per second
        # Create a clock obeject to make sure our game runs at this FPS
        clock = pygame.time.Clock()
        
        default_game_status = self.GameStatus(round_over=False, draw=None, player_won=None, winnings=0)

        self.display(default_game_status)

        while not self.quit:
            clock.tick(FPS)

            # ------ PLAY GAME -------
            game_count = 1

            # Dealer init
            self.playerDraws(dealer=True)
            self.display(default_game_status)

            self.divider()  # Print a divider

            # Players init
            self.playerDraws(times=2)
            self.display(default_game_status)

            # Place bet for this hand
            # bet = input('> Enter bet: ')
            # if bet == 'q':
            #     quit = True
            #     break
            # if bet.isdigit():
            #     bet = int(bet)
            # else:
            #     bet = 0
            bet = 10

            # PLace bet for this hand
            self.people['player0'].placeBet(bet)
            self.display(default_game_status)
            

            # Play
            
            self.handleEvents()


            # If every player hasn't bust, the dealer begins drawing
            if not self.allBust():

                print("Dealer\n{}\n".format(self.people['dealer']))

                # Dealer draws
                wait_before_draw = 1500
                last = pygame.time.get_ticks()
                while self.dealerContinueDraw():
                    now = pygame.time.get_ticks()
                    if now - last >= wait_before_draw:
                        self.playerDraws(dealer=True)
                        self.display(default_game_status)
                        last = now
                    self.handleEvents()

                if self.bust(dealer=True):
                    print('** Dealer bust! **')

                self.checkWinners()

            self.reset()  # Redraw new hands
            game_count += 1
            # Wait before begin next round 
            wait = 2000
            last = pygame.time.get_ticks()
            while True:
                now = pygame.time.get_ticks()
                if now - last >= wait:
                    break
                self.handleEvents()
                

game = GUIBlackjack()
game.main()

pygame.quit()
