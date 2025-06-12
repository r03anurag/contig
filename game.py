########### file to define a class for a typical game
from board import Board
from setup import generate_arithmetic_combos
import heapq

class ContigGame:
    def __init__(self, computer: bool):
        self.points1 = 100
        self.points2 = 100
        self.computer_mode = computer
        self.board = Board()

    '''Helper Function that will calculate the heuristic for a machine player, 
        given a certain possible candidate.'''
    def heuristic(self, candidate: int):
        wp, bf = self.board.total_winning_potential_and_blocking_factor(sq=candidate, player_id=2)
        nbn, nb = self.board.neighbor_score(sq=candidate)
        deficit = 0/100
        return (0.4*(1-deficit)*wp + 0.4*(1+deficit)*nbn + 0.2*bf, 
                nb,
                wp >= 1, 
                max((self.points2-nb,0))==0)
    
    '''Function to process a human's turn.
        Inputs: square (int), ID of player (int)
        Possible Outputs: 
            - "": desired square is taken or does not exist, choose another.
            - f"win|{x},{y}|{neighbors}": The respective human player has won the game. UI will know the 
                     current player and assign a win accordingly.
            - f"{x},{y}|{neighbors}": The turn is complete, and the other player gets to play now. 
                                 Subtract the neighbor points and adjust the score.
    '''
    def human_turn(self, square: int, player_id: int):
        good = self.board.allocate_square(sq=square, player_id=player_id, check_only=True)
        if not good:
            return ""
        x,y = self.board.num_loc(sq=square)
        wp, _ = self.board.total_winning_potential_and_blocking_factor(sq=square, player_id=player_id)
        _, nb = self.board.neighbor_score(sq=square)
        _ = self.board.allocate_square(sq=square, player_id=player_id)
        if player_id == 1:
            self.points1 = max((self.points1-nb,0))
        else:
            self.points2 = max((self.points2-nb,0))
        if wp >= 1 or self.points1 == 0 or self.points2 == 0:
            ws = self.board.combined_win_sequence(sq=square, player_id=player_id)
            return f"win|{x},{y}|{nb}|{ws}"
        return f"{x},{y}|{nb}"
    
    '''Function to process machine's turn.
        Inputs: dice rolls (list of 3 ints)
        Possible Outputs:
            - f"win|{x},{y}|{neighbors}{just}": Machine has won. UI knows the current player is 2 and displays accordingly.
            - "pass": Machine has no options available based on dice rolls, so it passes its turn.
            - f"{x},{y}|{neighbors}|{just}": Machine has completed its turn. Adjust its neighbor score,
                                     and display its dice rolls and computation for the human player to see.
    '''
    def machine_turn(self, dice: list):
        poss = generate_arithmetic_combos(x=dice[0], y=dice[1], z=dice[2])
        sposs = []
        for n, jsts in poss.items():
            check = self.board.allocate_square(sq=n, player_id=2, check_only=True)
            if check:
                sc, nb2, wpFlag, nbFlag = self.heuristic(candidate=n)
                heapq.heappush(sposs, [-sc, nb2, n])
                if wpFlag or nbFlag:
                    x1, y1 = self.board.num_loc(sq=n)
                    _ = self.board.allocate_square(sq=n, player_id=2)
                    self.points2 = max((self.points2-nb2,0))
                    j = jsts.copy()
                    j = j.pop()
                    ws = self.board.combined_win_sequence(sq=n, player_id=2)
                    return f"win|{x1},{y1}|{nb2}|{j}|{ws}"
        if len(sposs) == 0:
            return "pass"
        _, nb2, choice = heapq.heappop(sposs)
        _ = self.board.allocate_square(sq=choice, player_id=2)
        self.points2 = max((self.points2-nb2,0))
        justs = poss[choice].copy()
        just = justs.pop()
        x2, y2 = self.board.num_loc(sq=choice)
        return f"{x2},{y2}|{nb2}|{just}"