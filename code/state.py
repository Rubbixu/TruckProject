'''state variable'''



class state():
    def __init__(self, g, x, t, p):
        self.g = g
        self.x = x
        self.stage = t
        self.flag = p
        self.action_hist =[]
        self.cost = 0.0
        
    def getg(self): 
        return self.g
    
    def getx(self):
        return self.x
    
    def getStage(self):
        return self.stage

    def getActionPercent(self):
        return self.flag
    
    def getActionHistory(self):
        HL = self.action_hist[:]
        return HL
    
    def updateAction(self, oldState, action):
        self.action_hist = oldState.getActionHistory()
        self.action_hist.append(action)
    
    def setCost(self,cost):
        self.cost = cost
        
    def getCost(self):
        return self.cost

def stateTree(stage):
    tree = []
    for i in range(stage+1):
        tree.append({})
    return tree

