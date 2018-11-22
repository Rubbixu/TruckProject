import xlrd

wb = xlrd.open_workbook('data.xlsx')
sh = wb.sheet_by_index(1)
row = sh.nrows - 2
col = sh.ncols - 2
para = []   

for i in range(0,row,2):
    rowinfo = []
    for j in range(col):
        weightInfo = int(sh.cell(i+2,j+2).value)
        trafficInfo = int(sh.cell(i+3,j+2).value)
        rowinfo.append((weightInfo,trafficInfo))
    para.append(rowinfo)
