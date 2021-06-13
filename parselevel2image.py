import cv2
import numpy as np
import matplotlib.pyplot as plt
import pickle
import logging
import pdb
import pandas as pd
import os
import datetime
import time
has_init=False
row_num=57
col_num=6
tb_num=342
lasttime = 92500
lastprice =None
buyorder =None
sellorder =None
timelist = []
pricelist = []
tradelist = []
buylist = []
selllist = []
bslist=[]
# %load_ext autoreload
# %autoreload 2
# from parselevel2image import *
# arr1  =cv2.imread(r"2.jpg")
# print(arr1.shape)

# parselevel2price(arr1)
#save_pickle()

logger = logging.getLogger('root')
FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
logging.basicConfig(format=FORMAT)
logger.setLevel(logging.INFO)
data_input = open('ocr_conf.pkl', 'rb')
# digit_arr2=[None]*10
empty_arr2=np.full((10, 5), 255)

(digit_arr, digt_marsk_arr, empty_arr,char_s_arr,char_b_arr,digit_arr2) = pickle.load(data_input)
prec3_set=set()
data_input.close()
digit_width=6
digit_sep=2
colon_width=1
x_axis_start=1
digit_hight=11
row_sep=6
col_sep=317
time_pixel_threshold=190
price_pixel_threshold=210

first_time_col_bound=50
first_price_col_bound=128
first_deal_col_bound=192
first_buy_col_bound=251
first_sell_col_bound=307

trans_bound=4
dot_width=1



def setlastprice(_lastprice):
    global lastprice
    lastprice = _lastprice

def init(path,_first_time_col_bound,_first_price_col_bound,_first_deal_col_bound,_first_buy_col_bound,_first_sell_col_bound,_col_sep):
    # pdb.set_trace()
    global col_sep
    col_sep = _col_sep

    arr = cv2.imread(path)
    imhight=arr.shape[0]
    imwidth=arr.shape[1]
    global row_num
    row_num=int(imhight/(digit_hight+row_sep))
    global col_num
    col_num=round(imwidth/col_sep)
    global tb_num
    tb_num = row_num*col_num
    global first_time_col_bound
    first_time_col_bound=_first_time_col_bound
    global first_price_col_bound
    first_price_col_bound=_first_price_col_bound
    global first_deal_col_bound
    first_deal_col_bound=_first_deal_col_bound
    global first_buy_col_bound
    first_buy_col_bound =_first_buy_col_bound
    global first_sell_col_bound
    first_sell_col_bound = _first_sell_col_bound
    global has_init
    has_init = True

def save_pickle():
    data_output = open('ocr_conf.pkl', 'wb')
    pickle.dump((digit_arr, digt_marsk_arr, empty_arr,char_s_arr,char_b_arr,digit_arr2), data_output)
    data_output.close()

def ocrdigit(arr, bound,ref=None):

    digit_str=""
    char_arr = arr[:, bound - digit_width:bound]
    i=-1
    get_dot=False
    if ref is not None:
        while True:
            i += 1
            if i >= len(ref):
                break
            digit = int(ref[i])
            if np.logical_or((char_arr == digit_arr[digit]), digt_marsk_arr[digit]).all():
                digit_str += ref[i]
                bound = bound - digit_width - digit_sep
                char_arr = arr[:, bound - digit_width:bound]
                continue
            else:
                # pdb.set_trace()
                #
                # updateMarsk(digit,char_arr,True,22)
                break
    else:
        while True:
            i+=1
            if (char_arr == empty_arr).all():
                break

            ret, ret_val = arr2int(char_arr)
            if ret:
                digit_str += str(ret_val)
                bound = bound - digit_width - digit_sep
                char_arr = arr[:, bound - digit_width:bound]
            else:
                # may be get dot

                cid, errnum = findMatch(ret_val)

                errnum= 66 - np.sum(np.logical_or((char_arr == digit_arr[cid]), digt_marsk_arr[cid]))
                logger.debug(f'get error {errnum} for {cid}!')
                # updateMarsk(cid, ret_val,False)
                if errnum<2:
                    pdb.set_trace()
                    digit_str += str(cid)
                    bound = bound - digit_width - digit_sep
                    char_arr = arr[:, bound - digit_width:bound]
                    continue
                if digit_str is "":
                    logger.debug(f'digit_str is empty ,can not be dot!')
                    bound = bound - digit_width - digit_sep
                    char_arr = arr[:, bound - digit_width:bound]
                    continue
                if not get_dot:
                    digit_str += str(".")
                    bound = bound - dot_width - digit_sep
                    char_arr = arr[:, bound - digit_width:bound]
                    get_dot=True
                    logger.debug(f'get dot!')
                else:
                    # pdb.set_trace()
                    logger.debug('not get dot or dight ! break now !')
                    # logger.debug(ret_val)
                    break
    if digit_str=="":
        return None,False
    return digit_str,get_dot
def ocrVolume(arr,deal_col_bound,buy_col_bound,sell_col_bound):
    #check b or s
    #pdb.set_trace()
    bs=""
    bs_arr=arr[:,deal_col_bound-digit_width:deal_col_bound]
    b_num=np.sum(char_b_arr == bs_arr)
    s_num=np.sum(char_s_arr == bs_arr)
    e_num=np.sum(empty_arr == bs_arr)
    if b_num >e_num:
        if b_num >s_num:
            bs="B"
        else:
            bs="S"
    elif s_num >e_num:
        bs="S"
    deal_col_bound = deal_col_bound - digit_width - digit_sep
    ref,get_dot=ocrdigit(arr,deal_col_bound)
    bs=ref[::-1]+bs
    if get_dot:
        ref=None
    buy,_=ocrdigit(arr,buy_col_bound,ref)
    sell,_=ocrdigit(arr,sell_col_bound,ref)
    return (bs,buy[::-1],sell[::-1])

def ocrTimeArr(time_arr):
    y=time_arr.shape[1]
    second1= time_arr[:, y - digit_width:y]
    y=y-digit_width-digit_sep
    second2= time_arr[:, y - digit_width:y]
    y=y-digit_width-digit_sep-colon_width-digit_sep
    minute1= time_arr[:, y - digit_width:y]
    y=y-digit_width-digit_sep
    minute2= time_arr[:, y - digit_width:y]
    y=y-digit_width-digit_sep-colon_width-digit_sep
    hour1= time_arr[:, y - digit_width:y]
    return (hour1,minute2,minute1,second2,second1)

def arr2int(arr,last=None):
    if last is not None:
        if np.logical_or(arr ==digit_arr[last] ,digt_marsk_arr[last]).all():
            return 1,last

    for (cid,c) in enumerate( digit_arr):
        if np.logical_or(arr ==digit_arr[cid] ,digt_marsk_arr[cid]).all():
            return 1,cid
    return 0,arr
def arr2int2(arr):
    for (cid,c) in enumerate( digit_arr2):
        if (arr ==digit_arr2[cid]).all():
            return 1,cid
    return 0,arr
def ocrVolCol(colVol,i):
    x = x_axis_start
    printlist = []
    deal_col_bound=first_deal_col_bound+i * col_sep
    buy_col_bound=first_buy_col_bound+i * col_sep
    sell_col_bound = first_sell_col_bound+i * col_sep
    for i in range(round(colVol.shape[0] / (digit_hight + row_sep)) - 1):
        tupl=ocrVolume(colVol[x:x + digit_hight, :],deal_col_bound,buy_col_bound,sell_col_bound)
        x = x + digit_hight + row_sep
        printlist.append(tupl)
    for p in printlist:
        print(p)


def ocrTimeCol(coltime,lasttime = "start"):
    #     pdb.set_trace()
    x = x_axis_start   # config
    #     total is 57 row ,notice whether has 57 row in each colum section when call from pyautogui,
    last_time_arrs=[9,2,5,0,0]
    printlist=[]
    ret_val=-1
    for i in range(round(coltime.shape[0] / (digit_hight+row_sep)) - 1):
        timearrs = ocrTimeArr(coltime[x:x + digit_hight, :])
        if (timearrs[0] == empty_arr).all():
            # print(lasttime)
            printlist.append(lasttime)
        else:
            outstr = ""
            for (tid,_) in enumerate(timearrs):
                if tid == len(timearrs)-1:
                    #second1 not use last value
                    ret, ret_val = arr2int(timearrs[tid])
                else:
                    ret, ret_val = arr2int(timearrs[tid],last_time_arrs[tid])
                if not ret:
                    print(ret_val)
                    return ret_val,lasttime
                last_time_arrs[tid]=ret_val
                outstr = outstr + str(ret_val)

            # print(i, outstr)
            printlist.append(outstr)
            lasttime = outstr
        x = x + digit_hight+row_sep
    for p in printlist:
        print(p)
    return ret_val,lasttime

def updateMarsk(id,_arr,update=True,tol=20):
    #pdb.set_trace()

    print("before update marsk:",id)
    print(digt_marsk_arr[id])
    print(np.sum(digt_marsk_arr[id]))
    new=np.logical_or((_arr!=digit_arr[id]),digt_marsk_arr[id])

    print("after update marsk:",id)
    errsum=np.sum(new)
    print("after update marsk errsum:",errsum)
    if update:
        if errsum>tol:
            print("not update marsk id {} for error {} >{}".format(id,errsum,tol))
        else:
            digt_marsk_arr[id]=new
    return errsum

def findMatch(arr):
    bestid=0
    besterr=1000
    for (cid,c) in enumerate( digit_arr):
        currenterr=np.sum(arr != c)
        if besterr>currenterr:
            besterr=currenterr
            bestid=cid
    return bestid,besterr

def parselevel2vol(arr):
    arrg = cv2.cvtColor(arr, cv2.COLOR_BGR2GRAY)
    arrg[arrg >= time_pixel_threshold] = 255
    arrg[arrg < time_pixel_threshold] = 0
    for i in range(round(arr.shape[1] / col_sep)):
        ocrVolCol(arrg, i)

def parselevel2time(arr):
    arrg = cv2.cvtColor(arr, cv2.COLOR_BGR2GRAY)
    arrg[arrg >= time_pixel_threshold] = 255
    arrg[arrg < time_pixel_threshold] = 0
    lasttime="start"
    for i in range(round(arrg.shape[1]/col_sep)):
        ret_val, lasttime = ocrTimeCol(arrg[:, :first_time_col_bound + i * col_sep], lasttime)
        while not isinstance(ret_val, int):

            cid, errnum = findMatch(ret_val)
            if errnum > 10:
                print("not findMatch  cid {}, errnum {},ret_val {} !".format(cid, errnum,ret_val))
            if updateMarsk(cid, ret_val) > 10:
                break
            ret_val, lasttime = ocrTimeCol(arrg[:, :first_time_col_bound + i * col_sep], lasttime)

def getBinaryThreshold(arr):
    sa=np.sort(arr.flatten())
    sb=np.append(sa,sa[-1])
    diff = sb[1:] - sa
    maxid = np.argmax(diff)
    return sa[maxid] + (sa[maxid+1] -sa[maxid])/2
def updateVollist(arr, deal_col_bound, buy_col_bound, sell_col_bound,tb_index,arrg_,x):
    # check b or s
    global  buyorder
    global  sellorder
    arrg_2=arrg_[x: x + digit_hight,:]
    bs = 0
    bs_arr = arr[:, deal_col_bound - digit_width:deal_col_bound]
    b_num = np.sum(char_b_arr == bs_arr)
    s_num = np.sum(char_s_arr == bs_arr)
    e_num = np.sum(empty_arr == bs_arr)
    if b_num > e_num:
        if b_num > s_num:
            bs = 1
        else:
            bs = -1
    elif s_num > e_num:
        bs = -1
    bslist[tb_index]=bs
    ref, get_dot = ocrdigit(arr, deal_col_bound - digit_width - digit_sep)
    tradelist[tb_index] = float(ref[::-1])
    if get_dot:
        ref = None
    buy, _ = ocrdigit(arr, buy_col_bound, ref)
    sell, _ = ocrdigit(arr, sell_col_bound, ref)

    if buy==None:
        # pdb.set_trace()
        #check if is order char
        if arrg_2[:, buy_col_bound - digit_width:buy_col_bound].max() -arrg_2[:, buy_col_bound - digit_width:buy_col_bound].min()> 50:
            buylist[tb_index] = -2
    else:
        buylist[tb_index] = float(buy[::-1])


    if sell==None:
        #check if is order char
        if arrg_2[:, sell_col_bound - digit_width:sell_col_bound].max() -arrg_2[:, sell_col_bound - digit_width:sell_col_bound].min()> 50:
            selllist[tb_index] = -2
            # pdb.set_trace()
    else:
        selllist[tb_index] = float(sell[::-1])

    def ocrOrderChar(x_,bound,leftbound):
        # pdb.set_trace()
        arr = arrg_[x_: x_+10, leftbound:bound]

        threshold = getBinaryThreshold(arr)
        arrg_change =arrg_[x_: x_ + 10, leftbound:bound].copy()
        if np.sum(arrg_change < threshold) > arrg_change.shape[0]*arrg_change.shape[1]/2:
            arrg_change[arrg_change > threshold] = 0
            arrg_change[arrg_change !=0]=255
        else:
            arrg_change[arrg_change < threshold] = 0
            arrg_change[arrg_change > threshold] = 255

        y = arrg_change.shape[1]
        if (arrg_change[0, y - 5:y] == 255).all():
            return 0
        i=0
        vol=0


        while True:
            if (arrg_change[:, y - 5:y] == empty_arr2).all():
                break
            ret, ret_val = arr2int2(arrg_change[:, y - 5:y])

            if not ret:

                print(ret_val)
                pdb.set_trace()
                return
            y = y - 7
            vol += 10 ** i * ret_val
            i += 1
        return vol
    if buylist[tb_index] != -2:
        buyorder = None
    elif buyorder == None:

        ret = ocrOrderChar(x+2,buy_col_bound,deal_col_bound)
        if not ret:
            ret =  ocrOrderChar(x+10,buy_col_bound,deal_col_bound)
        buyorder = ret
        buylist[tb_index] = buyorder
    if selllist[tb_index] != -2:
        sellorder =None
    elif sellorder ==None:
        ret = ocrOrderChar(x + 2, sell_col_bound, buy_col_bound)
        if not ret:
            ret = ocrOrderChar(x + 10, sell_col_bound, buy_col_bound)
        sellorder=ret
        selllist[tb_index]=sellorder

def updatePricelist(price_arr,last_price_str,tb_index,precision):
    y = price_arr.shape[1]
    last_len = len(last_price_str)
    # left of dot
    i=0
    while True:
        if i>last_len-2 and (price_arr[:, y - digit_width:y] == empty_arr).all():
            break
        ret, ret_val = arr2int(price_arr[:, y - digit_width:y], int(last_price_str[last_len - i - 1]))

        if not ret:
            pdb.set_trace()
            print(ret_val)
            return

        y = y - digit_width - digit_sep
        if i== precision-1:
            y = y - dot_width - digit_sep
        pricelist[tb_index] += 10 ** i * ret_val
        i += 1
    pricelist[tb_index]=str(pricelist[tb_index])
    return pricelist[tb_index]
def updateTimelist(timearrs,last_time_arrs,tb_index):
    global  lasttime
    if (timearrs[0] == empty_arr).all():
        timelist[tb_index] = lasttime
    else:

        for (tid, _) in enumerate(timearrs):
            if tid == 4:
                # second1 not use last value
                ret, ret_val = arr2int(timearrs[tid])
            else:
                ret, ret_val = arr2int(timearrs[tid], last_time_arrs[tid])
            if not ret:
                pdb.set_trace()
                print(ret_val)
                return
            last_time_arrs[tid] = ret_val

        timelist[tb_index] = last_time_arrs[0] * 10000 + last_time_arrs[1] * 1000 + last_time_arrs[2] * 100 + \
                             last_time_arrs[3] * 10 + last_time_arrs[4]
        if last_time_arrs[0] != 9:
            timelist[tb_index] +=100000
        lasttime = timelist[tb_index]
def detecbound(arr,list,tb_index):

    if arr.min()>=170 and arr.max() <190:
        # get bound

        if list[tb_index] == None or list[tb_index] == -2:
            list[tb_index] = -3
        if tb_index+1<tb_num:
            list[tb_index+1] = -1
        return True
def regOverlap(arr,ref=None):
    if ref is not None:
        digit_str, _ = ocrdigit(arr,arr.shape[1],str(ref)[::-1])
        ret_val = int(digit_str[::-1])
        if ret_val != ref:

            print(f"time count checked failed {ref}")
            return
        else:
            print(f"time count checked {ref}")
            return
    x = x_axis_start
    x = x + digit_hight + row_sep
    digit_str,_ =ocrdigit(arr[x:x+digit_hight, :], first_time_col_bound+2, ref=None)
    ret_val= int(digit_str[::-1])

    if ret_val<tb_num:
        overlap =tb_num - ret_val+2
        logger.info(f'get return {ret_val},get overlap {overlap}')
        return overlap
    else:
        return 0

def printlist(plist):

    for r in range(row_num):
        s=""
        for ci in range(col_num):
            s=s+str(plist[ci*row_num+r])+"\t"
        print(s)

def img2pd(arr,path,precision,mode,checkoverlap=False):
    global has_init
    if not has_init:
        print("img2pd  init first !")
    global buyorder
    global sellorder
    global timelist
    timelist = [None] * tb_num
    global pricelist
    pricelist = [0] * tb_num
    global tradelist
    tradelist = [None] * tb_num
    global buylist
    buylist = [None] * tb_num
    global selllist
    selllist = [None] * tb_num
    global bslist
    global lasttime
    bslist = [None] * tb_num
    arrg = cv2.cvtColor(arr, cv2.COLOR_BGR2GRAY)
    arrg_2 = arrg.copy()

    str_lastime = str(lasttime)
    if len(str_lastime) == 5:
        str_lastime = "0" + str_lastime
    last_time_arrs = [int(x) for x in str_lastime]

    tb_index = 0
    global lastprice
    # pdb.set_trace()
    # BINARY the arr
    for ci in range(col_num):
        colprice = arrg[:, first_time_col_bound + ci * col_sep:first_price_col_bound + ci * col_sep]
        colprice[colprice >= price_pixel_threshold] = 255
        colprice[colprice < price_pixel_threshold] = 0

    arrg[arrg >= time_pixel_threshold] = 255
    arrg[arrg < time_pixel_threshold] = 0
    overlap = 0
    if checkoverlap:
        overlap = regOverlap(arrg)
    for ci in range(col_num):
        x = x_axis_start


        coltime = arrg[:, :first_time_col_bound + ci * col_sep]
        # coltime_count = arrg[:, :first_time_col_bound+2 + ci * col_sep]

        deal_col_bound = first_deal_col_bound + ci * col_sep
        buy_col_bound = first_buy_col_bound + ci * col_sep
        sell_col_bound = first_sell_col_bound + ci * col_sep

        for r in range(row_num):

            timearrs = ocrTimeArr(coltime[x:x + digit_hight, :])
            # if tb_index >0 :
            #     regOverlap(coltime_count[x:x + digit_hight, :], tb_index+1)
            updateTimelist(timearrs, last_time_arrs,tb_index)

            colprice = arrg[:, first_time_col_bound + ci * col_sep:first_price_col_bound + ci * col_sep]

            lastprice=updatePricelist(colprice[x:x + digit_hight, :], lastprice, tb_index,precision)
            updateVollist(arrg[x:x + digit_hight, :], deal_col_bound, buy_col_bound, sell_col_bound,tb_index,arrg_2,x)
            bound_arr=arrg_2[x + digit_hight + trans_bound, buy_col_bound - digit_width:buy_col_bound]
            if detecbound(bound_arr,buylist,tb_index):
                buyorder=None
            bound_arr = arrg_2[x + digit_hight + trans_bound, sell_col_bound - digit_width:sell_col_bound]
            if detecbound(bound_arr, selllist, tb_index) :
                sellorder=None
            tb_index+=1
            x = x + digit_hight + row_sep

    pd.DataFrame({'time':timelist[overlap:],'price':pricelist[overlap:],'trade':tradelist[overlap:],'bs':bslist[overlap:],'buy':buylist[overlap:],'sell':selllist[overlap:]}).to_csv(path,header=False,index=False,mode=mode)
    lasttime=timelist[-1]

def mergeOrderlist(lis):
    order_begin=-1
    order=[]
    order_price=None
    for i in range(len(lis)):

        if pd.isnull(lis[i]) and  order_begin == -1:
            order_begin = i
            continue
        if lis[i] >= 0:
            continue

        # begin
        if lis[i]==-1  and  order_begin == -1:
            order_begin = i

        if lis[i] == -2 :
            if order_price is  None:
                order_price = lis[i - 1]
            if order_begin == -1:
                order_begin=i-1

        if lis[i]==-3:
            if order_price is not None:
                if order_begin == -1:
                    pdb.set_trace()
                    print("error occur in mergeOrderdf")
                    return

                order.append([order_begin,i,order_price])
                order_price = None
                order_begin = -1
            #fake order merge to last order
            elif lis[i-1] >0: #tow block order
                order.append([i-1, i,lis[i-1]])
                order_begin = -1
            else:
                order[-1][1]=i
    return order

def changeUTF8(filename):
    # filename = r'/home/aistudio/mydata/detail/20200403'
    with open(filename, 'rb+') as f:
        data = f.read().decode('gb2312').encode('utf-8')
        f.seek(0)
        f.truncate()
        f.write(data)

def getprecisionset(filename):
    fo = open(filename)
    text_lines = fo.readlines()
    for line in text_lines[1:-1]:
        row = line.split()
        _precision=len(row[3])-row[3].find(".")
        # if row[3] == "0.000":
        #     pdb.set_trace()
        if _precision ==4:
            prec3_set.add(row[0])
        # if len(row) == 5:
        #     row[-2] = row[-1]
        #     df.append(row[:-1])
        # else:


def genOrderdf(imdf,lis):
    rows=[]
    for order in lis:
        trade_sum=imdf.trade[order[0]:order[1]+1].sum()
        start_time=imdf.time[order[0]]
        end_time=imdf.time[order[0]]
        trade_sum_price=(imdf[order[0]:order[1]+1].trade*imdf[order[0]:order[1]+1].price).sum()
        rows.append((trade_sum,trade_sum_price,start_time,end_time,order[0],order[1]))
    df = pd.DataFrame(rows,columns=["trade_sum","trade_sum_price","start_time","end_time","start_id","end_id"])
    return df

def parseOneId(scr, id, _lastprice, precision, tgt):
    path = os.path.join(scr,id)
    filenum=len(os.listdir(path))
    tgtpath=os.path.join(tgt,id)
    setlastprice(_lastprice)
    for i in range(filenum)[::-1]:
        if os.path.isfile(os.path.join(path, str(i + 1) + ".jpg")):
            print( f"img2pd {id} {str(i + 1)}.jpg ")

            arr = cv2.imread(os.path.join(path, str(i + 1) + ".jpg"),)

            img2pd(arr, f"{tgtpath}.csv",precision,'a')
        else:
            print("{id}{str(i + 1)}.jpg not exists")

def screenOneDay(scr,ids):


    now_time = datetime.datetime.now()
    path = scr + str(now_time.date())
    if not os.path.isdir(path):
        os.mkdir(path)
    import mss
    import uiautomation as auto
    tdx = auto.WindowControl(searchDepth=1, ClassName='TdxW_MainFrame_Class')
    mon = {'top': 88, 'left': 1, 'width': 1336, 'height': 612}
    sct = mss.mss()
    for (id,_,_) in ids:
        i = 1
        idpath = os.path.join(path, id)
        if not os.path.isdir(idpath):
            os.mkdir(idpath)

        not_first = True
        last_arr = None
        tdx.SendKeys(id + "{enter}", 0.2, 0)
        time.sleep(0.1)
        tdx.SendKeys('.504{enter}', 0.2, 0)
        time.sleep(0.5)
        while not_first:

            im = np.asarray(sct.grab(mon))
            img = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            if not (last_arr == img[:300, :600]).all():
                cv2.imwrite(os.path.join(idpath, f"{i}.jpg"), im)
                print(f"cv2.imwrite {i}.jpg")
                tdx.SendKeys('{PageUp}', 0.2, 0)
                last_arr = img[:300, :600]
                i += 1
            else:
                for t in range(10):
                    print(f"try screenshot times {t}")
                    im = np.asarray(sct.grab(mon))
                    img = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
                    tdx.SendKeys('{PageUp}', 0.2, 0)
                    if not (last_arr == img[:300, :600]).all():
                        break
                if (last_arr == img[:300, :600]).all():
                    not_first = False
            time.sleep(0.2)
def parseOneDay(scr,tgt):
    # path = r"Z:\trade\screen_shot\2021-06-07\301002\1.jpg"
    #
    # arr = cv2.imread(path)
    # l2.init(path, 54, 138, 206, 269, 329, 335)
    # for id in idl[:2]:
    #     l2.parseOneId(r"Z:\trade\screen_shot\2021-06-07", id, "000", 2, r"Z:\trade\screen_shot_csv\2021-06-07")
    now_time = datetime.datetime.now()
    path = tgt + str(now_time.date())
    if not os.path.isdir(path):
        os.mkdir(path)
    ids = os.listdir(scr)
    for id in ids:
        parseOneId(scr, id, path)

def getids(filename):
    # import tushare as ts
    # df = ts.get_today_all()
    # ids = df[df.changepercent > 5].sort_values('changepercent', ascending=False).code
    fo = open(filename)
    text_lines = fo.readlines()
    ids=set()
    for line in text_lines[1:-1]:
        row = line.split("\t")
        id=row[0]
        name=row[1]

        if row[2]=='--  ':
            continue
        change=float(row[2])
        closep=row[3]
        openp=row[4]
        if change > 4 or change < -4:
            ids.add( (id,openp,len(row[3])-row[3].find(".")-1))
    return ids