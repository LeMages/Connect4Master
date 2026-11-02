import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ia import AI, PLAYER, WIN_SCORE, IA_Decision


def empty_board():
    return np.zeros((6, 7), dtype=int)


def test_joue_le_coup_gagnant():
    board = empty_board()
    board[0][:3] = AI
    board[1][:2] = PLAYER
    assert IA_Decision(board, 1.0) == 3


def test_bloque_la_menace():
    board = empty_board()
    board[0][:3] = PLAYER
    assert IA_Decision(board, 1.0) == 3


def test_respecte_la_profondeur_maximale():
    reports = []
    IA_Decision(empty_board(), 5.0, max_depth=2, on_progress=lambda r: reports.append(json.loads(r)))
    assert [report["depth"] for report in reports] == [1, 2]
    assert all(len(report["scores"]) == 7 for report in reports)


def test_ne_propose_pas_une_colonne_pleine():
    board = empty_board()
    board[:, 3] = [AI, PLAYER, AI, PLAYER, AI, PLAYER]
    reports = []
    col = IA_Decision(board, 1.0, max_depth=2, on_progress=lambda r: reports.append(json.loads(r)))
    assert col != 3
    assert "3" not in reports[-1]["scores"]


def test_arrete_de_chercher_si_la_partie_est_decidee():
    # Double menace en bas : l'IA gagne à coup sûr sans utiliser tout son temps.
    board = empty_board()
    board[0][2:4] = AI
    board[1][2:4] = PLAYER
    reports = []
    IA_Decision(board, 10.0, on_progress=lambda r: reports.append(json.loads(r)))
    assert max(reports[-1]["scores"].values()) >= WIN_SCORE
    assert reports[-1]["elapsed"] < 9
