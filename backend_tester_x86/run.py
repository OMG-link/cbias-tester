from yaml import load
from backend_tester import BackendAutoTester 
from caseloader import Loader, TestCase

COMPILER = "./cbias.jar"
JAVA = "C:/Program Files/Java/jdk-17.0.1/bin/java"
OUT_DIR = "./out"
sftpArg = {'ip':'192.168.43.195','user':'pi','password':'raspberry','port':22}

scheme_function2022 = {
    "path" : "testcases/functional2022",
    "echo" : True
}

scheme_performance2022 = {
    "path" : "testcases\performance",
    "echo" : True
}

scheme_temp = {
    "path" : "testcases/tmp",
    "echo" : True
}


if __name__ == '__main__':
    tester = BackendAutoTester(COMPILER, JAVA, OUT_DIR, sftpArg)

    # schemes = [scheme_function2022]
    schemes = [scheme_performance2022]
    # schemes = [scheme_temp]

    for scheme in schemes:
        loader = Loader(scheme.get("path"))
        tester.run(loader.testcases, echo_ret=scheme.get("echo"))
