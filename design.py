import pygame
import math

def create_gradient_background(width, height, top_color, bottom_color):
    """Crée une surface avec un dégradé vertical."""
    gradient = pygame.Surface((width, height))
    for y in range(height):
        # Interpole la couleur pour chaque ligne
        r = top_color[0] * (1 - y / height) + bottom_color[0] * (y / height)
        g = top_color[1] * (1 - y / height) + bottom_color[1] * (y / height)
        b = top_color[2] * (1 - y / height) + bottom_color[2] * (y / height)
        pygame.draw.line(gradient, (r, g, b), (0, y), (width, y))
    return gradient

def create_token_surface(size, color):
    """Crée une surface pour un jeton avec un effet 3D amélioré."""
    token_surface = pygame.Surface((size, size), pygame.SRCALPHA)
    radius = size // 2
    center = (radius, radius)

    # 1. Ombre portée (sous le jeton)
    pygame.draw.circle(token_surface, (0, 0, 0, 50), (radius + 3, radius + 3), radius)

    # 2. Corps du jeton - une base plus sombre
    shadow_color = tuple(max(0, c - 40) for c in color)
    pygame.draw.circle(token_surface, shadow_color, center, radius)

    # 3. Reflet principal - un cercle plus clair et décalé vers le haut
    # Cela laisse un croissant d'ombre en bas, donnant une impression de volume
    highlight_offset = int(radius * 0.1)
    highlight_radius = radius - highlight_offset
    highlight_center = (center[0], center[1] - highlight_offset)
    pygame.draw.circle(token_surface, color, highlight_center, highlight_radius)

    # 4. Reflet spéculaire - petite touche de brillance
    specular_radius = int(radius * 0.5)
    specular_center = (center[0] + int(radius * 0.3), center[1] - int(radius * 0.4))
    specular_color = (255, 255, 255, 90)

    # Crée un dégradé radial pour le reflet spéculaire pour qu'il soit doux
    specular_surf = pygame.Surface((specular_radius * 2, specular_radius * 2), pygame.SRCALPHA)
    for i in range(specular_radius, 0, -1):
        alpha = specular_color[3] * (1 - i / specular_radius)
        pygame.draw.circle(specular_surf, (255, 255, 255, int(alpha)), (specular_radius, specular_radius), i)
    
    token_surface.blit(specular_surf, (specular_center[0] - specular_radius, specular_center[1] - specular_radius), special_flags=pygame.BLEND_RGBA_ADD)

    return token_surface

def create_grid_surface(cols, rows, square_size, color):
    """Crée la surcouche de la grille pour un effet de profondeur."""
    width = cols * square_size
    height = rows * square_size
    
    grid_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Dessine la grille solide
    grid_surface.fill(color)
    
    # Perce les trous pour les jetons
    for r in range(rows):
        for c in range(cols):
            center_x = int(c * square_size + square_size / 2)
            center_y = int(r * square_size + square_size / 2)
            pygame.draw.circle(grid_surface, (0, 0, 0, 0), (center_x, center_y), int(square_size / 2 - 5))

    # Ajoute un effet de biseau et d'ombre interne aux trous
    for r in range(rows):
        for c in range(cols):
            center_x = int(c * square_size + square_size / 2)
            center_y = int(r * square_size + square_size / 2)
            radius = int(square_size / 2 - 5)
            
            # Ombre interne (en haut à gauche du trou)
            for i in range(3):
                pygame.draw.arc(grid_surface, (0, 0, 0, 50), 
                                (center_x - radius, center_y - radius, radius * 2, radius * 2), 
                                0.8, 2.4, 3-i)
            # Reflet interne (en bas à droite du trou)
            for i in range(3):
                 pygame.draw.arc(grid_surface, (255, 255, 255, 50), 
                                (center_x - radius, center_y - radius, radius * 2, radius * 2), 
                                -0.8, -2.4, 3-i)

    return grid_surface

def find_winning_pieces(board):
    """Trouve les 4 pièces alignées et retourne leurs coordonnées."""
    ROWS, COLS = board.shape
    
    # Horizontal
    for r in range(ROWS):
        for c in range(COLS - 3):
            if board[r][c] != 0 and all(board[r][c] == board[r][c+i] for i in range(4)):
                return [(r, c+i) for i in range(4)]
    # Vertical
    for r in range(ROWS - 3):
        for c in range(COLS):
            if board[r][c] != 0 and all(board[r][c] == board[r+i][c] for i in range(4)):
                return [(r+i, c) for i in range(4)]
    # Diagonale ascendante
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if board[r][c] != 0 and all(board[r][c] == board[r+i][c+i] for i in range(4)):
                return [(r+i, c+i) for i in range(4)]
    # Diagonale descendante
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            if board[r][c] != 0 and all(board[r][c] == board[r-i][c+i] for i in range(4)):
                return [(r-i, c+i) for i in range(4)]
                
    return None 