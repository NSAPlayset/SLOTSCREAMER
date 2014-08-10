import usb.core
import usb.util
import sys
import struct
import math

pciin = None
pciout = None
cache=[]
cachebase=0

def readPCI(address,byteCount):
    global cache
    global cacheBase
    offset=address%256
    baseAddress=address-offset
    endOffset=(address+byteCount)%256
    endAddress=address+byteCount-endOffset+256
    if (len(cache)>0):
        print('cache exists')
        if ((cacheBase<=address) and ((cacheBase+len(cache))>=(address+byteCount))):
            print('cache hit')
            return bytes(cache[(address-cacheBase):(address+byteCount)-cacheBase])
    print('read not cached')
    cache=[]
    cacheBase=baseAddress
    print('cacheBase',cacheBase,'baseaddress',baseAddress,'endaddress',endAddress)
    while baseAddress<endAddress:
        print('BBBBI',0xcf,0,0,0x40,baseAddress)
        print("addr",baseAddress)
        pciout.write(struct.pack('BBBBI',0xcf,0,0,0x40,baseAddress))
        cache+=pciin.read(0x100)
        baseAddress+=256
    return bytes(cache[offset:offset+byteCount])


def initPCI():
    global pciin
    global pciout
    global cache
    cache=[]        
    # find our device
    dev = usb.core.find(idVendor=0x0525, idProduct=0x3380)
    if dev is None:
        raise ValueError('Device not found')
    dev.set_configuration()
    cfg = dev.get_active_configuration()
    intf=cfg[0,0]
    pciin = usb.util.find_descriptor(intf,custom_match = lambda e: e.bEndpointAddress==0x8e)
    assert pciin is not None
    sys.stdout.write('PCIIN found: '+str(pciin)+'\n')
    pciout = usb.util.find_descriptor(intf,custom_match = lambda e: e.bEndpointAddress==0xe)
    assert pciout is not None
    sys.stdout.write('PCIOUT found: '+str(pciout)+'\n')


def readmem(addr):
    pciout.write(struct.pack('BBBBI',0xcf,0,0,0x1,addr))
    return pciin.read(0x100)


def readIO(addr):
    pciout.write(struct.pack('BBBBI',0xdf,0,0,0x1,addr))
    return pciin.read(0x100)


def writeIO():
    pciout.write(struct.pack('BBBBI',0x5f,0,0,0x10,baseAddress))


def readCfg(addr):
    pciout.write(struct.pack('BBBBI',0xef,0,0,0x1,addr))
    return pciin.read(0x100)


def writeCfg():
    pciout.write(struct.pack('BBBBI',0x6f,0,0,0x10,baseAddress))


def readvPCI(req):
    for r in req:
        yield(r[0],readPCI(r[0],r[1]))


def writePCI(address, buf):
    #calculate buffer
    offset=address%256
    baseAddress=address-offset
    byteCount=len(buf)
    endOffset=(address+byteCount)%256
    endAddress=address+byteCount-endOffset+256
	 #read to fill buffer
    print('read buffer')
    readbuf=bytearray(readPCI(baseAddress,endAddress-baseAddress))
    #modify buffer
    print('modify buffer')
    for i in range(offset,endOffset):
        readbuf[i]=buf[i-offset]
    #write buffer
    print('write buffer')
    bufferIndex=0
    while baseAddress<endAddress:
        subbuf=readbuf[bufferIndex:bufferIndex+128]
        print("addr",baseAddress,'subbuf',len(subbuf))
        pciout.write(struct.pack('BBBBI'+'B'*128,0x4f,0,0,0x20,baseAddress,*subbuf))
        baseAddress+=128
        bufferIndex+=128
    global cache
    cache=[]        



#initPCI()
#readPCI(0x1000000,100)
#writePCI(0x1000010,[0xff,0xff,0xff,0xff])
#readPCI(0x1000000,100)



#readPCI(0,0x82)

#for x in range (0,100):
#    val=readPCI(x*100000,100000)

# write the data
#pciout.write(b'\xcf\x00\x00\x01\x00\x00\x00\x00')
#str=pciin.read(10000)
#sys.stdout.write('Read: '+str+'\n')


#def 
