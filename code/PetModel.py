

from state import state
from math import floor
import xlrd

class PetModel():
    def __init__(self):
        
        
        """also could import parameters in excel, parameter is weather and traffic 
        information, we called these as travel comditions'
        Row means each segment for the whole route; column means different time
        period that we will have varies driving conditions according time for each
        segment"""
        self.parameter = [[(0,1),(1,1),(0,0),(1,0)],
                           [(1,0),(1,0),(0,1),(0,1)],
                           [(1,0),(0,1),(1,0),(0,1)],
                           [(0,0),(0,0),(0,0),(0,0)]]
        """Distance is number of whole route from origin to destination"""
        self.distance = 100
        """action sets"""
        self.action = [0,55,75]
        self.maxSpeed = self.action[-1]
        """time period for each stage"""
        self.time_interval = 0.5
        """Number of stages we want to check. Here we can use this to limit the
        travel time, since sometimes we want driver to arrive in a time window.
        For example, if stage is 4, that means we want to driver finish route within 
        2 hours. """
        self.stage = 4
        self.time_block = 0.5
        self.distance_block = 25
    
    def readData(self, filename, sheet_index):
        wb = xlrd.open_workbook(filename)
        sh = wb.sheet_by_index(sheet_index)
        row = sh.nrows - 2
        col = sh.ncols - 2
        self.parameter = []   

        for i in range(0,row,2):
            rowinfo = []
            for j in range(col):
                weightInfo = int(sh.cell(i+2,j+2).value)
                trafficInfo = int(sh.cell(i+3,j+2).value)
                rowinfo.append((weightInfo,trafficInfo))
            self.parameter.append(rowinfo)
        self.distance = self.distance_block * row/2
        self.stage = col
    
    '''Caculate driving performance for each state.
       Current state is to record the distance from origin and block is 
       the criteria to get each segment.''' 
    def checkWeight(self,currentState):
        x = currentState.getx()
        t = currentState.getStage()
        '''Check in which segment currentState is'''
        rowCount = int(floor(x / self.distance_block))
        '''Check time period when we reach currentState.'''
        columnCount = int(floor(t * self.time_interval / self.time_block))
        '''Get information of driving condition and transform into driver's 
        performance'''
#        print(rowCount,columnCount)
        weatherWeight = self.parameter[rowCount][columnCount][0]
        trafficWeight = self.parameter[rowCount][columnCount][1]
        return 0.7*weatherWeight + 0.3*trafficWeight + 0.2
    
    
    '''Calculate risk cost for each stage. When we arrive each state, we know
    driving condition, performance. With action we take, we will know risk for 
    next period and our new driving condition and performance for new currentState
    '''
    def getCost(self, weight,g,percent,action):
        cost = (0.002*self.time_interval +
                0.005*g*percent*action*self.time_interval*(weight**2))
        return cost


    '''Transition function: for each stage, we need know x, g, t and using 
    'checkWeight' to find w.'''
    def transition(self, currentState, action):
        g = currentState.getg()
        x = currentState.getx()
        t = currentState.getStage()
        cost = currentState.getCost()
        weight = self.checkWeight(currentState)
        '''25 here is block to decide segment. Then Check whether driver finish the whole route. 
        If finished, we need check actual time we need by using variabel percent'''
        if x + action*self.time_interval > self.distance:
            action_true = self.distance - x
            percent = action_true / (action * self.time_interval)
            new_x = self.distance
        else:
            percent = 1.0
            new_x = x + action*self.time_interval
        new_g = g + percent*self.time_interval*weight*0.1*action - self.time_interval*0.1*(action==0)
        new_g = round(new_g,2)
        new_t = t + 1
        new_p = percent
        newState = state(new_g,new_x,new_t,new_p)
        newState.updateAction(currentState,action)
        newState.setCost(cost+self.getCost(weight,new_g,percent,action))
        return newState
    
    def checkArrivalOnTime(self,x,t):
        if self.maxSpeed * (self.stage - t)*self.time_interval + x >= self.distance:
            return True
        else:
            return False
    '''Record stage, currentState, action, g, risk cost, percent'''
    def printStage(self):
        initialState = state(0.5,0,0,1.0)
        initialState.setCost(0)
        stageList = [initialState]
        while stageList:
            currentState = stageList.pop(0)
            g = currentState.getg()
            c = currentState.getCost()
            x = currentState.getx()
            t = currentState.getStage()
            al = currentState.getActionHistory()
            p = currentState.getActionPercent()
            print("stage ",t,", position ",x,", action ",al,", cost ",c, g,p)
            if ((t < self.stage) and (x < self.distance) and self.checkArrivalOnTime(x,t)):
                for a in self.action:
                    newState = self.transition(currentState,a)
                    stageList.append(newState)
    
    
    def ObjectiveOptimization(self,p,q):
        initialState = state(0.5,0,0,1.0)
        initialState.setCost(0)
        stageList = [initialState]
        endState = None
        bestObj = 10000
        stageCount = 0
        while stageList:
            currentState = stageList.pop(0)
            x = currentState.getx()
            t = currentState.getStage()
            stageCount += 1
            if x == self.distance:
                per = currentState.getActionPercent()
                r = currentState.getCost()
                currentObj = p*r + (t-1 + per)*self.time_interval*q
                if currentObj < bestObj:
                    endState = currentState
                    bestObj = currentObj
                    total_time = (t-1 + per)*self.time_interval
                    best_r = r
            
            if ((t < self.stage) and (x < self.distance) and self.checkArrivalOnTime(x,t)):
                for a in self.action:
                    newState = self.transition(currentState,a)
                    stageList.append(newState)

        best_action = endState.getActionHistory()
        print ("p value",p,", q value ",q,", total time ",total_time, ", total risk cost (before times p)",best_r,
               ", best action ",best_action,", optimal value ",bestObj, ", total stage considered ",stageCount)

    def NoStop(self,speed,p,q):
        currentState = state(0.5,0,0,1.0)
        currentState.setCost(0)
        distance = 0
        while distance < self.distance:
            currentState = self.transition(currentState,speed)
            distance = currentState.getx()
        per = currentState.getActionPercent()
        t = currentState.getStage()
        t = (t - 1 + per) * self.time_interval
        r = currentState.getCost()
        currentObj = p*r + t*q
        print ("No Stop at speed ",speed)
        print ("p value",p,", q value ",q,", total time ",t, ", total risk cost (before times p)",r,
               ", optimal value ",currentObj)
    
    def NoRisk(self,p,q):   
        initialState = state(0.5,0,0,1.0)
        initialState.setCost(0)
        stageList = [initialState]
        endState = None
        bestObj = 10000
        stageCount = 0
        while stageList:
            currentState = stageList.pop(0)
            x = currentState.getx()
            t = currentState.getStage()
            stageCount += 1
            if x == self.distance:
                per = currentState.getActionPercent()
                r = currentState.getCost()
                currentObj = p*r + (t-1 + per)*self.time_interval*q
                if currentObj < bestObj:
                    endState = currentState
                    bestObj = currentObj
                    total_time = (t-1 + per)*self.time_interval
                    best_r = r
            
            if ((t < self.stage) and (x < self.distance) and self.checkArrivalOnTime(x,t)):
                rowCount = int(floor(x / self.distance_block))
                '''Check time period when we reach currentState.'''
                columnCount = int(floor(t * self.time_interval / self.time_block))
                '''Get information of driving condition and transform into driver's 
                performance'''
                weatherWeight = self.parameter[rowCount][columnCount][0]
                trafficWeight = self.parameter[rowCount][columnCount][1]
                if weatherWeight == 1 and trafficWeight == 1:
                    actions = [55,75]
                else:
                    actions = self.action
                for a in actions:
                    newState = self.transition(currentState,a)
                    stageList.append(newState)

        best_action = endState.getActionHistory()
        print ("No Risk Policy")
        print ("p value",p,", q value ",q,", total time ",total_time, ", total risk cost (before times p)",best_r,
               ", best action ",best_action,", optimal value ",bestObj, ", total stage considered ",stageCount)
                   
  
        
        