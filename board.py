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
    
    '''Allocate (or only check availability of if check_only=True) a square to a player.
       Possible return values:
            * 0: Square is non-existent (e.g., 512)
            * -1/-2: Square exists, but is taken by the respective player.
            * 1: Square is available
    '''
    def allocate_square(self, sq: int, player_id: int, check_only: bool = False):
        if sq not in self.num_placement:
            return 0
        x,y = self.num_loc(sq=sq)
        if self.num_status[x,y] != 0:
            return -self.num_status[x,y]
        if not check_only:
            self.num_status[x,y] = player_id
        return 1

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
        x,y = self.num_loc(sq=sq)
        col = self.num_status[max((x-5,0)):min(x+6,10), y]
        row = self.num_status[x, max((y-5,0)):min(y+6,10)]
        nwse_diag = np.diag(self.num_placement, k=y-x)
        nesw_diag = np.diag(np.fliplr(self.num_placement), k=9-y-x)
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
        locs = np.array([coords['n'],coords['s'],coords['w'],coords['e'],
                        coords['nw'],coords['ne'],coords['sw'],coords['se']])
        val = np.array([conds['n'],conds['s'],conds['w'],conds['e'],
                        conds['n'] and conds['w'],conds['n'] and conds['e'],
                        conds['s'] and conds['w'],conds['s'] and conds['e']])
        indices = locs[val]
        neighbs = self.num_status[tuple(indices.T)].astype(bool)
        total = np.sum(neighbs)
        return total/9, total
    
    '''Helper function that finds a continuous winning sequence containing a number 
        for a specific player (if it exists)'''
    def win_sequence(self, player_id: int, nums1d: np.ndarray, status1d: np.ndarray):
        g1 = np.where(status1d == player_id)
        g1_diffs = np.ediff1d(g1)
        y = np.where(g1_diffs == 1)
        if y[0].shape[0] < 5:
            return []
        y = np.append(y[0], y[0][-1]+1)
        r = g1[0][y]
        return nums1d[r].tolist()

    '''Function that finds all numbers associated with a player's win'''
    def combined_win_sequence(self, sq: int, player_id: int):
        x,y = self.num_loc(sq=sq)
        row_nums, row_status = self.num_placement[x, :], self.num_status[x, :]
        col_nums, col_status = self.num_placement[:, y], self.num_status[:, y]
        diag_nums, diag_status = np.diag(self.num_placement, k=y-x), np.diag(self.num_status, k=y-x)
        antidiag_nums = np.diag(np.fliplr(self.num_placement), k=9-y-x)
        antidiag_status = np.diag(np.fliplr(self.num_status), k=9-y-x)
        R = self.win_sequence(player_id=player_id, nums1d=row_nums.copy(), status1d=row_status.copy())
        C = self.win_sequence(player_id=player_id, nums1d=col_nums.copy(), status1d=col_status.copy())
        D = self.win_sequence(player_id=player_id, nums1d=diag_nums.copy(), status1d=diag_status.copy())
        A = self.win_sequence(player_id=player_id, nums1d=antidiag_nums.copy(), status1d=antidiag_status.copy())
        return R+C+D+A