# 参考：https://www.cnblogs.com/zhaoyingjie/p/12017275.html

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import binascii
import base64

import os

class RSAworker:
    def __init__(self, _path = os.path.dirname(__file__)):
        self.key_path = _path
        # 检查当前路径是否存在公私钥对，不存在则生成，公私钥对不匹配也备份原文件后生成
        pri_key_exist = os.path.exists(os.path.join(_path,"private.pem"))
        pub_key_exist = os.path.exists(os.path.join(_path,"public.pem"))
        if pri_key_exist and pub_key_exist:
            # 公私钥同时存在
            try:
                # 尝试读取公私钥对
                with open(os.path.join(_path,"private.pem"), 'rb') as f:
                    pri_key = RSA.import_key(f.read())
                with open(os.path.join(_path,"public.pem"), 'rb') as f:
                    pub_key = RSA.import_key(f.read())
            except(binascii.Error, ValueError) as e:
                # 读取失败
                # b64长度不正确、padding填充不正确、不是有效的PEM边界（begin end行丢失）等各种原因
                # 备份原公私钥文件并重新生成
                self.backup_old_pri_key_file()
                self.backup_old_pub_key_file()
                self._gen_new()
            else:
                if pub_key != pri_key.public_key():
                    # 公私钥不匹配，备份公钥文件并根据私钥重新生成公钥，并保存
                    self.backup_old_pub_key_file()
                    pub_key = self.gen_pub_by_exist_pri(pri_key)
                    self.pri_key = pri_key
                    self.pub_key = pub_key
                else:
                    # 公私钥文件匹配
                    self.pub_key = pub_key
                    self.pri_key = pri_key
        else:
            # 不是都存在或都不存在
            if pri_key_exist:
                # 只存在私钥，则生成对应公钥并保存
                with open(os.path.join(_path,"private.pem"), 'rb') as f:
                    pri_key = RSA.import_key(f.read())
                pub_key = self.gen_pub_by_exist_pri(pri_key)
                self.pri_key = pri_key
                self.pub_key = pub_key
            if pub_key_exist:
                # 只存在公钥，则备份现有公钥文件，并重新生成密钥对
                self.backup_old_pub_key_file()
                self._gen_new()
            else:
                # 公私钥都不存在
                self._gen_new()
    
    def backup_old_pub_key_file(self):
        '''备份现有公钥文件'''
        with open(os.path.join(self.key_path,"public.pem"), 'rb') as source_file:
            with open(os.path.join(self.key_path,"public.pem.bk"), 'wb') as target_file:
                target_file.write(source_file.read())

    def backup_old_pri_key_file(self):
        '''备份现有私钥文件'''
        with open(os.path.join(self.key_path,"private.pem"), 'rb') as source_file:
            with open(os.path.join(self.key_path,"private.pem.bk"), 'wb') as target_file:
                target_file.write(source_file.read())

    def gen_pub_by_exist_pri(self, pri_key):
        '''根据私钥生成新的公钥，保存到文件，返回公钥'''
        pub_key = pri_key.public_key()
        with open(os.path.join(self.key_path,"public.pem"), 'wb') as f:
            f.write(pub_key.exportKey())
        return pub_key
    
    def _gen_new_pri(self):
        '''重新生成私钥，保存到文件，返回私钥'''
        private_key = RSA.generate(2048)
        with open(os.path.join(self.key_path,"private.pem"), 'wb') as f:
            f.write(private_key.exportKey())
        return private_key
    
    def _gen_new(self):
        '''重新生成公私钥对，保存到文件，读取到self'''
        pri_key = self._gen_new_pri()
        pub_key = self.gen_pub_by_exist_pri(pri_key)
        self.pri_key = pri_key
        self.pub_key = pub_key

    def encrypt(self, plain_text):
        '''加密函数（没用到）'''
        cipher = PKCS1_v1_5.new(self.pub_key)
        cipher_text = cipher.encrypt(plain_text.encode())
        return(base64.b64encode(cipher_text))

    def decrypt(self, cipher_text):
        '''解密函数'''
        msg = base64.b64decode(cipher_text)
        cipher = PKCS1_v1_5.new(self.pri_key)
        plain_text = cipher.decrypt(msg,'DecryptError')
        if not plain_text.decode():
            raise PrivateKeyNotMatchError("解密错误，可能是私钥不匹配")
        return(plain_text.decode())
    
    def get_pub_key(self):
        '''获取PEM格式私钥'''
        return self.pub_key.export_key().decode()

class PrivateKeyNotMatchError(Exception):  
    '''解密失败异常，通常是私钥和公钥不匹配导致的'''
    def __init__(self, message):  
        self.message = message  
        super().__init__(self.message)  

# private_key = RSA.generate(2048)
# public_key = private_key.public_key()
# with open('private.pem', 'wb') as f:
#     f.write(private_key.exportKey())

if __name__ == "__main__":
    rsa = RSAworker()
    print(rsa.decrypt("cSqyyd8q/wicZrtXXL3kaMFsgwZVxI2r9/t3jM7kQLetDM7ED7iWaMHbnTsLk+lGlZB3BP6iYV3mPjZWeagbaIupO5s5txNEiYC5Psblntc28ctz6lxfeVu+08rgWxAzMjSz9HyOImhlbX5fMMiJ8BpX+lZS6UdOTqHNvSnPo5G+wHFXQq4QDwDTDDIr9oBN2tkEmJ+p4g8nGGm5rvw1z03XTFnYYtaPsB+5WRfpqlxoIyr9oAE7gAmEOr5HY1M3I0Nq+olZPso/qwHAvce78YCfO45yg0jHTWHjCxjxvXiUsx00+f6wwWK+WasoxhdtJI3d+KbqSXvSFDUjw3bmsg=="))

# try:
#     with open('private.pem', 'rb') as f:
#         privatekey = RSA.import_key(f.read())
# except (binascii.Error, ValueError) as e:
#     # b64长度不正确、padding填充不正确、不是有效的PEM边界（begin end行丢失）等各种原因
#     # 总之是密钥文件被篡改
#     print(e)
#     pass