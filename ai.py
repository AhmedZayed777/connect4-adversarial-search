# ai.py
import random
import math
import numpy as np
from game import Connect4Game, ROWS, COLS

class MinimaxAlphaBeta:
    """الفئة الأساسية لخوارزمية Minimax مع Alpha-Beta Pruning"""
    
    def __init__(self, player, depth, c_param=1.41):
        self.player = player
        self.opponent = 1 if player == 2 else 2
        self.max_depth = depth
        self.c_param = c_param
        self.nodes_evaluated = 0
        
    def get_best_move(self, game):
        """العثور على أفضل حركة"""
        self.nodes_evaluated = 0
        
        if game.turn != self.player:
            return None
        
        moves = self._order_moves(game)
        
        best_score = -float('inf')
        best_moves = []
        
        alpha = -float('inf')
        beta = float('inf')
        
        for col in moves:
            if game.is_valid_location(col):
                new_game = self._simulate_move(game, col)
                
                score = self._minimax_ab(new_game, self.max_depth - 1, 
                                        alpha, beta, False)
                
                if score > best_score:
                    best_score = score
                    best_moves = [col]
                elif score == best_score:
                    best_moves.append(col)
                
                alpha = max(alpha, score)
        
        return random.choice(best_moves) if best_moves else None
    
    def _minimax_ab(self, game, depth, alpha, beta, maximizing_player):
        """Minimax مع Alpha-Beta"""
        self.nodes_evaluated += 1
        
        if depth == 0 or game.game_over:
            return self._evaluate_board(game)
        
        if maximizing_player:
            max_eval = -float('inf')
            moves = self._order_moves(game)
            
            for col in moves:
                if game.is_valid_location(col):
                    new_game = self._simulate_move(game, col)
                    
                    eval_score = self._minimax_ab(new_game, depth - 1, 
                                                 alpha, beta, False)
                    
                    max_eval = max(max_eval, eval_score)
                    alpha = max(alpha, eval_score)
                    
                    if alpha >= beta:
                        break
            
            return max_eval
            
        else:
            min_eval = float('inf')
            moves = self._order_moves(game)
            
            for col in moves:
                if game.is_valid_location(col):
                    new_game = self._simulate_move(game, col)
                    
                    eval_score = self._minimax_ab(new_game, depth - 1, 
                                                 alpha, beta, True)
                    
                    min_eval = min(min_eval, eval_score)
                    beta = min(beta, eval_score)
                    
                    if beta <= alpha:
                        break
            
            return min_eval
    
    def _simulate_move(self, game, col):
        """محاكاة حركة"""
        new_game = Connect4Game()
        new_game.board = game.board.copy()
        new_game.turn = game.turn
        
        if new_game.drop_piece(col):
            new_game.switch_turn()
        
        return new_game
    
    def _order_moves(self, game):
        """ترتيب الحركات - متوازن وغير مركز على المركز"""
        valid_moves = [c for c in range(COLS) if game.is_valid_location(c)]
        
        if not valid_moves:
            return []
        
        center = COLS // 2
        
        # تصنيف الحركات
        center_moves = []
        strategic_moves = []
        other_moves = []
        
        for col in valid_moves:
            # تحقق أولاً من الحركات الاستراتيجية
            if self._is_strategic_move(game, col):
                strategic_moves.append(col)
            elif col == center:
                center_moves.append(col)
            else:
                other_moves.append(col)
        
        # **التعديل: لا نضع المركز أولاً دائماً**
        ordered = []
        
        # 1. الحركات الاستراتيجية أولاً
        ordered.extend(strategic_moves)
        
        # 2. الحركات الأخرى (مرتبة حسب المسافة من المركز)
        # نخلطها لعدم التركيز على نمط واحد
        random.shuffle(other_moves)
        ordered.extend(other_moves)
        
        # 3. المركز أخيراً (لتجنب التركيز عليه)
        ordered.extend(center_moves)
        
        return ordered
    
    def _is_strategic_move(self, game, col):
        """تحقق إذا كانت الحركة استراتيجية"""
        if not game.is_valid_location(col):
            return False
        
        # محاكاة سريعة
        temp_game = self._simulate_move(game, col)
        
        # تحقق من التهديدات
        if self._has_immediate_threat(temp_game):
            return True
        
        # تحقق من منع تهديدات الخصم
        opponent_temp = Connect4Game()
        opponent_temp.board = game.board.copy()
        opponent_temp.turn = self.opponent
        
        if opponent_temp.drop_piece(col):
            if opponent_temp.game_over:
                return True
        
        return False
    
    def _has_immediate_threat(self, game):
        """تحقق من وجود تهديد فوري"""
        # تحقق من جميع الاتجاهات للاعب الحالي
        player = game.turn
        board = game.board
        
        # أفقي
        for r in range(ROWS):
            for c in range(COLS - 3):
                if (board[r][c] == player and board[r][c+1] == player and 
                    board[r][c+2] == player and board[r][c+3] == 0):
                    return True
        
        # رأسي
        for c in range(COLS):
            for r in range(ROWS - 3):
                if (board[r][c] == player and board[r+1][c] == player and 
                    board[r+2][c] == player and board[r+3][c] == 0):
                    return True
        
        # قطري صاعد
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                if (board[r][c] == player and board[r+1][c+1] == player and 
                    board[r+2][c+2] == player and board[r+3][c+3] == 0):
                    return True
        
        # قطري منحدر
        for r in range(3, ROWS):
            for c in range(COLS - 3):
                if (board[r][c] == player and board[r-1][c+1] == player and 
                    board[r-2][c+2] == player and board[r-3][c+3] == 0):
                    return True
        
        return False
    
    def _evaluate_board(self, game):
        """تقييم متوازن للوحة"""
        if game.game_over:
            if game.winner == self.player:
                return 1000000
            elif game.winner == self.opponent:
                return -1000000
            return 0
        
        score = 0
        
        # تقييم جميع الاتجاهات الأفقية
        for r in range(ROWS):
            for c in range(COLS - 3):
                window = game.board[r, c:c+4]
                score += self._evaluate_window(window, self.player) * 12
                score -= self._evaluate_window(window, self.opponent) * 12
        
        # تقييم الاتجاهات الرأسية
        for c in range(COLS):
            for r in range(ROWS - 3):
                window = [game.board[r][c], game.board[r+1][c], 
                         game.board[r+2][c], game.board[r+3][c]]
                score += self._evaluate_window(window, self.player) * 8
                score -= self._evaluate_window(window, self.opponent) * 8
        
        # تقييم القطر الصاعد
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                window = [game.board[r][c], game.board[r+1][c+1],
                         game.board[r+2][c+2], game.board[r+3][c+3]]
                score += self._evaluate_window(window, self.player) * 15
                score -= self._evaluate_window(window, self.opponent) * 15
        
        # تقييم القطر المنحدر
        for r in range(3, ROWS):
            for c in range(COLS - 3):
                window = [game.board[r][c], game.board[r-1][c+1],
                         game.board[r-2][c+2], game.board[r-3][c+3]]
                score += self._evaluate_window(window, self.player) * 15
                score -= self._evaluate_window(window, self.opponent) * 15
        
        # **تخفيض كبير لوزن المركز**
        center = COLS // 2
        center_weight = 1  # وزن خفيف جداً
        
        for r in range(ROWS):
            if game.board[r][center] == self.player:
                score += (ROWS - r) * center_weight
        
        # **زيادة وزن الأعمدة المجاورة للمركز**
        for offset in [-1, 1, -2, 2]:
            col = center + offset
            if 0 <= col < COLS:
                for r in range(ROWS):
                    if game.board[r][col] == self.player:
                        score += (ROWS - r) * 2  # وزن مضاعف
        
        # **مكافأة التنوع في الأعمدة**
        columns_used = set()
        for r in range(ROWS):
            for c in range(COLS):
                if game.board[r][c] == self.player:
                    columns_used.add(c)
        
        diversity_bonus = len(columns_used) * 8
        score += diversity_bonus
        
        # **عقوبة التركيز في عمود واحد**
        if len(columns_used) > 0:
            pieces_per_column = [0] * COLS
            for r in range(ROWS):
                for c in range(COLS):
                    if game.board[r][c] == self.player:
                        pieces_per_column[c] += 1
            
            max_concentration = max(pieces_per_column)
            total_pieces = sum(pieces_per_column)
            
            if total_pieces > 0:
                concentration_ratio = max_concentration / total_pieces
                if concentration_ratio > 0.7:
                    score -= 100  # عقوبة كبيرة
        
        return score
    
    def _evaluate_window(self, window, player):
        """تقييم نافذة 4 خلايا"""
        opponent = 1 if player == 2 else 2
        
        player_count = 0
        opponent_count = 0
        empty_count = 0
        
        for cell in window:
            if cell == player:
                player_count += 1
            elif cell == opponent:
                opponent_count += 1
            else:
                empty_count += 1
        
        if player_count == 4:
            return 1000
        elif player_count == 3 and empty_count == 1:
            return 80
        elif player_count == 2 and empty_count == 2:
            return 15
        elif opponent_count == 3 and empty_count == 1:
            return -70
        elif opponent_count == 2 and empty_count == 2:
            return -10
        else:
            return 0
    
    def _evaluate_threats(self, game, player):
        """تقييم التهديدات"""
        threat_score = 0
        
        # أفقي
        for r in range(ROWS):
            for c in range(COLS - 3):
                window = game.board[r, c:c+4]
                threat_score += self._evaluate_window(window, player)
        
        # رأسي
        for c in range(COLS):
            for r in range(ROWS - 3):
                window = [game.board[r][c], game.board[r+1][c],
                         game.board[r+2][c], game.board[r+3][c]]
                threat_score += self._evaluate_window(window, player)
        
        # قطري
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                window = [game.board[r][c], game.board[r+1][c+1],
                         game.board[r+2][c+2], game.board[r+3][c+3]]
                threat_score += self._evaluate_window(window, player)
        
        return threat_score