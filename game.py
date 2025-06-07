########### file to define a class for a typical game
from board import Board
from setup import generate_arithmetic_combos
import random 
import heapq
import sys

class ContigGame:
    def __init__(self, computer: bool):
        self.player1 = {"points": 120, "color": "#a8e0f0"}
        self.player2 = {"points": 120, "color": "#f5bebc"}
        self.computer_mode = computer
        self.board = Board()
        self.current_player = False

    '''Helper Function that will calculate the heuristic for a machine player, 
        given a certain possible candidate.'''
    def heuristic(self, candidate: int):
        wp, bf = self.board.total_winning_potential_and_blocking_factor(sq=candidate, player_id=2)
        nbn, nb = self.board.neighbor_score(sq=candidate)
        deficit = 0/100
        return (0.4*(1-deficit)*wp + 0.4*(1+deficit)*nbn + 0.2*bf, 
                nb,
                wp >= 1, 
                max((self.player2['points']-nb,0))==0)
    
    '''Command Line Execution of a human vs. Computer Game - FOR TESTING ONLY. NOT MEANT FOR 
        REGULAR GAMEPLAY.'''
    def human_vs_computer_CLI(self):
        print(self.board.num_placement)
        while True:
            ## Human
            d1, d2, d3 = random.randint(1,12), random.randint(1,12), random.randint(1,12)
            pass1 = False
            while True:
                expr = input(f"Player 1, you rolled {d1}, {d2}, {d3}. Form an expression using mathematical operators, or pass:")
                if expr == "pass":
                    pass1 = True
                    break
                result = eval(expr)
                good = self.board.allocate_square(sq=result, player_id=1)
                if good:
                    break
            if not pass1:
                wp1, _ = self.board.total_winning_potential_and_blocking_factor(sq=result, player_id=1)
                _, nb1 = self.board.neighbor_score(sq=result)
                self.player1['points'] = max((self.player1['points']-nb1,0))
                print(self.board.num_status)
                print(f"scores (Human, Computer): {self.player1['points']}, {self.player2['points']}")
                if wp1 >= 1 or self.player1['points'] == 0:
                    print("Player 1 Wins!")
                    sys.exit(1)

            ## Computer
            d1, d2, d3 = random.randint(1,12), random.randint(1,12), random.randint(1,12)
            pass2 = False
            print(f"Computer rolled {d1}, {d2}, {d3}. Looking at possibilities...")
            poss = generate_arithmetic_combos(x=d1, y=d2, z=d3)
            #poss = list(filter(lambda p: self.board.allocate_square(sq=p, player_id=2, check_only=True), list(poss.keys())))
            sposs = []
            for n, _ in poss.items():
                #print(f"CHOICE {n}")
                check = self.board.allocate_square(sq=n, player_id=2, check_only=True)
                if check:
                    sc, nb2, wpFlag, nbFlag = self.heuristic(candidate=n)
                    heapq.heappush(sposs, [-sc, nb2, n])
                    if wpFlag or nbFlag:
                        _ = self.board.allocate_square(sq=n, player_id=2)
                        self.player2['points'] = max((self.player2['points']-nb2,0))
                        print(self.board.num_status)
                        print(f"scores (Human, Computer): {self.player1['points']}, {self.player2['points']}")
                        print("Computer Wins!")
                        sys.exit(1)
            if len(sposs) == 0:
                pass2 = True
                print("No possibilities, Computer passes its turn")
            if not pass2:
                _, nb2, choice = heapq.heappop(sposs)
                _ = self.board.allocate_square(sq=choice, player_id=2)
                self.player2['points'] = max((self.player2['points']-nb2,0))
                just = poss[choice].copy()
                print(f"Computer chooses square {choice}, computed as {just.pop()}. Its score is now {self.player2['points']}")
                print(self.board.num_status)
                print(f"scores (Human, Computer): {self.player1['points']}, {self.player2['points']}")
            

cg = ContigGame(computer=True)
cg.human_vs_computer_CLI()