a = []
for i in range(4):
    a.append({})

a[0][0.50] = 1 
for i in range(4):
    if 0.5 in a[i]:
        print i
print a[0][1]
