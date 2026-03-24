from collections import deque
from dataclasses import dataclass
from typing import List, Optional, Dict, Set, FrozenSet

# ============================================================
# Laboratorio 02
# Conversión directa de una expresión regular a un AFD,
# minimización del AFD y simulación del AFD minimizado.
#
# Soporta operadores:
#   |   unión
#   concatenación implícita (internamente usa 'CONCAT')
#   *   cerradura de Kleene
#   +   cerradura positiva
#   ?   opcional
#   \x  símbolo escapado (ej. \|, \*, \., \(, \), \\)
#   ε   epsilon (cadena vacía)
#
# No usa librerías de expresiones regulares.
# ============================================================

UNION = 'UNION'
CONCAT = 'CONCAT'
STAR = 'STAR'
PLUS = 'PLUS'
OPTIONAL = 'OPTIONAL'
LPAREN = 'LPAREN'
RPAREN = 'RPAREN'
SYMBOL = 'SYMBOL'
EPSILON = 'EPSILON'
ENDMARK = 'ENDMARK'

UNARY_TYPES = {STAR, PLUS, OPTIONAL}
BINARY_TYPES = {UNION, CONCAT}


@dataclass(frozen=True)
class Token:
    type: str
    value: str

    def __repr__(self):
        return f"Token({self.type}, {self.value!r})"


class Node:
    def __init__(self, value, left=None, right=None, position=None, token=None):
        self.value = value
        self.left = left
        self.right = right
        self.position = position
        self.token = token

        self.nullable = False
        self.firstpos: Set[int] = set()
        self.lastpos: Set[int] = set()

    def __repr__(self):
        return f"Node({self.value})"


# ------------------------------------------------------------
# Tokenización
# ------------------------------------------------------------
# ============================================================
# FASE 1: TOKENIZACIÓN - Convierte string a tokens
# ============================================================
# Convierte cadena de expresión regular a lista de tokens
# Identifica operadores (|, *, +, ?), paréntesis y símbolos literales
def tokenize(regex: str) -> List[Token]:
    if regex is None or regex == '':
        raise ValueError('La expresión regular no puede estar vacía.')

    tokens: List[Token] = []
    i = 0
    while i < len(regex):
        c = regex[i]

        if c == '\\':
            if i + 1 >= len(regex):
                raise ValueError('La expresión termina con una barra invertida sin escapar.')
            tokens.append(Token(SYMBOL, regex[i + 1]))
            i += 2
            continue

        if c == '|':
            tokens.append(Token(UNION, c))
        elif c == '*':
            tokens.append(Token(STAR, c))
        elif c == '+':
            tokens.append(Token(PLUS, c))
        elif c == '?':
            tokens.append(Token(OPTIONAL, c))
        elif c == '(':
            tokens.append(Token(LPAREN, c))
        elif c == ')':
            tokens.append(Token(RPAREN, c))
        elif c == 'ε':
            tokens.append(Token(EPSILON, c))
        else:
            tokens.append(Token(SYMBOL, c))
        i += 1

    return tokens


# ============================================================
# FASE 2: CONVERTIDOR INFIX→POSTFIJO - Algoritmo Shunting Yard
# ============================================================
# Verifica si un token puede ser el final de un átomo (necesita concatenación después)
def can_end_atom(token: Token) -> bool:
    return token.type in {SYMBOL, EPSILON, RPAREN, STAR, PLUS, OPTIONAL}


# Verifica si un token puede ser el inicio de un átomo (puede tener concatenación antes)
def can_start_atom(token: Token) -> bool:
    return token.type in {SYMBOL, EPSILON, LPAREN}


# Inserta operadores de concatenación explícita entre símbolos adyacentes
# Ej: abc -> a·b·c (necesario para convertir a árbol sintáctico)
def insert_concat(tokens: List[Token]) -> List[Token]:
    result: List[Token] = []
    for i, t1 in enumerate(tokens):
        result.append(t1)
        if i + 1 < len(tokens):
            t2 = tokens[i + 1]
            if can_end_atom(t1) and can_start_atom(t2):
                result.append(Token(CONCAT, '·'))
    return result


# ------------------------------------------------------------
# Infix -> postfix (Shunting Yard)
# ------------------------------------------------------------
# ============================================================
# INFIX → POSTFIJO (Shunting Yard Algorithm)
# ============================================================
# Convierte expresión infix a postfija usando algoritmo Shunting Yard
# Infix: a|b* → Postfija: ab*|
def to_postfix(tokens: List[Token]) -> List[Token]:
    precedence = {
        UNION: 1,
        CONCAT: 2,
        STAR: 3,
        PLUS: 3,
        OPTIONAL: 3,
    }

    output: List[Token] = []
    stack: List[Token] = []

    for token in tokens:
        if token.type in {SYMBOL, EPSILON, ENDMARK}:
            output.append(token)
        elif token.type == LPAREN:
            stack.append(token)
        elif token.type == RPAREN:
            while stack and stack[-1].type != LPAREN:
                output.append(stack.pop())
            if not stack:
                raise ValueError('Paréntesis desbalanceados.')
            stack.pop()
        else:
            while (
                stack and stack[-1].type != LPAREN and
                precedence.get(stack[-1].type, 0) >= precedence.get(token.type, 0)
            ):
                output.append(stack.pop())
            stack.append(token)

    while stack:
        if stack[-1].type in {LPAREN, RPAREN}:
            raise ValueError('Paréntesis desbalanceados.')
        output.append(stack.pop())

    return output


# ------------------------------------------------------------
# Árbol sintáctico
# ------------------------------------------------------------
# ============================================================
# FASE 3: CONSTRUCCIÓN DEL ÁRBOL SINTÁCTICO
# ============================================================
# Construye árbol sintáctico desde expresión postfija
# Cada símbolo obtiene un número de posición para el algoritmo de construcción del AFD
def build_syntax_tree(postfix: List[Token]):
    stack: List[Node] = []
    pos_counter = 1
    pos_to_symbol: Dict[int, str] = {}

    for token in postfix:
        if token.type == SYMBOL:
            node = Node(token.value, position=pos_counter, token=token)
            pos_to_symbol[pos_counter] = token.value
            pos_counter += 1
            stack.append(node)

        elif token.type == EPSILON:
            node = Node('ε', token=token)
            stack.append(node)

        elif token.type == ENDMARK:
            node = Node('#', position=pos_counter, token=token)
            pos_to_symbol[pos_counter] = '#'
            pos_counter += 1
            stack.append(node)

        elif token.type in UNARY_TYPES:
            if not stack:
                raise ValueError(f"Operador unario inválido: {token.value}")
            child = stack.pop()
            stack.append(Node(token.type, left=child, token=token))

        elif token.type in BINARY_TYPES:
            if len(stack) < 2:
                raise ValueError(f"Operador binario inválido: {token.value}")
            right = stack.pop()
            left = stack.pop()
            stack.append(Node(token.type, left=left, right=right, token=token))

        else:
            raise ValueError(f'Token desconocido: {token}')

    if len(stack) != 1:
        raise ValueError('La expresión regular es inválida.')

    return stack[0], pos_to_symbol


# ------------------------------------------------------------
# nullable, firstpos, lastpos, followpos
# ------------------------------------------------------------
# ============================================================
# FASE 4: CÁLCULO DE FUNCIONES - nullable, firstpos, lastpos
# ============================================================
# Calcula funciones del árbol de sintaxis: nullable, firstpos, lastpos, followpos
# Estos datos se usan para construir directamente el AFD sin generar NFA primero
def compute_functions(node: Optional[Node], followpos: Dict[int, Set[int]]):
    if node is None:
        return

    # Hoja epsilon
    if node.value == 'ε' and node.left is None and node.right is None:
        node.nullable = True
        node.firstpos = set()
        node.lastpos = set()
        return

    # Hoja símbolo / #
    if node.left is None and node.right is None:
        node.nullable = False
        node.firstpos = {node.position}
        node.lastpos = {node.position}
        followpos.setdefault(node.position, set())
        return

    # Unario
    if node.value in UNARY_TYPES:
        compute_functions(node.left, followpos)
        child = node.left

        if node.value == STAR:
            node.nullable = True
            node.firstpos = set(child.firstpos)
            node.lastpos = set(child.lastpos)
            for i in child.lastpos:
                followpos[i].update(child.firstpos)

        elif node.value == PLUS:
            node.nullable = child.nullable
            node.firstpos = set(child.firstpos)
            node.lastpos = set(child.lastpos)
            for i in child.lastpos:
                followpos[i].update(child.firstpos)

        elif node.value == OPTIONAL:
            node.nullable = True
            node.firstpos = set(child.firstpos)
            node.lastpos = set(child.lastpos)
        return

    # Binario
    compute_functions(node.left, followpos)
    compute_functions(node.right, followpos)

    if node.value == UNION:
        node.nullable = node.left.nullable or node.right.nullable
        node.firstpos = node.left.firstpos | node.right.firstpos
        node.lastpos = node.left.lastpos | node.right.lastpos

    elif node.value == CONCAT:
        node.nullable = node.left.nullable and node.right.nullable

        if node.left.nullable:
            node.firstpos = node.left.firstpos | node.right.firstpos
        else:
            node.firstpos = set(node.left.firstpos)

        if node.right.nullable:
            node.lastpos = node.left.lastpos | node.right.lastpos
        else:
            node.lastpos = set(node.right.lastpos)

        for i in node.left.lastpos:
            followpos[i].update(node.right.firstpos)


# ------------------------------------------------------------
# Construcción del AFD directo
# ------------------------------------------------------------
# ============================================================
# FASE 5: CONSTRUCCIÓN DEL AFD - Método Directo de Brzozowski
# ============================================================
# Construye AFD directamente desde el árbol usando el método de Brzozowski
# Cada estado represente un conjunto de posiciones (firstpos de algún nodo)
def build_dfa(root: Node, followpos: Dict[int, Set[int]], pos_to_symbol: Dict[int, str]):
    alphabet = sorted({sym for sym in pos_to_symbol.values() if sym != '#'})

    hash_pos = None
    for pos, sym in pos_to_symbol.items():
        if sym == '#':
            hash_pos = pos
            break
    if hash_pos is None:
        raise ValueError("No se encontró el símbolo final '#'.")

    start_state: FrozenSet[int] = frozenset(root.firstpos)
    states: List[FrozenSet[int]] = []
    state_ids: Dict[FrozenSet[int], str] = {}
    transitions: Dict[str, Dict[str, str]] = {}
    accepting_states: Set[str] = set()

    queue = deque([start_state])
    state_ids[start_state] = 'S0'
    states.append(start_state)

    while queue:
        current = queue.popleft()
        current_name = state_ids[current]
        transitions[current_name] = {}

        if hash_pos in current:
            accepting_states.add(current_name)

        for a in alphabet:
            u: Set[int] = set()
            for p in current:
                if pos_to_symbol[p] == a:
                    u.update(followpos[p])
            if u:
                uf = frozenset(u)
                if uf not in state_ids:
                    state_ids[uf] = f'S{len(state_ids)}'
                    states.append(uf)
                    queue.append(uf)
                transitions[current_name][a] = state_ids[uf]

    return {
        'alphabet': alphabet,
        'states': states,
        'state_ids': state_ids,
        'transitions': transitions,
        'start_state': 'S0',
        'accepting_states': accepting_states,
        'hash_pos': hash_pos,
    }


# ------------------------------------------------------------
# Minimización del AFD
# ------------------------------------------------------------
# ============================================================
# FASE 6: MINIMIZACIÓN DEL AFD - Particionamiento Iterativo
# ============================================================
# Cuenta transiciones totales en el AFD (útil para comparar antes/después minimización)
def count_transitions(dfa):
    return sum(len(trans) for trans in dfa['transitions'].values())


# ============================================================
# COMPLETACIÓN Y MINIMIZACIÓN DEL AFD
# ============================================================
# Completa el AFD añadiendo un estado sumidero para transiciones indefinidas
# Necesario para la minimización (requiere AFD completo)
def complete_dfa(dfa):
    alphabet = list(dfa['alphabet'])
    transitions = {state: dict(trans) for state, trans in dfa['transitions'].items()}
    accepting = set(dfa['accepting_states'])

    all_states = set(transitions.keys()) | {dfa['start_state']}
    for trans in dfa['transitions'].values():
        all_states.update(trans.values())

    sink_needed = False
    for state in list(all_states):
        transitions.setdefault(state, {})
        for symbol in alphabet:
            if symbol not in transitions[state]:
                sink_needed = True

    sink_name = None
    if sink_needed:
        base = 'POZO'
        sink_name = base
        counter = 0
        while sink_name in all_states:
            counter += 1
            sink_name = f'{base}_{counter}'

        transitions[sink_name] = {symbol: sink_name for symbol in alphabet}
        all_states.add(sink_name)

        for state in list(all_states):
            transitions.setdefault(state, {})
            for symbol in alphabet:
                if symbol not in transitions[state]:
                    transitions[state][symbol] = sink_name

    return {
        'alphabet': alphabet,
        'states': sorted(all_states),
        'transitions': transitions,
        'start_state': dfa['start_state'],
        'accepting_states': accepting,
        'sink_state': sink_name,
    }


# Calcula estados alcanzables desde el estado inicial (BFS)
def reachable_states(dfa):
    visited = set()
    queue = deque([dfa['start_state']])

    while queue:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)

        for nxt in dfa['transitions'].get(current, {}).values():
            if nxt not in visited:
                queue.append(nxt)

    return visited


# Minimiza el AFD usando particionamiento (algoritmo similar a Hopcroft)
# Fusiona estados equivalentes que tienen el mismo comportamiento
def minimize_dfa(dfa):
    completed = complete_dfa(dfa)
    reachable = reachable_states(completed)

    alphabet = completed['alphabet']
    transitions = {
        state: {sym: dst for sym, dst in completed['transitions'][state].items()}
        for state in reachable
    }
    accepting = completed['accepting_states'] & reachable
    start_state = completed['start_state']

    non_accepting = reachable - accepting
    partitions = []
    if accepting:
        partitions.append(set(accepting))
    if non_accepting:
        partitions.append(set(non_accepting))

    if not partitions:
        raise ValueError('No se pudo construir la partición inicial.')

    changed = True
    while changed:
        changed = False
        new_partitions = []

        for group in partitions:
            signatures = {}
            for state in group:
                signature = []
                for symbol in alphabet:
                    dest = transitions[state][symbol]
                    dest_group_index = next(
                        i for i, part in enumerate(partitions) if dest in part
                    )
                    signature.append(dest_group_index)
                signature = tuple(signature)
                signatures.setdefault(signature, set()).add(state)

            if len(signatures) == 1:
                new_partitions.append(group)
            else:
                changed = True
                new_partitions.extend(signatures.values())

        partitions = new_partitions

    original_reachable = reachable_states({
        'alphabet': dfa['alphabet'],
        'transitions': dfa['transitions'],
        'start_state': dfa['start_state'],
    })

    sink_state = completed.get('sink_state')

    ordered_partitions = []
    start_partition = next(part for part in partitions if start_state in part)
    ordered_partitions.append(start_partition)
    for part in partitions:
        if part is not start_partition:
            ordered_partitions.append(part)

    visible_partitions = []
    hidden_sink_partition = None
    for part in ordered_partitions:
        if part & original_reachable:
            visible_partitions.append(part)
        elif sink_state is not None and sink_state in part:
            hidden_sink_partition = part

    state_name_of_partition = {}
    for index, part in enumerate(visible_partitions):
        state_name_of_partition[frozenset(part)] = f'M{index}'

    state_to_min = {}
    for part in visible_partitions:
        min_name = state_name_of_partition[frozenset(part)]
        for state in part:
            state_to_min[state] = min_name

    if hidden_sink_partition is not None:
        for state in hidden_sink_partition:
            state_to_min[state] = None

    min_transitions = {}
    min_accepting = set()
    min_states = []

    for part in visible_partitions:
        rep = next(iter(part))
        min_name = state_to_min[rep]
        min_states.append(min_name)
        min_transitions[min_name] = {}

        if part & accepting:
            min_accepting.add(min_name)

        for symbol in alphabet:
            dest = transitions[rep][symbol]
            dest_min = state_to_min[dest]
            if dest_min is not None:
                min_transitions[min_name][symbol] = dest_min

    return {
        'alphabet': alphabet,
        'states': min_states,
        'transitions': min_transitions,
        'start_state': state_to_min[start_state],
        'accepting_states': min_accepting,
        'partitions': [sorted(part) for part in visible_partitions],
        'state_map': state_to_min,
        'original_completed': completed,
    }


# ------------------------------------------------------------
# Simulación del AFD
# ------------------------------------------------------------
# ============================================================
# FASE 7: SIMULACIÓN DEL AFD
# ============================================================
# Simula el AFD: procesa una cadena símbolo a símbolo
# Retorna True si la cadena es aceptada (termina en estado aceptante)
def simulate_dfa(dfa, string: str) -> bool:
    current = dfa['start_state']
    for ch in string:
        if ch not in dfa['alphabet']:
            return False
        nxt = dfa['transitions'].get(current, {}).get(ch)
        if nxt is None:
            return False
        current = nxt
    return current in dfa['accepting_states']


# ------------------------------------------------------------
# Utilidades de impresión
# ------------------------------------------------------------
# ============================================================
# UTILIDADES DE IMPRESIÓN Y DEPURACIÓN
# ============================================================
# Convierte lista de tokens a cadena legible (para impresión/depuración)
def tokens_to_string(tokens: List[Token]) -> str:
    pieces = []
    for t in tokens:
        if t.type == CONCAT:
            pieces.append('·')
        elif t.type == ENDMARK:
            pieces.append('#')
        else:
            pieces.append(t.value)
    return ''.join(pieces)


# Convierte expresión postfija a cadena espacio-separada (legibilidad)
def postfix_to_string(postfix: List[Token]) -> str:
    return ' '.join(t.value if t.type != CONCAT else '·' for t in postfix)


# Imprime la tabla followpos (para depuración)
def print_followpos(followpos, pos_to_symbol):
    print('\nTabla followpos:')
    print('Posición | Símbolo | followpos')
    print('--------------------------------')
    for pos in sorted(pos_to_symbol.keys()):
        if pos_to_symbol[pos] == '#':
            continue
        print(f"{pos:^8} | {pos_to_symbol[pos]:^7} | {sorted(followpos.get(pos, set()))}")


# Imprime mapeo posición→símbolo (para depuración)
def print_positions(pos_to_symbol):
    print('\nPosiciones de hojas:')
    print('Posición | Símbolo')
    print('------------------')
    for pos in sorted(pos_to_symbol.keys()):
        print(f"{pos:^8} | {pos_to_symbol[pos]:^7}")


# Imprime propiedades del árbol de sintaxis (nullable, firstpos, lastpos)
def print_syntax_info(root):
    print('\nFunciones de la raíz:')
    print(f'nullable : {root.nullable}')
    print(f'firstpos : {sorted(root.firstpos)}')
    print(f'lastpos  : {sorted(root.lastpos)}')


# Genera clave de ordenamiento para estados (ordena alfabético+numérico)
def _state_sort_key(name: str):
    letters = ''.join(ch for ch in name if ch.isalpha())
    digits = ''.join(ch for ch in name if ch.isdigit())
    return (letters, int(digits) if digits else 0, name)


# Imprime tabla de transiciones del AFD en formato tabular
def print_dfa_table(dfa, title='Tabla de transición del AFD'):
    alphabet = dfa['alphabet']
    transitions = dfa['transitions']
    accepting = dfa['accepting_states']

    print(f'\n{title}:')
    header = ['Estado'] + alphabet
    print(' | '.join(f'{h:^12}' for h in header))
    print('-' * (15 * len(header)))

    ordered_states = sorted(transitions.keys(), key=_state_sort_key)
    for state in ordered_states:
        label = state
        if state == dfa['start_state']:
            label += '(I)'
        if state in accepting:
            label += '(F)'

        row = [f'{label:^12}']
        for sym in alphabet:
            row.append(f"{transitions[state].get(sym, '-'):^12}")
        print(' | '.join(row))


# Imprime qué conjunto de posiciones representa cada estado del AFD directo
def print_direct_state_sets(dfa):
    print('\nConjuntos que representa cada estado del AFD directo:')
    inv = {v: k for k, v in dfa['state_ids'].items()}
    for state_name in sorted(inv.keys(), key=lambda s: int(s[1:])):
        print(f'{state_name} = {sorted(inv[state_name])}')


# Imprime particiones/clases de equivalencia del AFD minimizado
def print_minimized_partitions(min_dfa):
    print('\nParticiones / equivalencias del AFD minimizado:')
    for index, part in enumerate(min_dfa['partitions']):
        print(f'M{index} = {part}')


# Compara estadísticas del AFD original vs minimizado
def print_comparison(dfa_directo, dfa_minimizado):
    estados_directo = len(dfa_directo['transitions'])
    trans_directo = count_transitions(dfa_directo)

    estados_min = len(dfa_minimizado['transitions'])
    trans_min = count_transitions(dfa_minimizado)

    print('\nComparación de autómatas:')
    print('--------------------------------------------------')
    print(f'AFD directo     -> estados: {estados_directo}, transiciones: {trans_directo}')
    print(f'AFD minimizado  -> estados: {estados_min}, transiciones: {trans_min}')
    print('--------------------------------------------------')

    if estados_directo == estados_min and trans_directo == trans_min:
        print('Resultado: el AFD obtenido por método directo ya era mínimo.')
    else:
        print('Resultado: la minimización redujo el autómata.')



# ============================================================
# ORQUESTACI\u00d3N COMPLETA: Expresi\u00f3n Regular → AFD Minimizado
# ============================================================
# Convierte expresi\u00f3n regular a AFD minimalizado
# Orquesta todo el pipeline: tokenizar → postfijo → árbol → cálculo funciones → AFD → minimizar
def regex_to_dfa(regex: str):
    tokens = tokenize(regex)
    tokens_with_concat = insert_concat(tokens)

    # Aumenta la expresión con paréntesis externos y marcador de fin
    augmented_tokens = [Token(LPAREN, '(')] + tokens_with_concat + [Token(RPAREN, ')'), Token(CONCAT, '·'), Token(ENDMARK, '#')]
    postfix = to_postfix(augmented_tokens)
    root, pos_to_symbol = build_syntax_tree(postfix)

    # Calcula propiedades del árbol
    followpos = {pos: set() for pos in pos_to_symbol}
    compute_functions(root, followpos)
    
    # Construye y minimiza el AFD
    dfa = build_dfa(root, followpos, pos_to_symbol)
    minimized_dfa = minimize_dfa(dfa)

    return {
        'input_regex': regex,
        'regex_with_concat': tokens_to_string(tokens_with_concat),
        'augmented_regex': tokens_to_string(augmented_tokens),
        'postfix': postfix,
        'root': root,
        'pos_to_symbol': pos_to_symbol,
        'followpos': followpos,
        'dfa': dfa,
        'minimized_dfa': minimized_dfa,
    }

