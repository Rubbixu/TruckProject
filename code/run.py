'''run file'''
from valueiteration import ValueIterationModel
from PetModel import PetModel

a = PetModel()
''' change different p and q '''

p = 1.0
q = 1.0
# =============================================================================
# p = float(input("Please insert p: "))
# q = float(input("Please insert q: "))
# =============================================================================
print("\nThe result of original optimization: ")

''' If you want to use a different dataset, replacing 'data.xlsx' with your filename'''

a.readData('data.xlsx',1)
#print(a.parameter)
#print(a.stage)
#print(a.distance)
#a.printStage()
a.ObjectiveOptimization(p,q)

''' change first argument to try a different speed '''
a.NoStop(75,p,q)
a.NoRisk(75,p,q)
# =============================================================================
# print("\nThe result of value iteration: ")
# b = ValueIterationModel(p,q)
# b.Optimizer()
# =============================================================================
# =============================================================================
# decision = None
# while (decision != 'y' and decision != 'n'): 
#     decision = raw_input("Do you want to print all states(y/n): ")
#     if decision == 'y':
#         print("\nAll states will be printed below\n")
#         a.printStage()
#     elif decision == 'n':
#         break
# =============================================================================
        
