from BackendTest import BackendAutoTester
from caseloader import Loader

if __name__ == '__main__':
    path = 'testgen-0821-110303'

    tester = BackendAutoTester(path)
    loader = Loader(path)

    tester.run(loader.testcases)

# python3 pi_run.py