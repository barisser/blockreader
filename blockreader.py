import requests
import json
import encodings
import numpy as np
import matplotlib.pyplot as plt
import encodings
import math
import io
import time
import struct

address_list=['0']
btc_list=[0]
throughput=[0]

totaltx=0
lastblock=0
blocksdb=[]
lastblockdb=0

blocksperfile=100 #for DB


lastblockdbfile=open("lastblockdb.txt")
lastblockdb=json.load(lastblockdbfile)
lastblockdbfile.close()

def block(x):
    a=requests.get("https://blockchain.info/block-height/"+str(x)+"?format=json")

    if(a.status_code==200):
        b=json.loads(str(a.content))

        f=0
        for x in b['blocks']:
            if(x['main_chain']):
                #is main chain block, interpret

                return x

def localblock(x):  #must have correct block file already opened
    a=x%blocksperfile
    return blocksdb[a]
"""
def saveblock(x):
    global blocksdb,lastblockdb,blocksperfile

    

    if(x%blocksperfile==0): #you need to erase the blockdb to write again
        blocksdb=[]
    a=block(x)
    t=a['time']
    print datetime.datetime.fromtimestamp(int(t)).strftime('%Y-%m-%d %H:%M:%S')
    blocksdb.append(a)
       
    whichdb='blocks'+str(int(x/blocksperfile))+'.txt'
    
    with io.open(whichdb,'w',encoding='utf-8') as f:  #dump whatever you have in blocksdb
        f.write(unicode(json.dumps(blocksdb,ensure_ascii=False)))
        f.close()
    lastblockdb=x
    
    with io.open('lastblockdb.txt','w',encoding='utf-8') as f:
        f.write(unicode(json.dumps(lastblockdb,ensure_ascii=False)))

    if(len(a)==0):
        return False
    elif(len(a)>0):
        return True

"""
def saveblock(x):

    whichdb='blocks'+str(int(x/blocksperfile))+'.txt' 
    
    if(x==0):
        f=open(whichdb,'w') 
    else:
        f=open(whichdb,'a+')  #opens for appending and reading only
    
    b=block(x)  #already returned as JSON object
    b2=json.dumps(b)  #non-json
    print str(x) + "    "+str(len(b2))
    #use 8 byte leader string to say length of subsequent block in file
    #must always be 8 bytes
    leadermax=8
    leader=len(b2)
    leaderstring=str(leader)
    p=leadermax-len(leaderstring)
    a=0
    while a<p:
        leaderstring='0'+leaderstring
        a=a+1

    f.write(leaderstring)
    f.write(b2)
    #print len(leaderstring) #to make sure its always 8

    f.close()
    

              
        

def loadblocks():
    global blocksdb,lastblockdb
    blocksdb=[]
    lastblockdbfile=open("lastblockdb.txt")
    lastblockdb=json.load(lastblockdbfile)
    lastblockdbfile.close()

    #find number of db files to look for
    dbmax=int(lastblockdb/blocksperfile)
    if(lastblockdb%blocksperfile>0):
        dbmax=dbmax+1 #round up

    print "Files to cover: "+str(dbmax)
    a=0
    while(a<dbmax):
        blockfilen=open("blocks"+str(a)+".txt")
        adding=json.load(blockfilen)
        print a
        for x in adding:
            blocksdb.append(x)
        
        a=a+1
        blockfilen.close()


    print "Last Block in DB: "+str(lastblockdb)

def loadblockfile(x):
    global blocksdb, lastblockdb, blockfile
    blocksdb=[]
    if(x*blocksperfile>lastblockdb):
        return -1
    else:
        blockfile=open("blocks"+str(x)+".txt")

        #open blocks sequentially
        go=True
        while go:
            leader=blockfile.read(8)  #not referenced to 8 seen elsewhere
            if(leader==''): #at end of file
                go=False
            else:
                leader=int(leader)
                blk=blockfile.read(leader)
                blk=json.loads(blk)
                blocksdb.append(blk)
        

        #stuff=json.load(blockfile)
        #for x in stuff:
        #    blocksdb.append(x)
    return blockfile

def closeblockfile(x):
    x.close()
        

def saveblocks(startx,endx):
    x=startx
    global lastblockdb
    while(x<endx+1):
        #print x
        r=saveblock(x)
        
        if(r==False):
            x=endx+1
        
        x=x+1



    
def throughput(blockn):
    a=localblock(blockn)
    global addresses, through
    addresses=[0]
    through=[0]

    for x in a['tx']:

        inputters=x['inputs']
        outputters=x['out']

        for i in outputters:
            iaddr=i['addr']
            iamt=i['value']/100000000

            r=findinlist(iaddr,addresses)
            if(r>0):
                through[r]=through[r]+iamt
            else:
                placeinlist(iaddr,-1*r,addresses)
                placeinlist(iamt,-1*r,through)
        
    


def transactions_in_block(x, local):
    global totaltx
    blockn=x
    if(local):
        g=len(blocksdb)
        d=localblock(x)
    else:
        d=block(x)
    #print x
    hhh=d['time']
    global sumbtc
    jj=0
    for x in d['tx']:
        totaltx=totaltx+1
        ins=x['inputs']
        
        t=0
        g=x['out']
        sumbtc=0
        for f in g:
            if(f['type']>-1):
                giveraddress=str(f['addr'])
                giveramt=float(f['value'])/100000000
                giverplace=findinlist(giveraddress,address_list)
                if(giveramt<50):
                    jj=1
                    
                if(giverplace<0):  #add new entry
                    giverplace=giverplace*-1
                    placeinlist(giveraddress,giverplace,address_list)
                    placeinlist(giveramt,giverplace,btc_list)
                    #print str(giverplace)+ "  "+giveraddress+"  "+str(giveramt)
                else:
                    newamt=btc_list[giverplace]+giveramt
                    btc_list[giverplace]=newamt
                    #placeinlist(newamt,giverplace,btc_list)
            
       
        for y in ins:
            if(len(y)>0):
                if blockn<129878:
                    receiveraddress=str(y['prev_out']['addr'])
                    receiveramt=float(y['prev_out']['value'])/100000000
                    receiverplace=findinlist(receiveraddress,address_list)
                else:
                    receiveraddress=str(y['addr'])
                    receiveramt=float(y['value']/100000000)
                    receiverplace=findinlist(receiveraddress,address_list)
            
                if(receiverplace<0):
                   receiverplace=receiverplace*-1
                   placeinlist(receiveraddress,receiverplace,address_list)
                   placeinlist(-1*receiveramt,receiverplace,btc_list)
                else:
                    newamt=btc_list[receiverplace]-receiveramt
                    btc_list[receiverplace]=newamt
                #placeinlist(newamt,receiverplace,btc_list)
                #print "taking   "+str(receiverplace)+"  "+receiveraddress+"   "+str(address_list[receiverplace])+"  "+str(receiveramt)
                #print str(y['prev_out']['addr'])+"   "+str(y['prev_out']['value'])

    clear(1000)

    return hhh
            
def placeinlist(x,n,list):      # 0th position is still a position
    b=len(list)
    if(b>0):
        list.append(list[b-1])

        a=b-1
        while(a>=n):
            list[a+1]=list[a]
            
            a=a-1

        a=a+1
        list[a]=x
    elif(b==0):
        list.append(x)


def removefromlist(n,list):
    a=0
    list2=[]
    b=len(list)
    while(a<n):
        list2.append(list[a])
        a=a+1
    while(a<b-1):
        list2.append(list[a+1])
        a=a+1

    return list2

def findinlist(x,list):
    b=len(list)
    a=-1
    if(b>0):
        lowerbound=0
        upperbound=b
        a=(lowerbound+upperbound)/2
        p=b
        h=int(str(x).encode("hex"),32)
        depth=0
        g=0
        cont=True
        while(cont):
            g=g+1
            a=(lowerbound+upperbound)/2
            hexa=int(str(list[a]).encode("hex"),32)
            
            if(h==hexa):
                cont=False
            elif(upperbound-lowerbound<2 and h>hexa):
                cont=False
                a=-upperbound
            elif(upperbound-lowerbound<2 and h<hexa):
                cont=False
                a=-lowerbound
            
            elif(h<hexa):
                
                upperbound=a
                                
            elif(h>hexa):
                
                lowerbound=a
            elif(g>math.log(b,2)*3):
                cont=False
                a=-1
            
                
              

                
    return a


c=[]
x=0
while (x<20):
    x=x+1
    c.append(x*x)
    
d=[0]*371

a=0
while a<371:

    for x in c:
        if(x==a):
            d[a]=d[a]+1
    
    a=a+1
    
import datetime
    
def blocks(startblock,endblock, local):   #now opens and closes blockdbfiles dynamically
    s=time.time()
    a=startblock
    global lastblock, blocksdb
    blocksdb=[]
    j=startblock/blocksperfile
    first=loadblockfile(j)
    startingnew=True
    while a<endblock+1:

        #if not check():
        #    a=endblock+1

        if(a%blocksperfile==0 and not startingnew):
            closeblockfile(first)
            print "should start"
            j=a/blocksperfile
            first=loadblockfile(j)
            
        k=transactions_in_block(a,local)
        #clear(100)
        startingnew=False
        #print len(blocksdb)
        
        t=(datetime.datetime.fromtimestamp(int(k)).strftime('%Y-%m-%d %H:%M:%S'))
        print "Block: "+str(a)+"     "+str(t)
        lastblock=a
        a=a+1
    lastblock=endblock+1
    blocksdb=[]
    print time.time()-s

def wallets():
    x=1
    b=len(address_list)
    while x<b:
        print address_list[x]+"   "+str(btc_list[x])
        x=x+1


def save():
    #btcfile=open("btc.txt","wb")
    #addressfile=open("addresses.txt","wb")

    with io.open('btc.txt','w',encoding='utf-8') as f:
        f.write(unicode(json.dumps(btc_list,ensure_ascii=False)))
    with io.open('addresses.txt','w',encoding='utf-8') as f:
        f.write(unicode(json.dumps(address_list,ensure_ascii=False)))
    with io.open('lastblock.txt','w',encoding='utf-8') as f:
        f.write(unicode(json.dumps(lastblock,ensure_ascii=False)))


def load():
    global address_list,btc_list,lastblock
    
    btcfile=open("btc.txt")
    addressfile=open("addresses.txt")
    blockfile=open("lastblock.txt")
    
    btc_list=json.load(btcfile)
    address_list=json.load(addressfile)
    lastblock=json.load(blockfile)
    
    blockfile.close()
    btcfile.close()
    addressfile.close()

    print "Last Block: "+str(lastblock)
    print "Number of Addresses: "+str(len(address_list)-1)
    
def check():
    s=0
    a=0
    ok=True
    while a<len(btc_list):
        s=s+btc_list[a]
        if(btc_list[a]<-1*0.0000001):
            ok=False
            
            print "member "+str(address_list[a])+" has "+str(btc_list[a])
            a=len(btc_list)
        a=a+1
    if(not s/lastblock==50):
        #ok=False
        print str(s/lastblock)
    return ok

def clear(n):
    a=0
    b=0
    
    global btc_list,address_list
    while(a<len(btc_list) and b<n):
        if(btc_list[a]==0):
            del btc_list[a]
            del address_list[a]
            b=b+1
            #print str(a)+"    number cleared: "+str(b)
            
            #btc_list=removefromlist(a,btc_list)
            #address_list=removefromlist(a,address_list)
        a=a+1

    print str(b)
    return 0


#color coin reading

#issuer public address list
issuers=[]

#issuer signal address
signals=[]

colorbtc=[]
coloraddress=[]
"""
def color_tx_in_block(x, local):
    
    if(local):
        g=len(blocksdb)
        if(x<g):
            d=localblock(x)
    else:
        d=block(x)
        
    hhh=d['time']
    
    for x in d['tx']:
        
        ins=x['inputs']
        
        t=0
        g=x['out']
        sumbtc=0

        for y in ins:
            if(len(y)>0):
                senderaddress=str(y['prev_out']['addr'])
                senderamt=float(y['prev_out']['value'])/100000000
                senderplace=findinlist(senderaddress,coloraddress)

                if(senderplace>-1):
                    senderamount=coloraddress[senderplace]
                else:
                    senderamount=0

                if(senderamount>0):
                    
                          
                if(receiverplace<0):
                   receiverplace=receiverplace*-1
                   placeinlist(receiveraddress,receiverplace,address_list)
                   placeinlist(-1*receiveramt,receiverplace,btc_list)
                else:
                    newamt=btc_list[receiverplace]-receiveramt
                    btc_list[receiverplace]=newamt
                #placeinlist(newamt,receiverplace,btc_list)
                #print "taking   "+str(receiverplace)+"  "+receiveraddress+"   "+str(address_list[receiverplace])+"  "+str(receiveramt)
                #print str(y['prev_out']['addr'])+"   "+str(y['prev_out']['value'])

        
        for f in g:
            if(f['type']>-1):
                giveraddress=str(f['addr'])
                giveramt=float(f['value'])/100000000
                giverplace=findinlist(giveraddress,address_list)
                if(giveramt<50):
                    jj=1
                    
                if(giverplace<0):  #add new entry
                    giverplace=giverplace*-1
                    placeinlist(giveraddress,giverplace,address_list)
                    placeinlist(giveramt,giverplace,btc_list)
                    #print str(giverplace)+ "  "+giveraddress+"  "+str(giveramt)
                else:
                    newamt=btc_list[giverplace]+giveramt
                    btc_list[giverplace]=newamt
                    #placeinlist(newamt,giverplace,btc_list)
            
       
        
    return hhh
"""




def loadblockinfile(file):  #you need to be in the correct place in the file already
    global headerlength,versionnumber,previousblockhash, merkleroot, timestamp, bits, nonce
    if(not file.read(4)=='\xf9\xbe\xb4\xd9'):
        return -1
    else:
        headerlength=file.read(4)
        versionnumber=file.read(4)
        previousblockhash=file.read(32)
        merkleroot=file.read(32)
        timestamp=file.read(4)
        bits=file.read(4)
        nonce=file.read(4)

        

        print "header length: "+ str(convert_to_int(headerlength))
        #print "previous block hash: "+str(convert_to_int(previousblockhash))
        print "timestamp: "+str(convert_to_int(timestamp))
        print "nonce: "+str(convert_to_int(nonce))
    

def convert_to_int(x):
    g=len(x)
    f=struct.unpack("<"+str(g/4)+"i",x)
    return f[0]



"""
throughput=[]
addresses=[]  #for throughput
inaddress=[]
outaddress=[]  #out per address, indexed with addresses
"""
class address_tx:
    addr=''
    throughput=0
    inputs=0
    outputs=0
    def __init__(self):
        self.addr=''
        self.throughput=0
        self.inputs=0
        self.outputs=0
 


class tx:
    inblock=-2
    inputs=[]
    outputs=[]
    inamts=[]
    outamts=[]
    def __init__(self):
        self.inputs=[]
        self.outputs=[]
        self.inamts=[]
        self.outamts=[]
        self.inblock=-1


addresses=[]
transactions=[]

def findaddress(addr):
    a=0
    r=-1
    while a<len(addresses):
        if(addresses[a].addr==addr):
            r=a
            a=len(addresses)
            
        
        a=a+1

    return r


def tx_in_block(blockn):

    #b=loadblockfile(blockn%blocksperfile)
    #a=localblock(blockn)
    a=block(blockn)
   # closeblockfile(b)
    b=a['tx']
    global addresses, transactions 
    for x in b:
        #print x
        c=x['inputs']
        d=x['out']
        tempins=[]

        t=tx()
        t.inblock=blockn
        
        for inputters in c: #inputters first

            if(len(inputters)>0):
                
                amt=float(inputters['prev_out']['value'])/100000000
                addr=inputters['prev_out']['addr']
                tempins.append(addr)

                t.inputs.append(addr)
                t.inamts.append(amt)

                pi=findaddress(addr)

                if(pi==-1):
                    ar=address_tx()
                    ar.addr=addr
                    ar.throughput=amt
                    ar.inputs=amt
                    ar.outputs=0
                    addresses.append(ar)
                else:
                    addresses[pi].throughput=addresses[pi].throughput+amt
                    addresses[pi].inputs=addresses[pi].inputs+amt


        for outputters in d:

            if(len(outputters)>0):
                
                amt=float(outputters['value'])/100000000
                addr=outputters['addr']

                ok=True
                for x in tempins:
                    if(x==addr):
                        ok=False

                if ok:
                    
                    t.outputs.append(addr)
                    t.outamts.append(amt)

                    po=findaddress(addr)

                    if(po==-1):
                        ar=address_tx()
                        ar.addr=addr
                        ar.throughput=amt
                        ar.inputs=0
                        ar.outputs=amt
                        addresses.append(ar)
                    else:
                        addresses[po].throughput=addresses[po].throughput+amt
                        addresses[po].outputs=addresses[po].outputs+amt
                    
        transactions.append(t)


def sortlists(): #dumb way
    global addresses
    templist=[]
    boolist=[True]*len(addresses)
    a=0
    for x in addresses:
        a=a+1
           #lets do this the dumb way for now, N^2

        best=-1
        bestplace=0
        y=0

        while y<len(addresses):

            if(boolist[y]==True and not y==x):
                score=addresses[y].throughput   #int(str(thelist[y]).encode("hex"),32)

                if(score>best):
                    best=score
                    bestplace=y

                y=y+1
            else:
                y=y+1

        templist.append(addresses[bestplace])
        boolist[bestplace]=False
    addresses=templist

    

def draw_addresses():
    #addresses should be found and sorted by now
    
    maxn=1000

    n=len(addresses)
    if(n>maxn):
        n=maxn
    global x,y
    x=np.zeros(n)
    y=np.zeros(n)
    areas=np.zeros(n)

    a=0

    radius=10
    polar=0
    radiusincrement=.5
    polarincrement=15
    
    for addre in addresses:

        radius=radius+1
        polar=polar+polarincrement#/math.log(radius,2)

        if(a<n):

            x[a]=math.cos(polar*math.pi/180)*radius
            y[a]=math.sin(polar*math.pi/180)*radius

            areas[a]=addre.throughput
    
        a=a+1
        
    global fromcoordinates, tocoordinates
    fromcoordinates=np.zeros([len(transactions),2])
    tocoordinates=np.zeros([len(transactions),2])
    
    d=0
    for tx in transactions:
        if tx.inamts>0:
            if len(tx.inputs)>0:
                fromplace=findaddress(tx.inputs[0])
                toplace=findaddress(tx.outputs[0])

                fromcoordinates[d][0]=x[fromplace]
                fromcoordinates[d][1]=y[fromplace]
                tocoordinates[d][0]=x[toplace]
                tocoordinates[d][1]=y[toplace]
                d=d+1

        
        

    #normalize areas
    t=0
    for f in areas:
       t=t+f

    desired_average_area=100
    factor=desired_average_area/(t/n)

    q=0
    while q<n:
        #areas[q]=areas[q]/factor
        q=q+1

    plt.scatter(x,y,s=areas)

    j=0
    while j<len(fromcoordinates):
        fx=fromcoordinates[j][0]
        fy=fromcoordinates[j][1]
        ttx=tocoordinates[j][0]
        tty=tocoordinates[j][1]
        plt.plot([fx,fy],[ttx,tty],lw=1)
        j=j+1


    #LINES
   
   


    plt.show()
    

        
#tx_in_block(100000)
#sortlists()
#draw_addresses()
