from math import floor
from state import state,stateTree


class ValueIterationModel():
    def __init__(self,p,q):
        
        
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
        """time period for each stage"""
        self.time_interval = 0.5
        """Number of stages we want to check. Here we can use this to limit the
        travel time, since sometimes we want driver to arrive in a time window.
        For example, if stage is 4, that means we want to driver finish route within 
        2 hours. """
        self.stage = 4
        self.time_block = 0.5
        self.distance_block = 25
        self.p = p
        self.q = q
    
    
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
    
    def Optimizer(self):
        bestObj = 10000
        states = stateTree(self.stage)
        initialState = state(0.5,0,0,1.0)
        states[0][0] = {}
        states[0][0][0.5] = initialState
        for t in range(self.stage):
            for x in states[t]:
                for g in states[t][x]:
                    currentState = states[t][x][g]
                    for a in self.action:
                        newState = self.transition(currentState,a)
                        new_x = newState.getx()
                        new_t = newState.getStage()
                        if new_x == self.distance:
                            r = newState.getCost()
                            per = newState.getActionPercent()
                            currentObj = self.p*r + (new_t-1 + per)*self.time_interval*self.q
                            if currentObj < bestObj:
                                bestObj = currentObj
                                total_time = (new_t-1 + per)*self.time_interval
                                best_action = newState.getActionHistory()
                                best_r = r
                        if ((new_t < self.stage) and (new_x < self.distance)):
                            new_g = newState.getg()
                            if new_x not in states[new_t]:
                                states[new_t][new_x] = {}
                                states[new_t][new_x][new_g] = newState
                            else:
                                if new_g not in states[new_t][new_x]:
                                    states[new_t][new_x][new_g] = newState
                                else:
                                    r = newState.getCost()
                                    r_old = states[new_t][new_x][new_g].getCost()
                                    if r < r_old:
                                        states[new_t][new_x][new_g] = newState
        print ("p value",self.p,", q value ",self.q,", total time ",total_time, ", total risk cost (before times p)",best_r,
               ", best action ",best_action,", optimal value ",bestObj)
                                    
                                