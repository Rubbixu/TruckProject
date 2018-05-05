a = [(1,2),(3,0),(0,-1),(1,-10)]
a.sort(key = lambda element:(element[0],element[1]))
for x in a:
    u,v = x
    print u,v