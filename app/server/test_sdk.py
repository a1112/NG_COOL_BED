from multiprocessing import Process

from SDK.Devclass import cap_one

if  __name__== "__main__":
    Process(target=cap_one,args=(b'30.30.30.4',)).start()
