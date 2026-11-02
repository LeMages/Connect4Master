import json
import numpy as np
import math
import time

PLAYER, AI = 1, -1
EMPTY = 0
WIN_SCORE = 100000000000000

def get_valid_locations(board):
    ROWS, COLS = board.shape
    valid_locations = []
    for col in range(COLS):
        if is_valid_move(board, col):
            valid_locations.append(col)
    return valid_locations

def is_valid_move(board, col):
    ROWS, _ = board.shape
    # La rangée du haut est ROWS-1 car la rangée 0 est en bas
    return board[ROWS - 1][col] == 0

def get_next_open_row(board, col):
    ROWS, _ = board.shape
    for r in range(ROWS):
        if board[r][col] == 0:
            return r
    return None

def winning_move(board, piece):
    ROWS, COLS = board.shape
    # Vérifier les victoires horizontales
    for c in range(COLS - 3):
        for r in range(ROWS):
            if all(board[r][c + i] == piece for i in range(4)):
                return True

    # Vérifier les victoires verticales
    for c in range(COLS):
        for r in range(ROWS - 3):
            if all(board[r + i][c] == piece for i in range(4)):
                return True

    # Vérifier les diagonales ascendantes
    for c in range(COLS - 3):
        for r in range(ROWS - 3):
            if all(board[r + i][c + i] == piece for i in range(4)):
                return True

    # Vérifier les diagonales descendantes
    for c in range(COLS - 3):
        for r in range(3, ROWS):
            if all(board[r - i][c + i] == piece for i in range(4)):
                return True
    return False

def check_winning_move(board, piece):
    """
    Vérifie si un coup gagnant est possible pour le joueur donné.
    Retourne la colonne à jouer si un coup gagnant existe, None sinon.
    """
    for col in get_valid_locations(board):
        row = get_next_open_row(board, col)
        if row is not None:
            temp_board = board.copy()
            temp_board[row][col] = piece
            if winning_move(temp_board, piece):
                return col
    return None


def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER if piece == AI else AI
    
    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2
    
    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4
    
    return score

def score_position(board, piece):
    score = 0
    ROWS, COLS = board.shape

    # Score center
    center_array = [int(i) for i in list(board[:, COLS // 2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    # Score Horizontal
    for r in range(ROWS):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLS - 3):
            window = row_array[c:c + 4]
            score += evaluate_window(window, piece)

    # Score Vertical
    for c in range(COLS):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROWS - 3):
            window = col_array[r:r + 4]
            score += evaluate_window(window, piece)

    # Score diagonal
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r + i][c + i] for i in range(4)]
            score += evaluate_window(window, piece)

    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r + 3 - i][c + i] for i in range(4)]
            score += evaluate_window(window, piece)

    return score

def is_terminal_node(board):
    return winning_move(board, PLAYER) or winning_move(board, AI) or len(get_valid_locations(board)) == 0

def minimax(board, depth, alpha, beta, maximizingPlayer, start_time, max_time, pv_move=None):
    if time.time() - start_time >= max_time - 0.1:
        raise TimeoutError("Temps limite atteint")

    valid_locations = get_valid_locations(board)

    # Ordonnancement des coups : on teste le coup de la variation principale de l'itération précédente en premier
    COLS = board.shape[1]
    ordered_locations = sorted(valid_locations, key=lambda col: abs(col - COLS // 2))
    if pv_move is not None and pv_move in ordered_locations:
        ordered_locations.remove(pv_move)
        ordered_locations.insert(0, pv_move)

    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI):
                return (None, WIN_SCORE)
            elif winning_move(board, PLAYER):
                return (None, -WIN_SCORE)
            else: # Game is over, no more valid moves
                return (None, 0)
        else: # Depth is zero
            return (None, score_position(board, AI))

    if maximizingPlayer:
        value = -math.inf
        column = ordered_locations[0]
        for col in ordered_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            b_copy[row][col] = AI
            new_score = minimax(b_copy, depth - 1, alpha, beta, False, start_time, max_time)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value
    else: # Minimizing player
        value = math.inf
        column = ordered_locations[0]
        for col in ordered_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            b_copy[row][col] = PLAYER
            new_score = minimax(b_copy, depth - 1, alpha, beta, True, start_time, max_time)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value


def score_columns(board, depth, start_time, max_time):
    """
    Retourne le score exact de chaque colonne jouable à la profondeur donnée.
    La racine n'est pas élaguée : le panneau de l'interface affiche toutes les colonnes.
    """
    COLS = board.shape[1]
    scores = {}
    for col in sorted(get_valid_locations(board), key=lambda c: abs(c - COLS // 2)):
        b_copy = board.copy()
        b_copy[get_next_open_row(board, col)][col] = AI
        scores[col] = minimax(b_copy, depth - 1, -math.inf, math.inf, False, start_time, max_time)[1]
    return scores


def IA_Decision(board, max_time, max_depth=None, on_progress=None):
    """
    Fonction principale qui prend une matrice en entrée et retourne le numéro de colonne à jouer.
    max_depth plafonne la recherche (niveaux de difficulté).
    on_progress reçoit une analyse JSON après chaque profondeur terminée.
    """
    if not isinstance(board, np.ndarray):
        board = np.array(board)

    start_time = time.time()

    def report(depth, scores, best, reason):
        if on_progress is not None:
            on_progress(json.dumps({
                "depth": depth,
                "scores": {str(col): score for col, score in scores.items()},
                "best": int(best),
                "reason": reason,
                "elapsed": time.time() - start_time,
            }))

    winning_move_col = check_winning_move(board, AI)
    if winning_move_col is not None:
        report(0, {}, winning_move_col, "win")
        return winning_move_col

    blocking_move_col = check_winning_move(board, PLAYER)
    if blocking_move_col is not None:
        report(0, {}, blocking_move_col, "block")
        return blocking_move_col

    best_col = None
    depth = 1

    valid_moves = get_valid_locations(board)
    if valid_moves:
        # Initialiser avec le meilleur coup statique (colonne centrale)
        COLS = board.shape[1]
        valid_moves = sorted(valid_moves, key=lambda col: abs(col - COLS // 2))
        best_col = valid_moves[0]

    empty_cells = int(np.count_nonzero(board == EMPTY))

    while valid_moves and depth <= empty_cells and (max_depth is None or depth <= max_depth):
        try:
            if time.time() - start_time >= max_time - 0.1:
                break
            scores = score_columns(board, depth, start_time, max_time)
            # À score égal, max garde le premier coup : le plus proche du centre
            best_col = max(valid_moves, key=lambda col: scores[col])
            report(depth, scores, best_col, "search")
            # Victoire ou défaite forcée : chercher plus loin ne changera rien
            if abs(scores[best_col]) >= WIN_SCORE:
                break
            depth += 1
        except TimeoutError:
            break
        except Exception as e:
            print(f"Error in IA_Decision: {e}")
            break

    return best_col