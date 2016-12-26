#!coding=utf-8

import heapq


#node=[(r,c),g,h,prenode]
#heapnode = [h,node,True]

#堆结构
class Aheap:
    def __init__(self):
        self.hnodelist = []
        self.pos2hnode = {}
        self.valid_hnode_num = 0

    #压入堆中一个节点,如果该节点对应的pos已经存在,则替换已有的那个节点
    def push(self,node):
        pos = node[0]
        if pos in self.pos2hnode:
            self.__remove_by_pos(pos)
        h = node[1] + node[2]
        heapnode = [h, node,True]
        heapq.heappush(self.hnodelist, heapnode)
        self.pos2hnode[pos] = heapnode
        self.valid_hnode_num+=1

    def __remove_by_pos(self,pos):
        if pos in self.pos2hnode:
            heapnode = self.pos2hnode.pop(pos)
            heapnode[2]=False
            self.valid_hnode_num-=1

    def contains_by_pos(self,pos):
        if pos in self.pos2hnode:
            return self.pos2hnode[pos][1]
        else:
            return None

    #小根堆,取小根堆的堆顶(最小值)
    def pop(self):
        while len(self.hnodelist):
            h,node,check = heapq.heappop(self.hnodelist)
            if check:
                self.valid_hnode_num-=1
                return node

    def size(self):
        return self.valid_hnode_num


class RasterHandler(object):
    def __init__(self,_data=[]):
        self.data=_data
        self.row = len(self.data)
        self.col = len(self.data[0]) if self.row > 0 else 0
        self.minval = float('+inf')
        self.maxval = float('-inf')
        self.meanval = 0
        self.midval = 0
        # if self.row!=0 and self.col!=0:
            # self.__precalculate()

    def __precalculate(self):
        sum = 0.0
        vallist = []
        for datalist in self.data:
            for val in datalist:
                if val<self.minval:
                    self.minval = val
                if val>self.maxval:
                    self.maxval
                sum+=val
                vallist.append(val)
        self.meanval = sum/(self.row*self.col)
        vallist.sort()
        self.midval = vallist[len(vallist)/2]




    def loaddata_sta_in(self,filepath):
        with open(filepath,'r') as fin:
            for line in fin:
                items = line.strip().split()
                tempdata_list = [float(val) for val in items]
                self.data.append(tempdata_list)
            self.row = len(self.data)
            self.col = len(self.data[0])
            # print('row=%s,col=%s'%(self.row,self.col))

    def get_srround_val(self,pos):
        r = pos[0]
        c = pos[1]
        resultlist = []
        curdata = self.data[r][c]
        p = 1.414
        if r-1>=0 and c-1>=0:
            resultlist.append(((r-1,c-1),(curdata+self.data[r-1][c-1])*p))
        if r-1>=0:
            resultlist.append(((r-1,c),curdata+self.data[r-1][c]))
        if r-1>=0 and c+1 <self.col:
            resultlist.append(((r-1,c+1),(curdata+self.data[r-1][c+1])*p))
        if c-1>=0:
            resultlist.append(((r,c-1),curdata+self.data[r][c-1]))
        if c+1<self.col:
            resultlist.append(((r, c+1), curdata+self.data[r][c+1]))
        if r+1<self.row and c-1>=0:
            resultlist.append(((r+1, c-1), (curdata+self.data[r+1][c-1])*p))
        if r+1<self.row:
            resultlist.append(((r + 1, c), curdata+self.data[r + 1][c]))
        if r+1<self.row and c+1 < self.col:
            resultlist.append(((r+1,c+1),(curdata+self.data[r+1][c+1])*p))
        # print("souroudlist=",resultlist)
        return resultlist

    def get_val_by_pos(self,pos):
        r = pos[0]
        c = pos[1]
        if r>=0 and r<self.row and c>=0 and c<self.col:
            return self.data[r][c]
        return 0

class Astar(object):
    def __init__(self,_data=[],sign_fun='astar_no'):
        self.raster = RasterHandler(_data)
        self.startpos = (0,0) #(row_number,col_number)
        self.endpos = (0,0)
        if sign_fun=='astar_no':
            self.fun_h = self.fun_h_zero
        elif sign_fun == 'astar_euc':
            self.fun_h = self.fun_h_euc_dis
        elif sign_fun == 'astar_man':
            self.fun_h = self.fun_h_manhadun_dis


    def fun_h_zero(self,cur_pos):
        return 0

    def fun_h_euc_dis(self,cur_pos):
        r = cur_pos[0]
        c = cur_pos[1]
        end_r = self.endpos[0]
        end_c = self.endpos[1]
        dis = ((r-end_r)**2+(c-end_c)**2)**0.5
        return dis*self.raster.midval

    def fun_h_manhadun_dis(self,cur_pos):
        r = cur_pos[0]
        c = cur_pos[1]
        end_r = self.endpos[0]
        end_c = self.endpos[1]
        return abs(end_r-r)+abs(end_c-c)



    def setstarpos(self,pos):
        self.startpos = pos

    def setendpos(self,pos):
        self.endpos = pos

    def loaddata_from_file(self,filepath):
        self.raster.loaddata_sta_in(filepath)

    def runAstar(self):
        open_heap = Aheap()
        close_dict = {}
        start_g = self.raster.get_val_by_pos(self.startpos)
        start_h = self.fun_h(self.startpos)
        startnode = [self.startpos,start_g,start_h,self.startpos]
        open_heap.push(startnode)

        def _getpath(node):
            resultlist = [node[0]]
            while node[0]!=self.startpos:
                node = close_dict[node[3]]
                resultlist.append(node[0])
            resultlist.reverse()
            return resultlist

        while  open_heap.size():
            curnode = open_heap.pop()
            curpos,cur_g,cur_h,cur_rep_pos = curnode
            close_dict[curpos]=curnode
            nextnodelist = self.raster.get_srround_val(curpos)
            for temppos,tempval in nextnodelist:
                if temppos in close_dict:
                    continue
                temp_h = self.fun_h(temppos)
                temp_g = cur_g + tempval
                temp_last_node = open_heap.contains_by_pos(temppos)
                temp_last_pos = curpos
                if temp_last_node and temp_last_node[1]<temp_g:
                    temp_g = temp_last_node[1]
                    temp_last_pos = temp_last_node[3] #这里认为启发式函数的值只与改点位置和终点位置有关,每个格子的启发函数值是确定的。
                temp_node=(temppos,temp_g,temp_h,temp_last_pos)
                if temppos==self.endpos:
                    return _getpath(temp_node)
                open_heap.push(temp_node)




import datetime
def test():
    starttime = datetime.datetime.now()
    star = Astar()
    star.loaddata_from_file('./data.txt')
    star.setstarpos((0,0))
    star.setendpos((50,50))
    curtime1 = datetime.datetime.now()
    print((curtime1-starttime).seconds)
    print(star.runAstar())
    curtime2 =datetime.datetime.now()
    print((curtime2-curtime1).seconds)

if __name__=='__main__':
    test()


















