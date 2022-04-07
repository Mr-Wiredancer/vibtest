import time
import os
import serial 

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import logging

# 正常情况日志级别使用INFO，需要定位时可以修改为DEBUG，此时SDK会打印和服务端的通信信息
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

# 1. 设置用户属性, 包括 secret_id, secret_key, region等。Appid 已在CosConfig中移除，请在参数 Bucket 中带上 Appid。Bucket 由 BucketName-Appid 组成
secret_id = 'AKIDymMyLekEBE1b3GnF0Z3IINF2TgeXGbom'     # 替换为用户的 SecretId，请登录访问管理控制台进行查看和管理，https://console.cloud.tencent.com/cam/capi
secret_key = 'sfDWihR2MRQ9d36uugDbkgYGjyxgZEfx'   # 替换为用户的 SecretKey，请登录访问管理控制台进行查看和管理，https://console.cloud.tencent.com/cam/capi
region = None              # 通过Endpoint初始化不需要配置region
token = None               # 如果使用永久密钥不需要填入token，如果使用临时密钥需要填入，临时密钥生成和使用指引参见https://cloud.tencent.com/document/product/436/14048
scheme = 'http'           # 指定使用 http/https 协议来访问 COS，默认为 https，可不填

endpoint = 'cos.ap-guangzhou.myqcloud.com' # 替换为用户的 endpoint 或者 cos全局加速域名，如果使用桶的全球加速域名，需要先开启桶的全球加速功能，请参见https://cloud.tencent.com/document/product/436/38864
config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Endpoint=endpoint, Scheme=scheme)
client = CosS3Client(config)

ser = serial.Serial(
        port='/dev/ttyAMA0',
        baudrate = 115200,
        parity = serial.PARITY_NONE,
        stopbits = serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        )

def combine(low:int, high:int):
    combined = ( high << 8 ) | low
    return int.from_bytes(combined.to_bytes(2, byteorder='big'), byteorder='big', signed=True) 

def decode_acc( data ):
    acc = []
    if data[0] == 81:
        accs = []
        for i in range(3):
            low, high = data[i*2+1], data[i*2+2]
            accs.append(combine(low, high)/32768*16) 
        
        return accs    
        
    elif data[0] == 82:
        accs = []
        for i in range(3):
            low, high = data[i*2+1], data[i*2+2]
            accs.append(combine(low, high)/32768*2000) 
        
        return accs    

    elif data[0] == 83:
        accs = []
        for i in range(3):
            low, high = data[i*2+1], data[i*2+2]
            accs.append(combine(low, high)/32768*180) 
        return accs    

    else:
        return None

def upload_file(fname):
    try:
        with open(fname, 'rb') as fp:
            response = client.put_object(
                Bucket='tianjitest-1252729957',
                Body=fp,
                Key=fname,
                StorageClass='STANDARD',
                EnableMD5=False
            )
        print('upload succeeded')
        os.remove(fname)
    except Exception as e:
        print('upload failed', e)
        time.sleep(1)
        upload_file(fname)


columns = ['time', 'x_acc', 'y_acc', 'z_acc', 'x_ang_acc', 'y_ang_acc', 'z_ang_acc', 'x_ang', 'y_ang', 'z_ang']

start = int(time.time())
fout = open(f'data/{start}.csv', 'w')
fout.write(" ".join(columns)+"\n")
count = 0
while 1:
    try:
        ser.reset_input_buffer()
        ser.read_until(b'UQ')# 55
        data = b'Q'+ser.read(9)
        acc = decode_acc(data)
        if data[0] != 81: continue
        assert data[0]==81

        ser.read_until(b'U')# 55
        data = ser.read(10)
        ang_acc = decode_acc(data)
        assert data[0]==82

        ser.read_until(b'U')# 55
        data = ser.read(10)
        ang = decode_acc(data)
        assert data[0]==83

        fout.write(" ".join(map(str, [time.time()] + acc + ang_acc + ang))+"\n")
        count += 1

        # uplaod file and reset
        if count == 120*100:
            count = 0
            fout.close()
            upload_file(f'data/{start}.csv')
            start = int(time.time())
            fout = open(f'data/{start}.csv', 'w')
            fout.write(" ".join(columns)+"\n")

    except Exception as e:
        print('error', e)
        time.sleep(1) 
