# contig
My version of the classic mathematical game in which one tries to either reduce their points to 0 and/or gets a consecutive sequence.

# Description
Contig is a game in which two (2) players utilize 3 numbers, rolled on 3 12-sided dice (in this case randomly generated integers between 1-12), 
along with the mathematical operations of addition (+), subtraction (-), multiplication (*), division (/), and exponentiation 
(**; denoted as "^" on UI), to calculate a final result that corresponds with a square on a 10x10 board. One of the objectives is to 
carefully select squares such that one creats a continuous sequence of six (6) squares captured by them. This sequence may be 
horizontal, vertical, or diagonal.

Additionally, each player begins with 100 points. Every time a player selects a square, their points decrease based on how many 
squares adjacent to their selection have been taken (i.e. their "neighbors"). Again, these neighbors can be horizontally, vertically, 
or diagonally adjacent to the square in question. For example, on their turn, if a player selects a square that has 4 neighbors, their
score decreases by 4. The other objective of this game is to be the first to arrive at zero (0) points. 

# Getting Started

## Dependencies
* You will need to install NumPy. To do so, run `pip install numpy` on your terminal.
* Make sure to install [node.js](https://nodejs.org/en/download/current).
* Code is compatible with any OS. Make sure your Python version is at least 3.12.9 for predictable results.

## Running the code
* You will need TWO (2) terminal instances - one for the frontend, and one for the backend.
* Backend:
    * Navigate to `contig/` directory, and open a terminal.
    * Type `flask run`.
* Frontend:
    * Navigate to `contig/contig` directory, and open another terminal.
        1. Type `npm install` (only if it is the first time running the code).
        2. Type `npm run dev` to run the server locally. 
            * (OPTIONAL) If you want to build this app for production, additionally run the command `npm run build`.
        3. Copy paste the url containing "localhost" (should be displayed in the terminal) into
           your browser. 
* This game can either be played by 2 people, or one can play against the computer. To do the latter, change the variable `computer` in
  line 12 of `app.py` to `True`. 

# Author
* Anurag Renduchintala

# Versions
* 6/12/2025
    * Initial release.

# Acknowledgements
* This game was inspired by the Mathematics Pentathlon Division III Game [Contig60](https://www.mathpentath.org/product/contig-60tm-complete-game/). I remember playing this game back in elementary school during my time at Math Pentathlon, 
and wanted to experiment with a bigger board (10x10 opposed to 8x8), the capability to use exponentiation, and how 
an AI might make decisions at every step of the game. 