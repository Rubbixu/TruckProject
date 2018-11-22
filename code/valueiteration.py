from math import floor
from state import stateTree
import xlrd

class ValueIterationModel():
    def __init__(self,p=1.0,q=1.0,g=0.5):


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
        self.p = p
        self.q = q
        self.g_upper = 100
        self.g_lower = 0
        self.initial_g = g
        self.costNone = 0.1
        self.costMultiplier = 0.05
        self.gNone = 0.5
        self.gMultiplier = 0.02

    '''Utility function'''
    def setP(self,p):
        self.p = p

    def setq(self,q):
        self.q = q

    def setg(self,g):
        self.initial_g = g

    '''function to load data'''
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
    def checkWeight(self,x,t):
        '''Check in which segment currentState is'''
        rowCount = int(floor(x / self.distance_block))
        '''Check time period when we reach currentState.'''
        columnCount = int(floor(t * self.time_interval / self.time_block))
        '''Get information of driving condition and transform into driver's
        performance'''
        weatherWeight = self.parameter[rowCount][columnCount][0]
        trafficWeight = self.parameter[rowCount][columnCount][1]
        return weatherWeight,trafficWeight


    '''Calculate risk cost for each stage. When we arrive each state, we know
    driving condition, performance. With action we take, we will know risk for
    next period and our new driving condition and performance for new currentState
    '''
    def getCost(self, weight,g,percent,action):
        cost = (self.costNone*self.time_interval +
                self.costMultiplier*g*percent*action*self.time_interval*(weight**2))
        cost = round(cost,2)
        return cost


    '''Transition function: for each stage, we need know x, g, t and using
    'checkWeight' to find w.'''
    def transition(self, x, t, currentState, action):
        g,cost,history = currentState
        weatherWeight,trafficWeight = self.checkWeight(x,t)
        weight = 0.7*weatherWeight + 0.3*trafficWeight + 0.2
        '''25 here is block to decide segment. Then Check whether driver finish the whole route.
        If finished, we need check actual time we need by using variabel percent'''
        if x + action*self.time_interval > self.distance:
            action_true = self.distance - x
            percent = action_true / (action * self.time_interval)
            new_x = self.distance
        else:
            percent = 1.0
            new_x = x + action*self.time_interval
        new_g = g + percent*self.time_interval*weight*self.gMultiplier*action - self.time_interval*self.gNone*(action==0)
        new_g = max(round(new_g,2), 0)
        new_cost = cost + self.getCost(weight,new_g,percent,action)
        new_history = history[:]
        new_history.append(action)
        return new_g,new_cost,new_history,percent,new_x

    def checkArrivalOnTime(self,x,t):
        if self.maxSpeed * (self.stage - t)*self.time_interval + x >= self.distance:
            return True
        else:
            return False

    def gboundary(self,g):
        l = len(self.action)
        if g < self.g_lower:
            return 1,l
        if g> self.g_upper:
            return 0,1
        return 0,l

    '''Based on action history, reconstruct every state taken and print them out'''
    def reconstruct(self,history):
        currentState = (self.initial_g,0,[])
        x = 0
        t = 0
        gPlotList = [self.initial_g]
        cPlotList = [0]
        for a in history:
            new_g,new_cost,new_history,percent,x = self.transition(x,t,currentState,a)
            gPlotList.append(new_g)
            cPlotList.append(new_cost)
            t += 1
            print('Stage %d, action is %d, g is %.2f, cost is %.2f, travel distance is %.1f'% (t,a,new_g,new_cost,x))
            currentState = (new_g,new_cost,new_history)
        return gPlotList,cPlotList

    def checkRisk(self,x,t):
        weatherWeight,trafficWeight = self.checkWeight(x,t)
        l = len(self.action)
        if weatherWeight == 1 and trafficWeight == 1:
            return 0,1
        else:
            return 0,l

    def Optimizer(self,no_risk=0, num_of_stage=None, g_upper=100.0,g_lower=0.0):
        self.g_upper = g_upper
        self.g_lower = g_lower
        if num_of_stage == None or num_of_stage > self.stage:
            num_of_stage = self.stage
        bestObj = 10000
        states = stateTree(self.stage)
        states[0][0] = [(self.initial_g,0,[])]
        state_count = 0
        for t in range(self.stage):
            new_t = t + 1
            for x in states[t]:
                if not self.checkArrivalOnTime(x,t):
                    continue
                states[t][x].sort(key=lambda element: (element[0], element[1]))
                max_cost = 10000
                for currentState in states[t][x]:
                    state_count += 1
                    g,cost,_ = currentState
                    if cost >= max_cost:
                        continue
                    else:
                        max_cost = cost
                    ind_min,ind_max = self.gboundary(g)
                    if no_risk == 1:
                        ind_min,ind_max = self.checkRisk(x,t)
                    for a in self.action[ind_min:ind_max]:
                        new_g,new_cost,new_history,percent,new_x = self.transition(x,t,currentState,a)
                        if new_x == self.distance:
                            state_count += 1
                            currentObj = self.p*new_cost + (new_t-1 + percent)*self.time_interval*self.q
                            if currentObj < bestObj:
                                bestObj = currentObj
                                total_time = round((new_t-1 + percent)*self.time_interval,2)
                                best_action = new_history
                                best_c = new_cost
                        if ((new_t < num_of_stage) and (new_x < self.distance)):
                            newState=(new_g,new_cost,new_history)
                            if new_x not in states[new_t]:
                                states[new_t][new_x] = []
                                states[new_t][new_x].append(newState)
                            else:
                                states[new_t][new_x].append(newState)
        if bestObj == 10000:
            '''which indicates that no solution is found'''
            if no_risk == 1:
                print ("No Risk Policy is ON, and no solution is found")
                return None,None
            else:
                print ("I don't think this would ever happen")
            return 0
        print ("no risk policy ",no_risk == 1, "p value",self.p,", q value ",self.q,", total time ",total_time, ", total risk cost (before times p)",best_c,
               ", best action ",best_action,", optimal value ",bestObj, ", total stage considered ",state_count)
        return self.reconstruct(best_action)

    def Go(self,actions):
        currentState = (self.initial_g,0,[])
        x = 0
        t = 0
        for a in actions:
            new_g,new_cost,new_history,percent,x = self.transition(x,t,currentState,a)
            t += 1
            if x == self.distance:
                currentObj = self.p*new_cost + (t-1 + percent)*self.time_interval*self.q
                total_time = round((t-1 + percent)*self.time_interval,2)
                print ("p value",self.p,", q value ",self.q,", total time ",total_time, ", total risk cost (before times p)",new_cost,
               ", all actions executed ",actions == new_history,", objective value ",currentObj)
                return 0
            currentState = (new_g,new_cost,new_history)
        print("I dont think this is working")

    def NoStop(self, speed = None):
        '''default speed is maximum speed in actions'''
        if speed == None:
            speed = self.action[-1]
        currentState = (self.initial_g,0,[])
        x = 0
        t = 0
        while x < self.distance:
            new_g,new_cost,new_history,percent,x = self.transition(x,t,currentState,speed)
            t += 1
            currentState = (new_g,new_cost,new_history)
        currentObj = self.p*new_cost + (t-1 + percent)*self.time_interval*self.q
        total_time = round((t-1 + percent)*self.time_interval,2)
        print ("No Stop at speed ",speed,", p value",self.p,", q value ",self.q,", total time ",total_time, ", total risk cost (before times p)",new_cost,
               ", optimal value ",currentObj)
        return self.reconstruct(new_history)
    
