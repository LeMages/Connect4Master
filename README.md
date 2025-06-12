# Connect4Master : Puissance 4 avec IA Avancée

## Présentation du Jeu
Ce projet est une implémentation du jeu Puissance 4 avec une interface graphique moderne et une intelligence artificielle basée sur l'algorithme Minimax avec élagage alpha-beta. Le jeu propose une expérience de jeu fluide avec des animations et des effets visuels, tout en offrant un défi intéressant grâce à l'IA.

## Technologies Utilisées
- **Python 3.x** : Langage principal
- **Pygame** : Bibliothèque pour l'interface graphique
- **NumPy** : Pour la manipulation efficace des matrices du jeu
- **Math** : Pour les calculs mathématiques nécessaires à l'IA

## Installation

### Création de l'environnement virtuel
1. Ouvrez un terminal dans le dossier du projet
2. Créez un environnement virtuel :
```bash
python -m venv venv
```
3. Activez l'environnement virtuel :
   - Sur Windows :
   ```bash
   .\venv\Scripts\activate
   ```
   - Sur Linux/Mac :
   ```bash
   source venv/bin/activate
   ```
4. Installez les dépendances :
```bash
pip install -r requirements.txt
```

## Fonctionnalités de l'IA

### Fonctions Principales

#### `IA_Decision(board, max_time)`
- Fonction principale qui détermine le meilleur coup à jouer
- Utilise une approche itérative avec approfondissement progressif
- Prend en compte le temps maximum de réflexion
- Implémente des optimisations comme la variation principale (PV)

#### `minimax(board, depth, alpha, beta, maximizingPlayer, start_time, max_time, pv_move)`
- Implémente l'algorithme Minimax avec élagage alpha-beta
- Gère la profondeur de recherche et le temps limite
- Optimisé avec l'ordre des coups et la variation principale

#### `score_position(board, piece)`
- Évalue la position actuelle du plateau
- Attribue des scores basés sur :
  - Occupation du centre
  - Alignements horizontaux, verticaux et diagonaux
  - Menaces et opportunités de victoire

#### `evaluate_window(window, piece)`
- Évalue une fenêtre de 4 cases
- Attribue des scores selon :
  - 4 pièces alignées : +100
  - 3 pièces + 1 vide : +5
  - 2 pièces + 2 vides : +2
  - 3 pièces adverses + 1 vide : -4

### Fonctions Utilitaires

#### `get_valid_locations(board)`
- Retourne la liste des colonnes où un coup est possible

#### `is_valid_move(board, col)`
- Vérifie si un coup est valide dans une colonne donnée

#### `get_next_open_row(board, col)`
- Trouve la première rangée vide dans une colonne

#### `winning_move(board, piece)`
- Vérifie si un joueur a gagné
- Examine les alignements horizontaux, verticaux et diagonaux

#### `check_winning_move(board, piece)`
- Vérifie si un coup gagnant est possible
- Retourne la colonne à jouer si un coup gagnant existe

## Paramètres du Jeu
- Taille du plateau configurable (5-10 lignes, 5-10 colonnes)
- Temps de réflexion de l'IA ajustable (1-10 secondes)
- Interface graphique adaptative (plein écran)

## Comment Jouer
1. Lancez le jeu : `python main.py`
2. Utilisez le menu principal pour :
   - Démarrer une partie
   - Ajuster les paramètres
   - Quitter le jeu
3. En jeu :
   - Cliquez sur une colonne pour placer votre pion
   - L'IA jouera automatiquement
   - Utilisez Échap pour retourner au menu principal 