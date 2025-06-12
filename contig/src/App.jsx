import { useState, useEffect } from 'react'
import axios, {isAxiosError} from 'axios'
import './App.css'

// helper function to get a random int in range [min, max)
function getRandomInt(min, max) {
  const minCeiled = Math.ceil(min);
  const maxFloored = Math.floor(max);
  return Math.floor(Math.random() * (maxFloored - minCeiled) + minCeiled); 
  // The maximum is exclusive and the minimum is inclusive
}

export default function ContigGame() {
  // variables to store players 1 and 2 points (initially 100)
  const [points1, setPoints1] = useState(100);
  const [points2, setPoints2] = useState(100);
  const lightcolors = {1:"#a8e0f0",2:"#f5bebc"};
  const darkcolors = {1:"blue",2:"red"};
  // variables for the grid (numbers, statuses (0,1,2))
  const [numbers, setNumbers] = useState([Array(10).fill(0),Array(10).fill(0),
                                          Array(10).fill(0),Array(10).fill(0),
                                          Array(10).fill(0),Array(10).fill(0),
                                          Array(10).fill(0),Array(10).fill(0),
                                          Array(10).fill(0),Array(10).fill(0)]);
  const [status, setStatus] = useState([Array(10).fill(0),Array(10).fill(0),
                                        Array(10).fill(0),Array(10).fill(0),
                                        Array(10).fill(0),Array(10).fill(0),
                                        Array(10).fill(0),Array(10).fill(0),
                                        Array(10).fill(0),Array(10).fill(0)]);
  // variable to store current player (1/2)
  const [currentPlayer, setCurrentPlayer] = useState(1);
  // variable to indicate computer mode or not
  const [computerMode, setComputerMode] = useState(false);
  /* variables to indicate who the winner is (0 if no one has won yet, otherwise 1/2),
      and what sequence of numbers constitutes the win */
  const [win, setWin] = useState(false);
  const [winSeq, setWinSeq] = useState([]);
  // variables to store the dice rolls and operators, as well as what has been used
  const [keys, setKeys] = useState([0,0,0,"+","-","*","/","^","(",")"]);
  const [used, setUsed] = useState([]);
  const [indices, setIndices] = useState([]);
  const [useCount, setUseCount] = useState(Array(10).fill(0));
  // variable to determine if expression was invalid
  const [invalidExpr, setInvalidExpr] = useState(false);
  // variable to store what goes on the display
  const [display, setDisplay] = useState("---");

  // function to handle the clicking of keyboard buttons
  function handleKeyboardPress(keyVal, idx) {
    let thisUsed = used.slice();
    let thisUseCount = useCount.slice();
    let thisIdcs = indices.slice();
    thisUsed.push(keyVal);
    thisIdcs.push(idx);
    thisUseCount[idx]++;
    setUseCount(thisUseCount.slice());
    setUsed(thisUsed.slice());
    setIndices(thisIdcs.slice());
    setDisplay(thisUsed.join(''));
  }
  
  // function to handle Backspace clicks
  function handleBackspace() {
    let thisUsed = used.slice();
    let thisUseCount = useCount.slice();
    let thisIdcs = indices.slice();
    thisUsed.pop();
    let last_used_item_idx = thisIdcs.pop();
    thisUseCount[last_used_item_idx]--;
    setUseCount(thisUseCount.slice());
    setUsed(thisUsed.slice());
    setIndices(thisIdcs.slice());
    setDisplay(thisUsed.length == 0 ? "---": thisUsed.join(''));
    if (thisUsed.length == 0) {
      setInvalidExpr(false);
    }
  }

  // function to handle Pass click
  function handlePass() {
    let thisCurrentPlayer = currentPlayer;
    setCurrentPlayer(thisCurrentPlayer == 1 ? 2 : 1);
  }

  // function to handle Clear click
  function handleClear() {
    setUsed([]);
    setUseCount(Array(10).fill(0));
    setIndices([]);
    setDisplay("---");
    setInvalidExpr(false);
  }

  // function to handle Enter click
  async function handleEnter() {
    // 1. See if the expression is acceptable using RegEx
    let result;
    let pattern = /(\+|-)?\d{1,2}(\+|\*|\/|-|\^)(\+|-)?\d{1,2}(\+|\*|\/|-|\^)(\+|-)?\d{1,2}/;
    let thisUsed = used.join('');
    let valid = pattern.test(thisUsed.replace("(","").replace(")",""));
    if (valid) {
      try {
        result = eval(thisUsed.replace("^","**"));
      } catch {
        setInvalidExpr(true);
        return;
      }
    } else {
      setInvalidExpr(true);
      return;
    }
    // 2. Expression evaluates to a valid number. Check to make sure it is a + int, 
    // then send it to the backend to check validity.
    if (result < 1 || Math.floor(result) !== result) {
      setDisplay("Result must be a positive integer between 1 and 180.");
      return;
    }
    const response = await axios.post(`http://localhost:5000/api/humanturn`, `${result},${currentPlayer}`);
    // square does not exist or is already taken
    if (response.data === "") {
      setDisplay(`Square ${result} is either taken or does not exist. Select another option, or pass.`);
      return;
    }
    // current player has won
    else if (response.data.slice(0,3) === "win") {
      let data = response.data.split("|");
      let coords = data[1].split(",")
      let nb = +data[2];
      let ws = eval(data[3]);
      let thisStatus = status.slice();
      if (currentPlayer == 1) {
        let thisPoints1 = points1;
        thisPoints1 = Math.max(thisPoints1-nb,0);
        thisStatus[+coords[0]][+coords[1]] = 1;
        setPoints1(thisPoints1);
      } else {
        let thisPoints2 = points2;
        thisPoints2 = Math.max(thisPoints2-nb,0);
        thisStatus[+coords[0]][+coords[1]] = 2;
        setPoints2(thisPoints2);
      }
      setStatus(thisStatus.slice());
      setWin(true);
      setWinSeq(ws.slice());
      return;
    }
    // regular turn; subtract points and switch player
    else {
      let data = response.data.split("|");
      let coords = data[0].split(",")
      let nb = +data[1];
      let thisStatus = status.slice();
      if (currentPlayer == 1) {
        let thisPoints1 = points1;
        thisPoints1 = Math.max(thisPoints1-nb,0);
        thisStatus[+coords[0]][+coords[1]] = 1;
        setPoints1(thisPoints1);
      } 
      else {
        let thisPoints2 = points2;
        thisPoints2 = Math.max(thisPoints2-nb,0);
        thisStatus[+coords[0]][+coords[1]] = 2;
        setPoints2(thisPoints2);
      }
    }
    // 3. Switch player
    let thisCurrentPlayer = currentPlayer;
    setCurrentPlayer(thisCurrentPlayer == 1 ? 2 : 1);
    return;
  }

  // function to handle machine posting and getting data to & from server
  async function handleMachineTurn(die1, die2, die3) {
    if (computerMode && currentPlayer == 2) {
      const response = await axios.post("http://localhost:5000/api/machineturn", `${die1},${die2},${die3}`);
      // machine passes. Simply switch player.
      if (response.data === "pass") {
        setDisplay("System passes its turn.");
        setCurrentPlayer(1);
        return;
      }
      // machine has won 
      else if (response.data.slice(0,3) === "win") {
        let data = response.data.split("|");
        let coords = data[1].split(",")
        let nb = +data[2];
        let just = data[3];
        let ws = eval(data[4]);
        let thisStatus = status.slice();     
        let thisPoints2 = points2;
        thisPoints2 = Math.max(thisPoints2-nb,0);
        thisStatus[+coords[0]][+coords[1]] = 2;
        setPoints2(thisPoints2);
        setStatus(thisStatus.slice());
        setDisplay(`System rolled ${die1},${die2},${die3}. ${just} = ${numbers[+coords[0]][+coords[1]]}`);
        setWin(true);
        setWinSeq(ws.slice());
        return;
      }
      // handle data as usual
      else {
        let data = response.data.split("|");
        let coords = data[0].split(",")
        let nb = +data[1];
        let just = data[2];
        let thisStatus = status.slice();
        let thisPoints2 = points2;
        thisPoints2 = Math.max(thisPoints2-nb,0);
        thisStatus[+coords[0]][+coords[1]] = 2;
        setPoints2(thisPoints2);
        setStatus(thisStatus.slice());
        setDisplay(`System rolled ${die1},${die2},${die3}. ${just} = ${numbers[+coords[0]][+coords[1]]}`);
      }
      // switch player to 1
      setCurrentPlayer(1);
    }
    return;
  }

  // function to load saved game data
  async function loadData() {
    const response = await axios.get("http://localhost:5000/api/load");
    console.log(response.data)
    if (Object.keys(response.data).length === 2) {
      newGame();
    } 
    else {
      let data = response.data;
      setNumbers(data.nums);
      setStatus(data.status);
      setPoints1(data.points1);
      setPoints2(data.points2);
      setComputerMode(data.computerMode);
      setCurrentPlayer(data.currentPlayer);
      setKeys(data.keys);
      setUsed(data.used);
      setIndices(data.indices);
      setUseCount(data.useCount);
      setInvalidExpr(data.invalidExpr);
      setDisplay(data.display);
    }
    return;
  }

  // function to create a new game
  async function newGame() {
    const response = await axios.get("http://localhost:5000/api/new");
    // new game due to no saved state
    setPoints1(100);
    setPoints2(100);
    setNumbers(response.data.nums);
    setStatus([Array(10).fill(0),Array(10).fill(0),
              Array(10).fill(0),Array(10).fill(0),
              Array(10).fill(0),Array(10).fill(0),
              Array(10).fill(0),Array(10).fill(0),
              Array(10).fill(0),Array(10).fill(0)]);
    setCurrentPlayer(1);
    setComputerMode(response.data.computerMode);
    setWin(false);
    setWinSeq([]);
    setKeys([getRandomInt(1,13),getRandomInt(1,13),getRandomInt(1,13),"+","-","*","/","^","(",")"]);
    setUsed([]);
    setIndices([]);
    setUseCount(Array(10).fill(0));
    setInvalidExpr(false);
    setDisplay("---");
    return;
  }

  // get the board and computerMode only the first time
  useEffect(() => {
    loadData();
  }, []);

  // get the dice every time player changes, and additionally play a machine turn if relevant.
  useEffect(() => {
    let thisKeys = keys.slice();
    thisKeys[0] = getRandomInt(1,13);
    thisKeys[1] = getRandomInt(1,13);
    thisKeys[2] = getRandomInt(1,13);
    setKeys(thisKeys.slice());
    // if current player is 2, and computermode (checked by function), machine plays its turn
    handleMachineTurn(thisKeys[0], thisKeys[1], thisKeys[2]);
  }, [currentPlayer]);

  // function to save game data
  function saveData() {
    let data = {"currentPlayer": currentPlayer,
                "keys": keys,
                "used": used,
                "indices": indices,
                "useCount": useCount,
                "invalidExpr": invalidExpr,
                "display": display};
    axios.post("http://localhost:5000/api/save", data);
    alert("Progress saved!");
    return;
  }


  return (
    <>
    <h3 style={{color: "black", backgroundColor: lightcolors[currentPlayer], borderStyle:"solid none solid none", 
                borderColor: darkcolors[currentPlayer]}}>
      { win ? (currentPlayer == 1 ? `${computerMode ? "Human" : "Player 1"} Wins!`: `${computerMode ? "Computer" : "Player 2"} Wins!`) : 
              `Current Player: ${computerMode ? (currentPlayer == 1 ? "Human" : "Computer") : `${currentPlayer}`}`}
    </h3>
    <button style={{backgroundColor: win && currentPlayer==1 ? (winSeq.length == 0 ? darkcolors[1] : lightcolors[1]) : lightcolors[1], 
                    color: win && currentPlayer==1 ? (winSeq.length == 0 ? "white" : "black") : "black",
                    fontSize: "21px"}}>{points1}</button>
    <button style={{backgroundColor: win && currentPlayer==2 ? (winSeq.length == 0 ? darkcolors[2] : lightcolors[2]) : lightcolors[2], 
                    color: win && currentPlayer==2 ? (winSeq.length == 0 ? "white" : "black") : "black",
                    fontSize: "21px"}}>{points2}</button>
    <br></br>
    <br></br>
    <Board sq_stat_grid={status} value_grid={numbers} win={win} winSeq={winSeq}></Board>
    <br></br>
    <p style={{backgroundColor: "#e6e6e6", fontSize: "22px"}}>{display}</p>
    <p style={{color: "red", fontSize: "18px"}} hidden={!invalidExpr}>INVALID EXPRESSION</p>
    <Keyboard won={win} keys={keys} counts={useCount} comp={computerMode && currentPlayer==2} 
              handler={handleKeyboardPress}></Keyboard>
    <button onClick={handleBackspace} style={{backgroundColor: "#a9f58e", fontSize: "21px"}} 
            disabled={win || (computerMode && currentPlayer==2)} id="backspace" type="button">Backspace</button>
    <button onClick={handleEnter} style={{backgroundColor: "#fca9f8", fontSize: "21px"}} 
            disabled={used.length == 0 || win || (computerMode && currentPlayer==2)} id="enter" type="button">Enter</button>
    <button onClick={handlePass} style={{backgroundColor: "#f2cb57", fontSize: "21px"}} 
            disabled={win || (computerMode && currentPlayer==2)} id="pass" type="button">Pass</button>
    <button onClick={handleClear} style={{backgroundColor: "gray", fontSize: "21px"}} 
            disabled={win || (computerMode && currentPlayer==2)} id="clear" type="button">Clear</button>
    <br></br>
    <br></br>
    <button onClick={saveData} style={{backgroundColor: "#daaeeb", fontSize: "21px"}} 
            disabled={win || (computerMode && currentPlayer==2)}>Save</button>
    <button onClick={newGame} style={{backgroundColor: "#daaeeb", fontSize: "21px"}}>New Game</button>
    </>
  )
}

// component for the whole 10x10 board
function Board({sq_stat_grid, value_grid, win, winSeq}) {
  return (
    <>
      <Row sq_stati={sq_stat_grid[0]} values={value_grid[0]} win={win} winSeq={winSeq}></Row><br></br>
      <Row sq_stati={sq_stat_grid[1]} values={value_grid[1]} win={win} winSeq={winSeq}></Row><br></br>
      <Row sq_stati={sq_stat_grid[2]} values={value_grid[2]} win={win} winSeq={winSeq}></Row><br></br>
      <Row sq_stati={sq_stat_grid[3]} values={value_grid[3]} win={win} winSeq={winSeq}></Row><br></br>
      <Row sq_stati={sq_stat_grid[4]} values={value_grid[4]} win={win} winSeq={winSeq}></Row><br></br>
      <Row sq_stati={sq_stat_grid[5]} values={value_grid[5]} win={win} winSeq={winSeq}></Row><br></br>
      <Row sq_stati={sq_stat_grid[6]} values={value_grid[6]} win={win} winSeq={winSeq}></Row><br></br>
      <Row sq_stati={sq_stat_grid[7]} values={value_grid[7]} win={win} winSeq={winSeq}></Row><br></br>
      <Row sq_stati={sq_stat_grid[8]} values={value_grid[8]} win={win} winSeq={winSeq}></Row><br></br>
      <Row sq_stati={sq_stat_grid[9]} values={value_grid[9]} win={win} winSeq={winSeq}></Row><br></br>
    </>
  )
}

// component for a size 10 row of numbers
function Row({sq_stati, values, win, winSeq}) {
  return (
    <>
      <Square sq_status={sq_stati[0]} value={values[0]} win={win} winSeq={winSeq}></Square>
      <Square sq_status={sq_stati[1]} value={values[1]} win={win} winSeq={winSeq}></Square>
      <Square sq_status={sq_stati[2]} value={values[2]} win={win} winSeq={winSeq}></Square>
      <Square sq_status={sq_stati[3]} value={values[3]} win={win} winSeq={winSeq}></Square>
      <Square sq_status={sq_stati[4]} value={values[4]} win={win} winSeq={winSeq}></Square>
      <Square sq_status={sq_stati[5]} value={values[5]} win={win} winSeq={winSeq}></Square>
      <Square sq_status={sq_stati[6]} value={values[6]} win={win} winSeq={winSeq}></Square>
      <Square sq_status={sq_stati[7]} value={values[7]} win={win} winSeq={winSeq}></Square>
      <Square sq_status={sq_stati[8]} value={values[8]} win={win} winSeq={winSeq}></Square>
      <Square sq_status={sq_stati[9]} value={values[9]} win={win} winSeq={winSeq}></Square>
    </>
  )
}

// component for a single square
function Square({sq_status, value, win, winSeq}) {
  const regBgColors = ["white","#a8e0f0","#f5bebc"];
  const winBgColors = ["white","blue","red"];
  let st = {color: win && winSeq.includes(value) ? "white": "black",
            backgroundColor: win && winSeq.includes(value) ? winBgColors[sq_status]: regBgColors[sq_status],
            fontSize: "21px",
            width: "90px",
            height: "50px"
          };
  return <button id="num" type="button" style={st}>{value}</button>
}

// component to define the keyboard that displays your numbers and operators
function Keyboard({won, keys, counts, comp, handler}) {
  let numbStyle = {backgroundColor: "lavender", fontSize: "21px"};
  let opStyle = {backgroundColor: "yellow", fontSize: "21px"};  
  return (
    <>
    <button onClick={() => handler(keys[0],0)} style={numbStyle} disabled={comp||won||counts[0] == 1}>{keys[0]}</button>
    <button onClick={() => handler(keys[1],1)} style={numbStyle} disabled={comp||won||counts[1] == 1}>{keys[1]}</button>
    <button onClick={() => handler(keys[2],2)} style={numbStyle} disabled={comp||won||counts[2] == 1}>{keys[2]}</button>
    <button onClick={() => handler(keys[3],3)} style={opStyle} disabled={comp||won||counts[3] == 2}>{keys[3]}</button>
    <button onClick={() => handler(keys[4],4)} style={opStyle} disabled={comp||won||counts[4] == 2}>{keys[4]}</button>
    <button onClick={() => handler(keys[5],5)} style={opStyle} disabled={comp||won||counts[5] == 2}>{keys[5]}</button>
    <button onClick={() => handler(keys[6],6)} style={opStyle} disabled={comp||won||counts[6] == 2}>{keys[6]}</button>
    <button onClick={() => handler(keys[7],7)} style={opStyle} disabled={comp||won||counts[7] == 2}>{keys[7]}</button>
    <button onClick={() => handler(keys[8],8)} style={opStyle} disabled={comp||won||counts[8] == 1}>{keys[8]}</button>
    <button onClick={() => handler(keys[9],9)} style={opStyle} disabled={comp||won||counts[9] == 1}>{keys[9]}</button>
    </>
  )
}