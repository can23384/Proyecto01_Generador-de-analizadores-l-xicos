const fs = require("fs");

const SPECIAL_LITERAL_MAP = {
  "+": "§",
  "*": "¶",
  "?": "¤",
  "|": "¦",
  "(": "«",
  ")": "»",
  ".": "•",
  "#": "♯"
};
const ANY_SYMBOL = "∷";
const LITERAL_UNDERSCORE = "⌁";
const RULES = [
  {
    "index": 0,
    "priority": 0,
    "token_name": "SKIP",
    "original_regex": "espacioEnBlanco",
    "converted_regex": "(( |\t|\n)+)",
    "action_code": "",
    "skip": true,
    "dfa": {
      "alphabet": [
        "\t",
        "\n",
        " "
      ],
      "states": [
        "M0",
        "M1"
      ],
      "transitions": {
        "M0": {
          "\t": "M1",
          "\n": "M1",
          " ": "M1"
        },
        "M1": {
          "\t": "M1",
          "\n": "M1",
          " ": "M1"
        }
      },
      "start_state": "M0",
      "accepting_states": [
        "M1"
      ],
      "partitions": [
        [
          "S0"
        ],
        [
          "S1"
        ]
      ],
      "state_map": {
        "S0": "M0",
        "S1": "M1"
      },
      "original_completed": {
        "alphabet": [
          "\t",
          "\n",
          " "
        ],
        "states": [
          "S0",
          "S1"
        ],
        "transitions": {
          "S0": {
            "\t": "S1",
            "\n": "S1",
            " ": "S1"
          },
          "S1": {
            "\t": "S1",
            "\n": "S1",
            " ": "S1"
          }
        },
        "start_state": "S0",
        "accepting_states": [
          "S1"
        ],
        "sink_state": null
      }
    }
  },
  {
    "index": 1,
    "priority": 1,
    "token_name": "TOKEN_2",
    "original_regex": "identificador",
    "converted_regex": "((a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z)((a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z)|(0|1|2|3|4|5|6|7|8|9))*)",
    "action_code": "console.log(\"Identificador\\n\")",
    "skip": false,
    "dfa": {
      "alphabet": [
        "0",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
        "H",
        "I",
        "J",
        "K",
        "L",
        "M",
        "N",
        "O",
        "P",
        "Q",
        "R",
        "S",
        "T",
        "U",
        "V",
        "W",
        "X",
        "Y",
        "Z",
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
        "h",
        "i",
        "j",
        "k",
        "l",
        "m",
        "n",
        "o",
        "p",
        "q",
        "r",
        "s",
        "t",
        "u",
        "v",
        "w",
        "x",
        "y",
        "z"
      ],
      "states": [
        "M0",
        "M1"
      ],
      "transitions": {
        "M0": {
          "A": "M1",
          "B": "M1",
          "C": "M1",
          "D": "M1",
          "E": "M1",
          "F": "M1",
          "G": "M1",
          "H": "M1",
          "I": "M1",
          "J": "M1",
          "K": "M1",
          "L": "M1",
          "M": "M1",
          "N": "M1",
          "O": "M1",
          "P": "M1",
          "Q": "M1",
          "R": "M1",
          "S": "M1",
          "T": "M1",
          "U": "M1",
          "V": "M1",
          "W": "M1",
          "X": "M1",
          "Y": "M1",
          "Z": "M1",
          "a": "M1",
          "b": "M1",
          "c": "M1",
          "d": "M1",
          "e": "M1",
          "f": "M1",
          "g": "M1",
          "h": "M1",
          "i": "M1",
          "j": "M1",
          "k": "M1",
          "l": "M1",
          "m": "M1",
          "n": "M1",
          "o": "M1",
          "p": "M1",
          "q": "M1",
          "r": "M1",
          "s": "M1",
          "t": "M1",
          "u": "M1",
          "v": "M1",
          "w": "M1",
          "x": "M1",
          "y": "M1",
          "z": "M1"
        },
        "M1": {
          "0": "M1",
          "1": "M1",
          "2": "M1",
          "3": "M1",
          "4": "M1",
          "5": "M1",
          "6": "M1",
          "7": "M1",
          "8": "M1",
          "9": "M1",
          "A": "M1",
          "B": "M1",
          "C": "M1",
          "D": "M1",
          "E": "M1",
          "F": "M1",
          "G": "M1",
          "H": "M1",
          "I": "M1",
          "J": "M1",
          "K": "M1",
          "L": "M1",
          "M": "M1",
          "N": "M1",
          "O": "M1",
          "P": "M1",
          "Q": "M1",
          "R": "M1",
          "S": "M1",
          "T": "M1",
          "U": "M1",
          "V": "M1",
          "W": "M1",
          "X": "M1",
          "Y": "M1",
          "Z": "M1",
          "a": "M1",
          "b": "M1",
          "c": "M1",
          "d": "M1",
          "e": "M1",
          "f": "M1",
          "g": "M1",
          "h": "M1",
          "i": "M1",
          "j": "M1",
          "k": "M1",
          "l": "M1",
          "m": "M1",
          "n": "M1",
          "o": "M1",
          "p": "M1",
          "q": "M1",
          "r": "M1",
          "s": "M1",
          "t": "M1",
          "u": "M1",
          "v": "M1",
          "w": "M1",
          "x": "M1",
          "y": "M1",
          "z": "M1"
        }
      },
      "start_state": "M0",
      "accepting_states": [
        "M1"
      ],
      "partitions": [
        [
          "S0"
        ],
        [
          "S1"
        ]
      ],
      "state_map": {
        "S0": "M0",
        "S1": "M1",
        "POZO": null
      },
      "original_completed": {
        "alphabet": [
          "0",
          "1",
          "2",
          "3",
          "4",
          "5",
          "6",
          "7",
          "8",
          "9",
          "A",
          "B",
          "C",
          "D",
          "E",
          "F",
          "G",
          "H",
          "I",
          "J",
          "K",
          "L",
          "M",
          "N",
          "O",
          "P",
          "Q",
          "R",
          "S",
          "T",
          "U",
          "V",
          "W",
          "X",
          "Y",
          "Z",
          "a",
          "b",
          "c",
          "d",
          "e",
          "f",
          "g",
          "h",
          "i",
          "j",
          "k",
          "l",
          "m",
          "n",
          "o",
          "p",
          "q",
          "r",
          "s",
          "t",
          "u",
          "v",
          "w",
          "x",
          "y",
          "z"
        ],
        "states": [
          "POZO",
          "S0",
          "S1"
        ],
        "transitions": {
          "S0": {
            "A": "S1",
            "B": "S1",
            "C": "S1",
            "D": "S1",
            "E": "S1",
            "F": "S1",
            "G": "S1",
            "H": "S1",
            "I": "S1",
            "J": "S1",
            "K": "S1",
            "L": "S1",
            "M": "S1",
            "N": "S1",
            "O": "S1",
            "P": "S1",
            "Q": "S1",
            "R": "S1",
            "S": "S1",
            "T": "S1",
            "U": "S1",
            "V": "S1",
            "W": "S1",
            "X": "S1",
            "Y": "S1",
            "Z": "S1",
            "a": "S1",
            "b": "S1",
            "c": "S1",
            "d": "S1",
            "e": "S1",
            "f": "S1",
            "g": "S1",
            "h": "S1",
            "i": "S1",
            "j": "S1",
            "k": "S1",
            "l": "S1",
            "m": "S1",
            "n": "S1",
            "o": "S1",
            "p": "S1",
            "q": "S1",
            "r": "S1",
            "s": "S1",
            "t": "S1",
            "u": "S1",
            "v": "S1",
            "w": "S1",
            "x": "S1",
            "y": "S1",
            "z": "S1",
            "0": "POZO",
            "1": "POZO",
            "2": "POZO",
            "3": "POZO",
            "4": "POZO",
            "5": "POZO",
            "6": "POZO",
            "7": "POZO",
            "8": "POZO",
            "9": "POZO"
          },
          "S1": {
            "0": "S1",
            "1": "S1",
            "2": "S1",
            "3": "S1",
            "4": "S1",
            "5": "S1",
            "6": "S1",
            "7": "S1",
            "8": "S1",
            "9": "S1",
            "A": "S1",
            "B": "S1",
            "C": "S1",
            "D": "S1",
            "E": "S1",
            "F": "S1",
            "G": "S1",
            "H": "S1",
            "I": "S1",
            "J": "S1",
            "K": "S1",
            "L": "S1",
            "M": "S1",
            "N": "S1",
            "O": "S1",
            "P": "S1",
            "Q": "S1",
            "R": "S1",
            "S": "S1",
            "T": "S1",
            "U": "S1",
            "V": "S1",
            "W": "S1",
            "X": "S1",
            "Y": "S1",
            "Z": "S1",
            "a": "S1",
            "b": "S1",
            "c": "S1",
            "d": "S1",
            "e": "S1",
            "f": "S1",
            "g": "S1",
            "h": "S1",
            "i": "S1",
            "j": "S1",
            "k": "S1",
            "l": "S1",
            "m": "S1",
            "n": "S1",
            "o": "S1",
            "p": "S1",
            "q": "S1",
            "r": "S1",
            "s": "S1",
            "t": "S1",
            "u": "S1",
            "v": "S1",
            "w": "S1",
            "x": "S1",
            "y": "S1",
            "z": "S1"
          },
          "POZO": {
            "0": "POZO",
            "1": "POZO",
            "2": "POZO",
            "3": "POZO",
            "4": "POZO",
            "5": "POZO",
            "6": "POZO",
            "7": "POZO",
            "8": "POZO",
            "9": "POZO",
            "A": "POZO",
            "B": "POZO",
            "C": "POZO",
            "D": "POZO",
            "E": "POZO",
            "F": "POZO",
            "G": "POZO",
            "H": "POZO",
            "I": "POZO",
            "J": "POZO",
            "K": "POZO",
            "L": "POZO",
            "M": "POZO",
            "N": "POZO",
            "O": "POZO",
            "P": "POZO",
            "Q": "POZO",
            "R": "POZO",
            "S": "POZO",
            "T": "POZO",
            "U": "POZO",
            "V": "POZO",
            "W": "POZO",
            "X": "POZO",
            "Y": "POZO",
            "Z": "POZO",
            "a": "POZO",
            "b": "POZO",
            "c": "POZO",
            "d": "POZO",
            "e": "POZO",
            "f": "POZO",
            "g": "POZO",
            "h": "POZO",
            "i": "POZO",
            "j": "POZO",
            "k": "POZO",
            "l": "POZO",
            "m": "POZO",
            "n": "POZO",
            "o": "POZO",
            "p": "POZO",
            "q": "POZO",
            "r": "POZO",
            "s": "POZO",
            "t": "POZO",
            "u": "POZO",
            "v": "POZO",
            "w": "POZO",
            "x": "POZO",
            "y": "POZO",
            "z": "POZO"
          }
        },
        "start_state": "S0",
        "accepting_states": [
          "S1"
        ],
        "sink_state": "POZO"
      }
    }
  },
  {
    "index": 2,
    "priority": 2,
    "token_name": "TOKEN_3",
    "original_regex": "numero",
    "converted_regex": "(-?(0|1|2|3|4|5|6|7|8|9)+)",
    "action_code": "console.log(\"Número\\n\")",
    "skip": false,
    "dfa": {
      "alphabet": [
        "-",
        "0",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9"
      ],
      "states": [
        "M0",
        "M1",
        "M2"
      ],
      "transitions": {
        "M0": {
          "-": "M2",
          "0": "M1",
          "1": "M1",
          "2": "M1",
          "3": "M1",
          "4": "M1",
          "5": "M1",
          "6": "M1",
          "7": "M1",
          "8": "M1",
          "9": "M1"
        },
        "M1": {
          "0": "M1",
          "1": "M1",
          "2": "M1",
          "3": "M1",
          "4": "M1",
          "5": "M1",
          "6": "M1",
          "7": "M1",
          "8": "M1",
          "9": "M1"
        },
        "M2": {
          "0": "M1",
          "1": "M1",
          "2": "M1",
          "3": "M1",
          "4": "M1",
          "5": "M1",
          "6": "M1",
          "7": "M1",
          "8": "M1",
          "9": "M1"
        }
      },
      "start_state": "M0",
      "accepting_states": [
        "M1"
      ],
      "partitions": [
        [
          "S0"
        ],
        [
          "S2"
        ],
        [
          "S1"
        ]
      ],
      "state_map": {
        "S0": "M0",
        "S2": "M1",
        "S1": "M2",
        "POZO": null
      },
      "original_completed": {
        "alphabet": [
          "-",
          "0",
          "1",
          "2",
          "3",
          "4",
          "5",
          "6",
          "7",
          "8",
          "9"
        ],
        "states": [
          "POZO",
          "S0",
          "S1",
          "S2"
        ],
        "transitions": {
          "S0": {
            "-": "S1",
            "0": "S2",
            "1": "S2",
            "2": "S2",
            "3": "S2",
            "4": "S2",
            "5": "S2",
            "6": "S2",
            "7": "S2",
            "8": "S2",
            "9": "S2"
          },
          "S1": {
            "0": "S2",
            "1": "S2",
            "2": "S2",
            "3": "S2",
            "4": "S2",
            "5": "S2",
            "6": "S2",
            "7": "S2",
            "8": "S2",
            "9": "S2",
            "-": "POZO"
          },
          "S2": {
            "0": "S2",
            "1": "S2",
            "2": "S2",
            "3": "S2",
            "4": "S2",
            "5": "S2",
            "6": "S2",
            "7": "S2",
            "8": "S2",
            "9": "S2",
            "-": "POZO"
          },
          "POZO": {
            "-": "POZO",
            "0": "POZO",
            "1": "POZO",
            "2": "POZO",
            "3": "POZO",
            "4": "POZO",
            "5": "POZO",
            "6": "POZO",
            "7": "POZO",
            "8": "POZO",
            "9": "POZO"
          }
        },
        "start_state": "S0",
        "accepting_states": [
          "S2"
        ],
        "sink_state": "POZO"
      }
    }
  },
  {
    "index": 3,
    "priority": 3,
    "token_name": "TOKEN_4",
    "original_regex": "'+'",
    "converted_regex": "§",
    "action_code": "console.log(\"Operador de suma\\n\")",
    "skip": false,
    "dfa": {
      "alphabet": [
        "§"
      ],
      "states": [
        "M0",
        "M1"
      ],
      "transitions": {
        "M0": {
          "§": "M1"
        },
        "M1": {}
      },
      "start_state": "M0",
      "accepting_states": [
        "M1"
      ],
      "partitions": [
        [
          "S0"
        ],
        [
          "S1"
        ]
      ],
      "state_map": {
        "S0": "M0",
        "S1": "M1",
        "POZO": null
      },
      "original_completed": {
        "alphabet": [
          "§"
        ],
        "states": [
          "POZO",
          "S0",
          "S1"
        ],
        "transitions": {
          "S0": {
            "§": "S1"
          },
          "S1": {
            "§": "POZO"
          },
          "POZO": {
            "§": "POZO"
          }
        },
        "start_state": "S0",
        "accepting_states": [
          "S1"
        ],
        "sink_state": "POZO"
      }
    }
  },
  {
    "index": 4,
    "priority": 4,
    "token_name": "TOKEN_5",
    "original_regex": "'*'",
    "converted_regex": "¶",
    "action_code": "console.log(\"Operador de multiplicación\\n\")",
    "skip": false,
    "dfa": {
      "alphabet": [
        "¶"
      ],
      "states": [
        "M0",
        "M1"
      ],
      "transitions": {
        "M0": {
          "¶": "M1"
        },
        "M1": {}
      },
      "start_state": "M0",
      "accepting_states": [
        "M1"
      ],
      "partitions": [
        [
          "S0"
        ],
        [
          "S1"
        ]
      ],
      "state_map": {
        "S0": "M0",
        "S1": "M1",
        "POZO": null
      },
      "original_completed": {
        "alphabet": [
          "¶"
        ],
        "states": [
          "POZO",
          "S0",
          "S1"
        ],
        "transitions": {
          "S0": {
            "¶": "S1"
          },
          "S1": {
            "¶": "POZO"
          },
          "POZO": {
            "¶": "POZO"
          }
        },
        "start_state": "S0",
        "accepting_states": [
          "S1"
        ],
        "sink_state": "POZO"
      }
    }
  },
  {
    "index": 5,
    "priority": 5,
    "token_name": "TOKEN_6",
    "original_regex": "'='",
    "converted_regex": "=",
    "action_code": "console.log(\"Operador de asignación\\n\")",
    "skip": false,
    "dfa": {
      "alphabet": [
        "="
      ],
      "states": [
        "M0",
        "M1"
      ],
      "transitions": {
        "M0": {
          "=": "M1"
        },
        "M1": {}
      },
      "start_state": "M0",
      "accepting_states": [
        "M1"
      ],
      "partitions": [
        [
          "S0"
        ],
        [
          "S1"
        ]
      ],
      "state_map": {
        "S0": "M0",
        "S1": "M1",
        "POZO": null
      },
      "original_completed": {
        "alphabet": [
          "="
        ],
        "states": [
          "POZO",
          "S0",
          "S1"
        ],
        "transitions": {
          "S0": {
            "=": "S1"
          },
          "S1": {
            "=": "POZO"
          },
          "POZO": {
            "=": "POZO"
          }
        },
        "start_state": "S0",
        "accepting_states": [
          "S1"
        ],
        "sink_state": "POZO"
      }
    }
  }
];
const EOF_RULE = null;


function normalizeInputChar(ch) {
    if (ch === "_") {
        return LITERAL_UNDERSCORE;
    }

    return Object.prototype.hasOwnProperty.call(SPECIAL_LITERAL_MAP, ch)
        ? SPECIAL_LITERAL_MAP[ch]
        : ch;
}


function stepDfa(dfa, currentState, rawChar) {
    const transitions = dfa.transitions[currentState] || {};
    const normalized = normalizeInputChar(rawChar);

    if (Object.prototype.hasOwnProperty.call(transitions, normalized)) {
        return transitions[normalized];
    }

    if (Object.prototype.hasOwnProperty.call(transitions, ANY_SYMBOL)) {
        return transitions[ANY_SYMBOL];
    }

    return null;
}


function isWhitespace(ch) {
    return ch === " " || ch === "\t" || ch === "\n" || ch === "\r" || ch === "\f" || ch === "\v";
}


function normalizeNewlines(text) {
    let out = "";
    let i = 0;

    while (i < text.length) {
        const ch = text[i];

        if (ch === "\r") {
            if (i + 1 < text.length && text[i + 1] === "\n") {
                out += "\n";
                i += 2;
            } else {
                out += "\n";
                i += 1;
            }
            continue;
        }

        out += ch;
        i += 1;
    }

    return out;
}


function matchRule(dfa, text, startPos) {
    let currentState = dfa.start_state;
    let lastAcceptPos = -1;

    let pos = startPos;

    while (pos < text.length) {
        const nextState = stepDfa(dfa, currentState, text[pos]);

        if (nextState === null) {
            break;
        }

        currentState = nextState;
        pos += 1;

        if (dfa.accepting_states.includes(currentState)) {
            lastAcceptPos = pos;
        }
    }

    if (lastAcceptPos === -1) {
        return 0;
    }

    return lastAcceptPos - startPos;
}


function updatePosition(lexeme, line, column) {
    for (const ch of lexeme) {
        if (ch === "\n") {
            line += 1;
            column = 1;
        } else {
            column += 1;
        }
    }

    return { line, column };
}


function consumeInvalidLexeme(text, startPos) {
    let pos = startPos;

    if (pos >= text.length) {
        return pos;
    }

    if (isWhitespace(text[pos])) {
        return pos + 1;
    }

    while (pos < text.length && !isWhitespace(text[pos])) {
        pos += 1;
    }

    return pos;
}


function runAction(actionCode, lexeme, line, column) {
    if (!actionCode || !actionCode.trim()) {
        return null;
    }

    try {
        const fn = new Function("lexeme", "lxm", "line", "column", actionCode);
        return fn(lexeme, lexeme, line, column);
    } catch (error) {
        console.error("Error ejecutando acción:", actionCode);
        console.error(error.message);
        return null;
    }
}


function tokenizeText(text) {
    const tokens = [];
    const errors = [];

    let pos = 0;
    let line = 1;
    let column = 1;

    while (pos < text.length) {
        let bestRule = null;
        let bestLength = 0;

        for (const rule of RULES) {
            const length = matchRule(rule.dfa, text, pos);

            if (length > bestLength) {
                bestLength = length;
                bestRule = rule;
            } else if (length === bestLength && length > 0) {
                if (bestRule === null || rule.priority < bestRule.priority) {
                    bestRule = rule;
                }
            }
        }

        if (bestRule === null || bestLength === 0) {
            const invalidEnd = consumeInvalidLexeme(text, pos);
            const badLexeme = text.slice(pos, invalidEnd);

            errors.push({
                line,
                column,
                lexeme: badLexeme,
                formatted:
                    `[ERROR LÉXICO] Línea ${line}, Columna ${column}: ` +
                    `${badLexeme.length > 1 ? "token no reconocido" : "carácter no reconocido"} ` +
                    `${JSON.stringify(badLexeme)}`
            });

            const updatedError = updatePosition(badLexeme, line, column);
            line = updatedError.line;
            column = updatedError.column;
            pos = invalidEnd;
            continue;
        }

        const lexeme = text.slice(pos, pos + bestLength);

        const tokenInfo = {
            rule_index: bestRule.index,
            token_name: bestRule.token_name,
            lexeme,
            line,
            column,
            regex: bestRule.original_regex,
            action_code: bestRule.action_code
        };

        const actionResult = runAction(bestRule.action_code, lexeme, line, column);

        if (!bestRule.skip) {
            if (typeof actionResult === "string" && actionResult.trim() !== "") {
                tokenInfo.token_name = actionResult;
            }

            tokens.push(tokenInfo);
        }

        const updated = updatePosition(lexeme, line, column);
        line = updated.line;
        column = updated.column;
        pos += bestLength;
    }

    if (EOF_RULE && !EOF_RULE.skip) {
        const eofResult = runAction(EOF_RULE.action_code, "", line, column);

        const eofToken = {
            rule_index: EOF_RULE.index,
            token_name:
                (typeof eofResult === "string" && eofResult.trim() !== "")
                    ? eofResult
                    : EOF_RULE.token_name,
            lexeme: "",
            line,
            column,
            regex: "eof",
            action_code: EOF_RULE.action_code
        };

        tokens.push(eofToken);
    }

    return { tokens, errors };
}


function printResults(result) {
    console.log("\n============================================================");
    console.log("TOKENS ENCONTRADOS");
    console.log("============================================================");

    for (const token of result.tokens) {
        console.log(
            `[TOKEN] Línea ${token.line}, Columna ${token.column}: ` +
            `${token.token_name} -> ${JSON.stringify(token.lexeme)}`
        );
    }

    console.log("\n============================================================");
    console.log("ERRORES LÉXICOS");
    console.log("============================================================");

    if (result.errors.length === 0) {
        console.log("No se encontraron errores léxicos.");
    } else {
        for (const err of result.errors) {
            console.log(err.formatted);
        }
    }
}


function main() {
    if (process.argv.length < 3) {
        console.log("Uso: node lexer_generado.js <archivo_entrada>");
        return;
    }

    const inputPath = process.argv[2];
    const rawText = fs.readFileSync(inputPath, "utf8");
    const text = normalizeNewlines(rawText);

    const result = tokenizeText(text);
    printResults(result);
}


module.exports = {
    tokenizeText,
    normalizeNewlines,
    printResults,
    RULES,
    EOF_RULE
};


if (require.main === module) {
    main();
}
