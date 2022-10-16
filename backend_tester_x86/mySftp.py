# -*- coding:utf-8 -*-
# copied from https://www.yisu.com/zixun/450939.html
import paramiko
import os

_XFER_FILE = 'FILE'
_XFER_DIR  = 'DIR'

class MainWindow(object):
    # 构造方法
    def __init__(self, arg):
        # 超类调用
        super(MainWindow, self).__init__()

        # 赋值参数[字典]
        # 参数格式 arg = {'ip':'填ip','user':'用户名','password':'密码','port':22}
        self.arg = arg
        # 赋值参数[FTP]
        self.sftp = None

        # 调试日志
        print (self.arg)


    # 启动程序
    def startup(self):
        # 连接FTP
        if self.sftp != None:
            print (u'您已经成功连接了')
        tmpstr = u'开始连接...用户名:'+self.arg['user']+u'  密码:'+self.arg['password']+' IP:'+self.arg['ip']+u' 端口:'+str(self.arg['port'])
        print (tmpstr)
        try:
            transport = paramiko.Transport((self.arg['ip'], self.arg['port']))
            transport.connect(username=self.arg['user'], password=self.arg['password'])
            self.sftp = paramiko.SFTPClient.from_transport(transport)
            print (u'连接成功 '+self.arg['ip'])
        except Exception as e:
            print (u'连接失败：'+str(e))

    # 关闭程序
    def shutdown(self):
        # 关闭FTP
        if self.sftp:
            self.sftp.close() 
            print ('### disconnect sftp server: %s!'%self.arg['ip'])
            self.sftp = None 

    # 处理上传
    def upload(self, source, target, replace):
        ### 操作数据
        # 来源路径
        source = source.replace('\\', '/')
        # 目标路径
        target = target.replace('\\', '/')


        ### 验证数据
        if not os.path.exists(source):
            print (u'来源资源不存在，请检查：' + source)
            return 'ERROR'


        ### 格式数据
        # 格式化目标路径
        self.__makePath(target)


        ### 处理数据
        # 文件媒体数据(文件类型, 文件名称)
        filetype, filename = self.__filetype(source)
        # 判断文件类型
        if filetype == _XFER_DIR:
            # 1.目录 
            self.uploadDir(source, target, replace)
        elif filetype == _XFER_FILE:
            # 2.文件 
            self.uploadFile(source, filename, replace)
        return 'OK'


    # 传送目录
    def uploadDir(self, source, target, replace):
        ### 验证数据
        # 判断目录存在
        if not os.path.isdir(source):   
            print (u'这个函数是用来传送本地目录的')
            return

        ### 处理数据
        # 遍历目录内容，上传资源
        for file in os.listdir(source):
            # 资源路径
            filepath = os.path.join(source, file) 

            # 判断资源文件类型
            if os.path.isfile(filepath): 
                # 1.文件
                self.uploadFile(filepath, file, replace) 
            elif os.path.isdir(filepath):
                # 2.目录
                try:
                    self.sftp.chdir(file) 
                except:
                    self.sftp.mkdir(file)
                    self.sftp.chdir(file) 
                self.uploadDir(filepath, file, replace)

        ### 重置数据
        # 返回上一层目录
        self.sftp.chdir('..') 

    # 传送文件
    def uploadFile(self, filepath, filename, replace):
        ### 验证数据
        # 验证文件类型
        if not os.path.isfile(filepath):
            print (u'这个函数是用来传送单个文件的')
            return
        # 验证文件存在
        if not os.path.exists(filepath):
            print (u'err:本地文件不存在，检查一下'+filepath)
            return
        # 验证FTP已连接
        if self.sftp == None:
            print (u'sftp 还未链接')
            return


        ### 处理数据
        # 判断文件存在是否覆盖
        if not replace:
            if filename in self.sftp.listdir():
                print (u'[*] 这个文件已经存在了，选择跳过:' + filepath + ' -> ' + self.sftp.getcwd() + '/' + filename)
                return
        # 上传文件
        try:
            self.sftp.put(filepath, filename)
            print (u'[+] 上传成功:' + filepath + ' -> ' + self.sftp.getcwd() + '/' + filename)
        except Exception as e:
            print (u'[+] 上传失败:' + filepath + ' because ' + str(e))

    # 获得文件媒体数据({文件/目录, 文件名称})
    def __filetype(self, source):
        # 判断文件类型
        if os.path.isfile(source):
            # 1.文件
            index = source.rfind('/')
            return _XFER_FILE, source[index+1:]
        elif os.path.isdir(source):  
            # 2.目录
            return _XFER_DIR, ''


    # 创建目标路径
    # 说明: 目标路径不存在则依次创建路径目录
    def __makePath(self, target):
        # 切换根目录
        self.sftp.chdir('/')

        # 分割目标目录为目录单元集合
        data = target.split('/')
        # 进入目标目录, 目录不存在则创建
        for item in data:
            try:
                self.sftp.chdir(item) 
            except:
                self.sftp.mkdir(item)
                self.sftp.chdir(item) 
                print (u'要上传的目录不存在，创建目录：' + item)