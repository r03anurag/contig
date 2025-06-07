########### file to define a class for a gameboard
from setup import get_gameboard
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

class Board:
    def __init__(self):
        # 10x10 array of nums as placed, 10x10 grid indicating thier status 
        # (0- available, 1/2-taken by respective player)
        self.num_placement, self.num_status = get_gameboard()

    '''Helper function to return the location of a number'''
    def num_loc(self, sq: int):
        pos = np.where(self.num_placement == sq)
        return pos[0][0], pos[1][0]
    
    '''Allocate a square to a player, if available (return True as indication of availability).
        If unavailable, return False as indication.'''
    def allocate_square(self, sq: int, player_id: int, check_only: bool = False):
        if sq not in self.num_placement:
            return False
        x,y = self.num_loc(sq=sq)
        if self.num_status[x,y] != 0:
            return False
        if not check_only:
            self.num_status[x,y] = player_id
        return True

    '''Helper function to compute winning potential and blocking factor given 1d-array of number statuses.'''
    def winning_potential_and_blocking_factor(self, oneD: np.ndarray, sq: int, player_id: int, diag: bool = False):
        if len(oneD) < 6:
            return 0,0
        if diag:
            nums_windows = sliding_window_view(x=oneD, window_shape=6).copy()
            idxs = np.where(np.isin(self.num_placement, oneD))
            oneD_actual = self.num_status[idxs]
            status_windows = sliding_window_view(x=oneD_actual, window_shape=6).copy()
            mask = np.any(nums_windows == sq, axis=1)
            imp = status_windows[mask]
        else:
            imp = sliding_window_view(x=oneD, window_shape=6).copy()
        opponent = 1 if player_id == 2 else 2
        wp_rows = imp[~np.any(imp == opponent, axis=1)]
        bf_rows = imp[~np.any(imp == player_id, axis=1)]
        if len(wp_rows) == 0:
            wp = 0
        else:
            wp = np.max(np.count_nonzero(wp_rows, axis=1))
        if wp == 5:
            wp = 17
        if len(bf_rows) == 0:
            bf = 0
        else:
            bf = np.max(np.count_nonzero(bf_rows, axis=1))
        return wp, bf

    '''Compute the total winning potential and blocking factor of a given number for a given player'''
    def total_winning_potential_and_blocking_factor(self, sq: int, player_id: int):
        #row_score, col_score, nwse_diag_score, nesw_diag_score = 0,0,0,0
        x,y = self.num_loc(sq=sq)
        col = self.num_status[max((x-5,0)):min(x+6,10), y]
        #print(self.num_placement[max((x-5,0)):min(x+6,10), y])
        row = self.num_status[x, max((y-5,0)):min(y+6,10)]
        #print(self.num_placement[x, max((y-5,0)):min(y+6,10)])
        # add indices for the diags to control space
        nwse_diag = np.diag(self.num_placement, k=y-x)
        #print(nwse_diag)
        #print(np.diag(self.num_placement, k=y-x))
        # lr_flipped_num_placement = np.fliplr(self.num_placement)
        # flip_loc = np.where(lr_flipped_num_placement == sq)
        # xf, yf = flip_loc[0][0], flip_loc[1][0]
        nesw_diag = np.diag(np.fliplr(self.num_placement), k=9-y-x)
        #print(nesw_diag)
        #print(np.diag(np.fliplr(self.num_placement), k=9-y-x))
        #print( np.flip(np.diag(np.fliplr(self.num_placement), k=9-y-x))[max((xf-5,0)):min((yf+6,10))] )
        row_wp, row_bf = self.winning_potential_and_blocking_factor(oneD=row, sq=sq, player_id=player_id)
        col_wp, col_bf = self.winning_potential_and_blocking_factor(oneD=col, sq=sq, player_id=player_id)
        nwse_diag_wp, nwse_diag_bf = self.winning_potential_and_blocking_factor(oneD=nwse_diag, sq=sq, player_id=player_id, diag=True)
        nesw_diag_wp, nesw_diag_bf = self.winning_potential_and_blocking_factor(oneD=nesw_diag, sq=sq, player_id=player_id, diag=True)
        twp = (row_wp + col_wp + nwse_diag_wp + nesw_diag_wp)/17
        tbf = (row_bf + col_bf + nwse_diag_bf + nesw_diag_bf)/17
        return twp, tbf

    '''Compute the neighbor score of a given number'''
    def neighbor_score(self, sq: int):
        x,y = self.num_loc(sq=sq)
        conds = {"n": x-1 >= 0, "s": x+1 <= 9, "w": y-1 >= 0, "e": y+1 <= 9}
        coords = {"n": (x-1,y), "s": (x+1,y), "e": (x,y+1), "w": (x,y-1),
                  "nw": (x-1,y-1), "se": (x+1,y+1), "sw": (x+1,y-1), "ne": (x-1, y+1)}
        # cant index. Simply put only coords, filter, then index
        locs = np.array([coords['n'],coords['s'],
                        coords['w'],coords['e'],
                        coords['nw'],coords['ne'],
                        coords['sw'],coords['se']])
        val = np.array([conds['n'],conds['s'],conds['w'],conds['e'],
                        conds['n'] and conds['w'],conds['n'] and conds['e'],
                        conds['s'] and conds['w'],conds['s'] and conds['e']])
        indices = locs[val]
        neighbs = self.num_status[tuple(indices.T)].astype(bool)
        total = np.sum(neighbs)
        return total/9, total
    
##############################################################

"""
class HumanPlayer:
    def __init__(self, num: int):
        self.id = num
        self.points = 125
        self.color = ["blue","red"][self.id-1]
    
##############################################################

class MachinePlayer:
    def __init__(self):
        self.id = 2
        self.points = 125
        self.color = "red"

    '''Function that will select a square based on possible candidates and its heuristic'''
    def select_square(candidates: list):
"""
