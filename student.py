from agent import Agent
import numpy as np

class Search(Agent):
    def __init__(self, player):
        super().__init__(player)
        self.max_depth=10
        self.candidate_limit=25
        self.directions=[(1,0),(0,1),(1,1),(1,-1)]
        self.skill_used=False

        # TODO: 在这里添加任何你需要的初始化代码
        
    def get_candidates(self,board):
        n=len(board)
        candidates=set()
        
        has_stone=False

        for i in range(n):
            for j in range(n):
                if board[i][j]==1 or board[i][j]==2:
                    has_stone=True
                    for dx in range(-2,3):
                        for dy in range(-2,3):
                            x=i+dx
                            y=j+dy
                            if 0<=x<n and 0<=y<n and board[x][y]==0:
                                candidates.add((x,y))
        if not has_stone:
            center=n//2
            return [(center,center)]
        return list(candidates)
    
    def ordered_candidates(self,board,player):
        candidates=self.get_candidates(board)
        opponent=3-player

        candidates.sort(key=lambda move:(self.evaluate_move(board,move,player)+self.evaluate_move(board,move,opponent)*0.8),reverse=True)
        return candidates[:self.candidate_limit]
    def is_winning_move(self,board,move,player):
        row,col=move
        if board[row][col]!=0:
            return False
        board[row][col]=player
        win=self.check_win_at(board,row,col,player)
        board[row][col]=0
        return win

        
    def check_win_at(self,board,row,col,player):
        n=len(board)
        for dx,dy in self.directions:
            count=1

            x,y=row+dx,col+dy
            while 0<=x<n and 0<=y<n and board[x][y]==player:
                count+=1
                x+=dx
                y+=dy

            x,y=row-dx,col-dy
            while 0<=x<n and 0<=y<n and board[x][y]==player:
                count+=1
                x-=dx
                y-=dy
            if count>=5:
                return True
        return False 
    
    def pattern_score(self,count,open_ends):
        if count>=5:
            return 1000000
        if count==4:
            if open_ends==2:
                return 100000
            elif open_ends==1:
                return 10000
        if count==3:
            if open_ends==2:
                return 5000
            elif open_ends==1:
                return 500
        if count==2:
            if open_ends==2:
                return 200
            elif open_ends==1:
                return 50
        if count==1:
            if open_ends==2:
                return 10
        return 0
            
    
    def evaluate_board(self,board):
        candidates=self.get_candidates(board)

        my_score=0
        opponent_score=0

        for move in candidates:
            my_score+=self.evaluate_move(board,move,self.player)
            opponent_score+=self.evaluate_move(board,move,self.opponent)
        return my_score-opponent_score
    def evaluate_move(self,board,move,player):
        row,col=move

        if board[row][col] != 0:
            return 0
    
        n=len(board)
        total_score=0

        board[row][col]=player

        for dx,dy in self.directions:
            count=1
            open_ends=0
            x,y=row+dx,col+dy
            while 0<=x<n and 0<=y<n and board[x][y]==player:
                count+=1
                x+=dx
                y+=dy
            
            if 0<=x<n and 0<=y<n and board[x][y]==0:
                open_ends+=1
            
            x,y=row-dx,col-dy
            while 0<=x<n and 0<=y<n and board[x][y]==player:
                count+=1
                x-=dx
                y-=dy
            
            if 0<=x<n and 0<=y<n and board[x][y]==0:
                open_ends+=1

            total_score+=self.pattern_score(count,open_ends)


        board[row][col]=0
        return total_score

    def find_opponent_danger(self,board):
        candidates=self.get_candidates(board)

        best_move=None
        best_score=0

        for move in candidates:
            score=self.evaluate_move(board,move,self.opponent)
            if score>best_score:
                best_score=score
                best_move=move
        
        if best_score>=10000:
            return best_move
        
        return None
    
    def minimax(self,board,depth,maximizing,alpha,beta):
        if depth==0:
            return self.evaluate_board(board)
        current_player=self.player if maximizing else self.opponent
        candidates=self.ordered_candidates(board,current_player)

        if not candidates:
            return self.evaluate_board(board)
        
        if maximizing:
            best_score=-10**18

            for move in candidates:
                row,col=move
                board[row][col]=self.player

                if self.check_win_at(board,row,col,self.player):
                    board[row][col]=0
                    return 10**12
                
                score=self.minimax(board,depth-1,False,alpha,beta)
                board[row][col]=0
                best_score=max(best_score,score)
                alpha=max(alpha,best_score)

                if beta<=alpha:
                    break
            
            return best_score
        else:
            best_score=10**18

            for move in candidates:
                row,col=move
                board[row][col]=self.opponent

                if self.check_win_at(board,row,col,self.opponent):
                    board[row][col]=0
                    return -10**12
                
                score=self.minimax(board,depth-1,True,alpha,beta)

                board[row][col]=0

                best_score=min(best_score,score)
                beta=min(beta,best_score)

                if beta<=alpha:
                    break
            return best_score



    def make_move(self, board):
        candidates=self.get_candidates(board)
        if not candidates:
            return None,None
        #下一步直接能赢
        for move in candidates:
            if self.is_winning_move(board,move,self.player):
                return move,None
        
        #下一步直接寄
        for move in candidates:
            if self.is_winning_move(board,move,self.opponent):
                return move,None
            
        best_move=None
        best_score=-10**18

        for move in candidates:
            score=self.evaluate_move(board,move,self.player)

            score+=self.evaluate_move(board,move,self.opponent)*0.8

            if score>best_score:
                best_score=score
                best_move=move
        skill_target=None

        if not self.skill_used:
            danger_move=self.find_opponent_danger(board)
            if danger_move is not None and danger_move!=best_move:
                skill_target=danger_move
                self.skill_used=True

        return best_move,skill_target

        # TODO: 在这里实现你的搜索算法来选择最佳移动
    
 