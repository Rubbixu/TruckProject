'''run file'''
from valueiteration import ValueIterationModel
import matplotlib.pyplot as plt
''' change different p and q '''

p = 1.0
q = 0.01
g = 0
# =============================================================================
# p = float(input("Please insert p: "))
# q = float(input("Please insert q: "))
# =============================================================================
#print("\nThe result of original optimization: ")
#
#''' If you want to use a different dataset, replacing 'data.xlsx' with your filename'''
#
#a.readData('data.xlsx',2)
##print(a.parameter)
##print(a.stage)
##print(a.distance)
##a.printStage()
#a.ObjectiveOptimization(p,q)

#a.readData('data.xlsx',1)
''' change first argument to try a different speed '''
#a.NoStop(75,p,q)
#a.NoRisk(75,p,q)
print("\nThe result of value iteration: ")
b = ValueIterationModel(p,q,g)
b.readData('data_6.21.xlsx',0)
g1,c1 = b.Optimizer(num_of_stage = 16)
# =============================================================================
# print('---------------------------------')
# g2,c2 = b.Optimizer(1)
# if g2 == None:
#     g2 = [0] * len(g1)
#     c2 = [0] * len(g1)
# print('---------------------------------')
# g3,c3 = b.NoStop()
# =============================================================================

# =============================================================================
# fig, axs = plt.subplots(2, 1)   
# 
# axs[0].plot(g1, '-rD', g2, '-bs', g3, '-g^')
# axs[0].set_title('g plot')
# axs[0].set_xlabel('stage')
# axs[0].set_ylabel('g')
# axs[1].plot(c1, '-rD', c2, '-bs', c3, '-g^')
# axs[1].set_xlabel('stage')
# axs[1].set_title('cost plot')
# axs[1].set_ylabel('cost')
# plt.subplots_adjust(hspace=0.8)
# fig.show()
# =============================================================================
q_list=[0.01,0.3,0.4,1,2,3,5,10]
b.pqratio_plot(q_list,16)




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
        
