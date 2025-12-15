# levels.py
from ai import MinimaxAlphaBeta
from game import COLS, ROWS, Connect4Game
import random
import numpy as np

class HardAI(MinimaxAlphaBeta):
    """AI صعب - متوازن ومتنوع الاستراتيجية"""
    
    def __init__(self, player):
        super().__init__(player, depth=5, c_param=1.0)
        self.randomness_factor = 0.03  # 3% فقط عشوائية
        self.last_move = None
        self.consecutive_same_column = 0
        self.center_column = COLS // 2
        self.center_obsession_counter = 0
        self.defensive_mode = False
        
    def get_best_move(self, game):
        """استراتيجية ذكية مع مرونة كبيرة"""
        valid_moves = [c for c in range(COLS) if game.is_valid_location(c)]
        if not valid_moves:
            return None
        
        # 1. تحقق من الفوز الفوري
        for col in valid_moves:
            test_game = self._simulate_move(game, col)
            if test_game.game_over and test_game.winner == self.player:
                print(f"[Hard AI] فوز فوري: العمود {col}")
                self.last_move = col
                return col
        
        # 2. تحقق من فوز الخصم الفوري (منعه)
        for col in valid_moves:
            temp_game = Connect4Game()
            temp_game.board = game.board.copy()
            temp_game.turn = self.opponent
            if temp_game.drop_piece(col):
                if temp_game.game_over:
                    print(f"[Hard AI] منع فوز الخصم: العمود {col}")
                    self.last_move = col
                    return col
        
        # 3. البحث عن أفضل حركة استباقية
        strategic_moves = self._find_strategic_moves(game)
        if strategic_moves:
            print(f"[Hard AI] حركات استراتيجية متاحة: {strategic_moves}")
        
        # 4. تجنب تكرار نفس العمود
        if self.last_move is not None and self.last_move in valid_moves:
            if self.consecutive_same_column >= 2:
                valid_moves.remove(self.last_move)
                print(f"[Hard AI] تجنب التكرار في العمود {self.last_move}")
                self.consecutive_same_column = 0
        
        # 5. استخدام Minimax الأساسي
        minimax_move = super().get_best_move(game)
        
        # 6. التحقق من إدمان المركز وتصحيحه
        if minimax_move == self.center_column:
            self.center_obsession_counter += 1
            print(f"[Hard AI] استخدام المركز #{self.center_obsession_counter}")
            
            # إذا استخدم المركز كثيراً، غير الاستراتيجية
            if self.center_obsession_counter >= 2 and len(valid_moves) > 1:
                # اختر أفضل حركة بديلة
                alternative_moves = [c for c in valid_moves 
                                   if c != self.center_column]
                
                if alternative_moves:
                    # تقييم البدائل
                    best_alt_score = -float('inf')
                    best_alt_move = alternative_moves[0]
                    
                    for col in alternative_moves:
                        alt_game = self._simulate_move(game, col)
                        score = self._evaluate_position(alt_game, col)
                        if score > best_alt_score:
                            best_alt_score = score
                            best_alt_move = col
                    
                    # إذا كانت البديلة جيدة بما يكفي، استخدمها
                    if best_alt_score > 50:
                        print(f"[Hard AI] تغيير استراتيجي: من {self.center_column} إلى {best_alt_move}")
                        self.last_move = best_alt_move
                        self.center_obsession_counter = 0
                        return best_alt_move
        else:
            self.center_obsession_counter = 0
        
        # 7. تحديث حالة الحركة الأخيرة
        if self.last_move == minimax_move:
            self.consecutive_same_column += 1
        else:
            self.consecutive_same_column = 0
        
        self.last_move = minimax_move
        return minimax_move
    
    def _find_strategic_moves(self, game):
        """العثور على حركات استراتيجية مهمة"""
        strategic_moves = []
        
        for col in range(COLS):
            if not game.is_valid_location(col):
                continue
            
            # محاكاة الحركة
            test_game = self._simulate_move(game, col)
            
            # حساب القيمة الاستراتيجية
            strategic_value = self._calculate_strategic_value(test_game, col)
            
            if strategic_value > 60:  # قيمة استراتيجية عالية
                strategic_moves.append((strategic_value, col))
        
        # ترتيب تنازلي حسب القيمة
        strategic_moves.sort(reverse=True)
        return [col for value, col in strategic_moves[:3]]  # أفضل 3 حركات
    
    def _calculate_strategic_value(self, game, col):
        """حساب القيمة الاستراتيجية لحركة"""
        if not game.is_valid_location(col):
            return 0
        
        row = game.get_next_open_row(col)
        if row is None:
            return 0
        
        score = 0
        
        # 1. قيمة بناء التهديدات
        threat_score = self._evaluate_threat_potential(game, col, row)
        score += threat_score
        
        # 2. قيمة الدفاع
        defensive_score = self._evaluate_defensive_value(game, col)
        score += defensive_score
        
        # 3. قيمة الموقع
        positional_score = self._evaluate_positional_value(col, row)
        score += positional_score
        
        # 4. عقوبة المركز المفرط
        if col == self.center_column and self.center_obsession_counter >= 2:
            score -= 30  # عقوبة لاستخدام المركز كثيراً
        
        return score
    
    def _evaluate_threat_potential(self, game, col, row):
        """تقييم قدرة الحركة على خلق تهديدات"""
        score = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for dr, dc in directions:
            # تحقق في كلا الاتجاهين
            count = 1
            
            # اتجاه إيجابي
            for i in range(1, 4):
                nr, nc = row + dr * i, col + dc * i
                if 0 <= nr < ROWS and 0 <= nc < COLS:
                    if game.board[nr][nc] == self.player:
                        count += 1
                    elif game.board[nr][nc] != 0:
                        break
                else:
                    break
            
            # اتجاه سلبي
            for i in range(1, 4):
                nr, nc = row - dr * i, col - dc * i
                if 0 <= nr < ROWS and 0 <= nc < COLS:
                    if game.board[nr][nc] == self.player:
                        count += 1
                    elif game.board[nr][nc] != 0:
                        break
                else:
                    break
            
            # تقييم التهديد
            if count >= 3:
                score += 100  # تهديد بثلاث قطع
            elif count == 2:
                score += 30   # بداية تهديد جيد
            elif count == 1:
                score += 5    # موضع جيد
        
        return score
    
    def _evaluate_defensive_value(self, game, col):
        """تقييم قيمة الحركة دفاعياً"""
        if not game.is_valid_location(col):
            return 0
        
        # محاكاة ما يمكن أن يفعله الخصم بعد حركتنا
        our_move_game = self._simulate_move(game, col)
        
        # تحقق من تهديدات الخصم في الجولة التالية
        opponent_threats = 0
        for opp_col in range(COLS):
            if our_move_game.is_valid_location(opp_col):
                opp_game = self._simulate_move(our_move_game, opp_col)
                if opp_game.game_over and opp_game.winner == self.opponent:
                    opponent_threats += 100  # تهديد فوز خطير
        
        # القيمة الدفاعية هي عكس تهديدات الخصم
        return -opponent_threats
    
    def _evaluate_positional_value(self, col, row):
        """تقييم قيمة الموقع"""
        score = 0
        
        # تفضيل المواقع المركزية لكن ليس بشكل مفرط
        center = COLS // 2
        distance_from_center = abs(col - center)
        
        # قيمة الموقع تنخفض كلما ابتعدنا عن المركز
        positional_value = max(0, 20 - distance_from_center * 5)
        score += positional_value
        
        # تفضيل الصفوف السفلية (أكثر استقراراً)
        row_value = (ROWS - row) * 3
        score += row_value
        
        return score
    
    def _evaluate_position(self, game, col):
        """تقييم سريع للموقع بعد الحركة"""
        score = 0
        
        # 1. نقاط للتهديدات
        score += self._evaluate_threats(game, self.player) * 10
        
        # 2. نقاط للدفاع
        score -= self._evaluate_threats(game, self.opponent) * 8
        
        # 3. نقاط لتوزيع القطع
        pieces_per_column = [0] * COLS
        for r in range(ROWS):
            for c in range(COLS):
                if game.board[r][c] == self.player:
                    pieces_per_column[c] += 1
        
        # مكافأة التنوع
        columns_used = sum(1 for count in pieces_per_column if count > 0)
        score += columns_used * 15
        
        # عقوبة التركيز المفرط
        if columns_used > 0:
            max_in_column = max(pieces_per_column)
            concentration = max_in_column / sum(pieces_per_column)
            if concentration > 0.6:
                score -= 80
        
        return score
    
    def _evaluate_board(self, game):
        """تقييم متوازن للوحة - حل مشكلة إدمان المركز"""
        if game.game_over:
            if game.winner == self.player:
                return 1000000
            elif game.winner == self.opponent:
                return -1000000
            return 0
        
        score = 0
        
        # استخدام التقييم الأساسي
        try:
            base_score = super()._evaluate_board(game)
            score += base_score
        except:
            score = self._basic_evaluation(game)
        
        # **تخفيض كبير لوزن المركز**
        center = COLS // 2
        center_pieces = 0
        
        for r in range(ROWS):
            if game.board[r][center] == self.player:
                center_pieces += 1
        
        # وزن خفيف جداً للمركز (مش أكثر من 20 نقطة)
        score += center_pieces * 5
        
        # **مكافأة كبيرة للأعمدة الأخرى**
        non_center_score = 0
        for c in range(COLS):
            if c == center:
                continue
            
            column_score = 0
            for r in range(ROWS):
                if game.board[r][c] == self.player:
                    # وزن أكبر للأعمدة غير المركزية
                    column_score += (ROWS - r) * 4
            
            non_center_score += column_score
        
        score += non_center_score
        
        # **عقوبة التركيز في عمود واحد**
        column_distribution = [0] * COLS
        for r in range(ROWS):
            for c in range(COLS):
                if game.board[r][c] == self.player:
                    column_distribution[c] += 1
        
        total_pieces = sum(column_distribution)
        if total_pieces > 3:  # فقط إذا كان لدينا عدة قطع
            max_in_column = max(column_distribution)
            concentration = max_in_column / total_pieces
            
            # عقوبة تصاعدية
            if concentration > 0.7:
                score -= 150
            elif concentration > 0.6:
                score -= 80
            elif concentration > 0.5:
                score -= 40
        
        # **مكافأة بناء تهديدات متنوعة**
        threat_diversity = self._calculate_threat_diversity(game)
        score += threat_diversity * 25
        
        return score
    
    def _calculate_threat_diversity(self, game):
        """حساب تنوع التهديدات عبر اللوحة"""
        threat_columns = set()
        
        for col in range(COLS):
            if not game.is_valid_location(col):
                continue
            
            row = game.get_next_open_row(col)
            if row is None:
                continue
            
            # تحقق في الاتجاهات الأربعة
            directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
            
            for dr, dc in directions:
                count = 1
                
                # اتجاه إيجابي
                r, c = row, col
                for i in range(1, 4):
                    nr, nc = r + dr * i, c + dc * i
                    if 0 <= nr < ROWS and 0 <= nc < COLS and game.board[nr][nc] == self.player:
                        count += 1
                    else:
                        break
                
                # اتجاه سلبي
                r, c = row, col
                for i in range(1, 4):
                    nr, nc = r - dr * i, c - dc * i
                    if 0 <= nr < ROWS and 0 <= nc < COLS and game.board[nr][nc] == self.player:
                        count += 1
                    else:
                        break
                
                if count >= 2:  # إذا كان هناك تهديد محتمل
                    threat_columns.add(col)
                    break
        
        return len(threat_columns)
    
    def _basic_evaluation(self, game):
        """تقييم أساسي"""
        score = 0
        
        # تقييم التهديدات
        for r in range(ROWS):
            for c in range(COLS - 3):
                window = game.board[r, c:c+4]
                score += self._evaluate_window(window, self.player) * 8
                score -= self._evaluate_window(window, self.opponent) * 8
        
        # تقييم القطر
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                window = [game.board[r][c], game.board[r+1][c+1],
                         game.board[r+2][c+2], game.board[r+3][c+3]]
                score += self._evaluate_window(window, self.player) * 10
                score -= self._evaluate_window(window, self.opponent) * 10
        
        # وزن خفيف للمركز
        center = COLS // 2
        for r in range(ROWS):
            if game.board[r][center] == self.player:
                score += 3
        
        return score

class EasyAI(MinimaxAlphaBeta):
    """AI سهل"""
    
    def __init__(self, player):
        super().__init__(player, depth=2, c_param=1.0)
        self.randomness_factor = 0.4
    
    def get_best_move(self, game):
        valid_moves = [c for c in range(COLS) if game.is_valid_location(c)]
        if not valid_moves:
            return None
        
        # 50% عشوائية
        if random.random() < self.randomness_factor:
            return random.choice(valid_moves)
        
        return super().get_best_move(game)

class MediumAI(MinimaxAlphaBeta):
    """AI متوسط"""
    
    def __init__(self, player):
        super().__init__(player, depth=4, c_param=1.0)
        self.randomness_factor = 0.1
    
    def get_best_move(self, game):
        valid_moves = [c for c in range(COLS) if game.is_valid_location(c)]
        if not valid_moves:
            return None
        
        # 10% عشوائية فقط
        if random.random() < self.randomness_factor:
            return random.choice(valid_moves)
        
        return super().get_best_move(game)

class AIController:
    """وحدة التحكم في AI"""
    
    @staticmethod
    def create_ai(difficulty, player):
        difficulty = difficulty.lower()
        
        if difficulty == "easy":
            return EasyAI(player)
        elif difficulty == "medium":
            return MediumAI(player)
        elif difficulty == "hard":
            return HardAI(player)
        else:
            return MediumAI(player)