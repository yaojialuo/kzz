import cv2
import numpy as np
import matplotlib.pyplot as plt
import pickle
import logging
import pdb
import pandas as pd
import os
row_num=57
col_num=6
tb_num=342
lasttime = 92500
lastprice =2648

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

(digit_arr, digt_marsk_arr, empty_arr,char_s_arr,char_b_arr) = pickle.load(data_input)
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

def init(path,_lastprice,_first_time_col_bound,_first_price_col_bound,_first_deal_col_bound,_first_buy_col_bound,_first_sell_col_bound,_col_sep):
    # pdb.set_trace()
    global col_sep
    col_sep = _col_sep
    global lastprice
    lastprice = _lastprice
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


def save_pickle():
    data_output = open('ocr_conf.pkl', 'wb')
    pickle.dump((digit_arr, digt_marsk_arr, empty_arr,char_s_arr,char_b_arr), data_output)
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
        return "0",False
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
def ocrPriceArr(price_arr,len=5,precision):
    digit_arr=[]
    y=price_arr.shape[1]
    #left of dot
    for i in range(precision):
        digit_arr.append(price_arr[:, y - digit_width:y])
        y = y - digit_width - digit_sep
    y=y-dot_width-digit_sep
    #right of dot
    for i in range(len-precision):
        digit_arr.append(price_arr[:, y - digit_width:y])
        y = y - digit_width - digit_sep
    return digit_arr
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
def ocrPriceCol(colprice,last_price_str):
    x = x_axis_start
    printlist = []
    last_len=len(last_price_str)
    for i in range(round(colprice.shape[0] / (digit_hight + row_sep)) - 1):
        price_arrs = ocrPriceArr(colprice[x:x + digit_hight, :],last_len+1,2)#read additional empty dight
        if (price_arrs[last_len] != empty_arr).all():
            last_len+=1  #price increase to more digits
        elif (price_arrs[last_len-2] == empty_arr).all():
            last_len -= 1  #price decrease to less digits

        outstr = ""
        for i in range(last_len):
            if last_len == len(last_price_str):
                ret, ret_val = arr2int(price_arrs[i], int(last_price_str[last_len-i-1]))
            else:
                ret, ret_val = arr2int(price_arrs[i])
            if not ret:
                print(ret_val)
                return ret_val, last_price_str
            outstr += str(ret_val)

        # print(i, outstr)
        printlist.append(outstr[::-1])
        last_price_str = outstr
        x = x + digit_hight + row_sep
    for p in printlist:
        print(p)
    return ret_val, last_price_str

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
def parselevel2price(arr):
    global lastprice
    arrg = cv2.cvtColor(arr, cv2.COLOR_BGR2GRAY)
    arrg[arrg >= price_pixel_threshold] = 255
    arrg[arrg < price_pixel_threshold] = 0

    for i in range(round(arrg.shape[1]/col_sep)):
        ret_val, lastprice = ocrPriceCol(arrg[:, :first_price_col_bound + i * col_sep], str(lastprice))
        while not isinstance(ret_val, int):

            cid, errnum = findMatch(ret_val)
            if errnum > 10:
                print("not findMatch  cid {}, errnum {},ret_val {} !".format(cid, errnum,ret_val))
            if updateMarsk(cid, ret_val) > 10:
                break
            ret_val, lastprice = ocrPriceCol(arrg[:, :first_price_col_bound + i * col_sep], lastprice)

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


def updateVollist(arr, deal_col_bound, buy_col_bound, sell_col_bound,tb_index,arrg_2):
    # check b or s
    # pdb.set_trace()
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
    deal_col_bound = deal_col_bound - digit_width - digit_sep
    ref, get_dot = ocrdigit(arr, deal_col_bound)
    tradelist[tb_index] = float(ref[::-1])
    if get_dot:
        ref = None
    buy, _ = ocrdigit(arr, buy_col_bound, ref)
    sell, _ = ocrdigit(arr, sell_col_bound, ref)

    if buy=="0":
        # pdb.set_trace()
        #check if is order char
        if arrg_2[:, buy_col_bound - digit_width:buy_col_bound].max() -arrg_2[:, buy_col_bound - digit_width:buy_col_bound].min()> 50:
            buylist[tb_index] = -2
        elif buylist[tb_index] is None:
            buylist[tb_index] = 0
    else:
        buylist[tb_index] = float(buy[::-1])

    if sell=="0":
        #check if is order char
        if arrg_2[:, sell_col_bound - digit_width:sell_col_bound].max() -arrg_2[:, sell_col_bound - digit_width:sell_col_bound].min()> 50:
            selllist[tb_index] = -2
        elif selllist[tb_index] is None:
            selllist[tb_index] = 0
    else:
        selllist[tb_index] = float(sell[::-1])

def updatePricelist(price_arrs,last_price_str,tb_index):
    last_len = len(last_price_str)

    if (price_arrs[last_len] != empty_arr).all():
        last_len += 1  # price increase to more digits
    elif (price_arrs[last_len - 2] == empty_arr).all():
        last_len -= 1  # price decrease to less digits


    for i in range(last_len):
        if last_len == len(last_price_str):
            ret, ret_val = arr2int(price_arrs[i], int(last_price_str[last_len - i - 1]))
        else:
            ret, ret_val = arr2int(price_arrs[i])
        if not ret:
            pdb.set_trace()
            print(ret_val)
            return
        pricelist[tb_index]+=10**i*ret_val
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

        if list[tb_index] == 0 or list[tb_index] == -2:
            list[tb_index] = -3
        if tb_index+1<tb_num:
            list[tb_index+1] = -1
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

def img2pd(arr,path,precision,checkoverlap=False):
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

            # print("lastprice:",lastprice)
            colprice = arrg[:, first_time_col_bound + ci * col_sep:first_price_col_bound + ci * col_sep,precision]
            price_arrs = ocrPriceArr(colprice[x:x + digit_hight, :], len(str(lastprice)) + 1)  # read additional empty dight
            lastprice=updatePricelist(price_arrs, str(lastprice), tb_index)


            updateVollist(arrg[x:x + digit_hight, :], deal_col_bound, buy_col_bound, sell_col_bound,tb_index,arrg_2[x:x + digit_hight, :])
            bound_arr=arrg_2[x + digit_hight + trans_bound, buy_col_bound - digit_width:buy_col_bound]
            detecbound(bound_arr,buylist,tb_index)
            bound_arr = arrg_2[x + digit_hight + trans_bound, sell_col_bound - digit_width:sell_col_bound]
            detecbound(bound_arr, selllist, tb_index)
            tb_index+=1
            x = x + digit_hight + row_sep

    pd.DataFrame({'time':timelist[overlap:],'price':pricelist[overlap:],'trade':tradelist[overlap:],'bs':bslist[overlap:],'buy':buylist[overlap:],'sell':selllist[overlap:]}).to_csv(path,header=False,index=False,mode="a")
    lasttime=timelist[-1]

def mergeOrderlist(lis):
    order_begin=-1
    order=[]
    has_price=False
    for i in range(len(lis)):

        if lis[i] > 0:
            continue
        if lis[0] == 0 and  order_begin == -1:
            order_begin =i
            continue
        # begin
        if lis[i]==-1  and  order_begin == -1:
            order_begin = i

        if lis[i] == -2 :
            has_price = True
            if order_begin == -1:
                order_begin=i

        if lis[i]==-3:
            if has_price:
                if order_begin == -1:
                    pdb.set_trace()
                    print("error occur in mergeOrderdf")
                    return

                order.append([order_begin,i])
                has_price = False
                order_begin = -1
            #fake order merge to last order
            else:
                order[-1][-1]=i
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

def parseimdir(src=r"E:\pycharm\kzz\screen_shot\000002",tgt):
    path = r"E:\pycharm\kzz\screen_shot\000002"
    filenum=len(os.listdir(path))
    for i in range(filenum)[::-1]:
        if os.path.isfile(os.path.join(path, str(i + 1) + ".jpg")):
            print(str(i + 1) + ".jpg")
            precision = 2
            arr = cv2.imread(os.path.join(path, str(i + 1) + ".jpg"),)
            if i + 1 == 303:
                arr = img2pd(arr, f"1.csv", True)
            else:
                arr = img2pd(arr, f"1.csv",precision)


        else:
            print(str(i + 1) + ".jpg not exists")