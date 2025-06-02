################ file responsible for setting up the gameboard. Comments are kept to show how numbers were selected.
################ important functions: generate_arithmetic_combos, set_gameboard
import itertools
import os
from sympy import isprime, divisors
from collections import defaultdict
import random
import numpy as np

'''
Function that takes in 3 integers x,y,z, and returns all possible results obtained 
using a combination of mathematical operators +,-,*,/,**.

Inputs: x (int), y (int), z (int)
Output: dict(int -> set[str]), mapping a result to all its possible derivations 
'''
def generate_arithmetic_combos(x: int, y: int, z: int):
    possTriples = list(itertools.permutations((x,y,z), r=3))
    possOps = list(itertools.permutations(("+","*","-","/","**")*2, r=2))
    options = defaultdict(set)
    for a,b,c in possTriples:
        for o1, o2 in possOps:
            comb = f"({a}{o1}{b}){o2}{c}"
            res = eval(comb)
            if type(res) == int and (res > 0 and res <= 180):
                options[res].add(comb)
    return options

'''
Function that generates all possible derivations (3-number combos) for numbers 1-180. 
Saved to nums_likelihood.txt. DO NOT RUN THIS FUNCTION.

Input: none
Outputs: list of all the numbers from 1-180, 
         ordered by the number of ways the number can be 
         generated with 3 12-sided dice using mathematical operators.
         Sorted in descending order.
'''
def generate_derivations():
    deriv = defaultdict(lambda: 0)
    for a in range(1,13):
        for b in range(1,13):
            for c in range(1,13):
                allcombs = generate_arithmetic_combos(x=a,y=b,z=c)
                for k,v in allcombs.items():
                    # eliminate any prime numbers > 50
                    if not(isprime(k) and k > 50):
                        deriv[k] += len(v)
    deriv = dict(sorted(deriv.items(), key=lambda p: p[1], reverse=True))
    if not os.path.exists("nums_likelihood.txt"):
        with open("nums_likelihood.txt", "w") as nfile:
            for n,c in deriv.items():
                nfile.writelines([f"{n} {c}\n"])
    return list(deriv.keys())

'''
Function that takes the sorted list from generate_derivations()
and maintains the following numbers:
    1. All nums < 50
    2. For nums > 50, all those that have at least 5 factors <= 12.
Excludes any numbers that do not have at least 100 possible derivations.
DO NOT CALL THIS FUNCTION; IT IS NOT NECESSARY FOR GAMEPLAY.
'''
def further_filter_nums(srtd: list):
    # function that will give nums an importance score.
    def importance(n: int):
        if n <= 50:
            return (1, n)
        else:
            facts_le_12 = list(filter(lambda div: div <= 12, divisors(n=n)))
            return (2, 1/len(facts_le_12))
    imp = list(filter(lambda v: importance(v) <= (2, 0.2), srtd[:108]))
    return imp

'''
Most important function that sets the gameboard.
Takes the numbers satisfying the two conditions from above, and then 
randomly picks remaining numbers from the most easily derivable numbers (no duplicates).
Input: None
Output: 9x9 numpy.array containing the numbers
'''
def set_gameboard():
    #important = further_filter_nums(generate_derivations())
    important = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 
                16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 
                29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 
                42, 43, 44, 45, 46, 168, 48, 49, 50, 47, 180, 176, 
                54, 56, 60, 160, 140, 66, 70, 72, 80, 84, 144, 88, 
                90, 96, 100, 108, 110, 112, 150, 120, 126, 132]
    #t = list(filter(lambda w: w not in important, generate_derivations()))
    #t = further_filter_nums(t)
    others = random.sample([64, 81, 63, 55, 52, 77, 99, 51, 128, 65, 121, 
                            75, 57, 68, 78, 105, 76, 58, 69, 91, 98, 62, 
                            74, 125, 85, 135, 104, 117, 154, 82, 102, 92, 95],
                            k = 81-len(important))
    total = important+others
    random.shuffle(total)
    board = np.array(total)
    board = board.reshape((1,81))
    board = board.reshape((9,9))
    