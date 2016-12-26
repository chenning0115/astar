

import random
import datetime
def gendata(row,col,path):
    with open(path,'w') as fout:
        for i in range(row):
            templist = []
            for j in range(col):
                templist.append(str(random.randint(0,1000)))
            fout.write('\t'.join(templist)+'\n')





if __name__=='__main__':
    # gendata(1000,1000,'./data.txt')
    mydict = {}
    starttime = datetime.datetime.now()
    num = 10**9
    for i in range(num):
        pass

    curtime = datetime.datetime.now()
    print((curtime - starttime).seconds)



