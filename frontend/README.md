# Frontend Tester

Cbias frontend has an IREmitter to emit in-memory intermediate code as .ll text,
which meets text-based LLVM IR format and can be recognized by LLVM tool chain.

Thus, before in-memory IR can be processed by backend to generate assembly code, 
IR can be run by being dumped as text file and conveyed to LLVM tool chain. Batch
test can be perform on frontend for debugging purposes.

## Environment

* Platform: Ubuntu 20.04 (recommended)
* JDK: 17.0.3.1 (recommended)
* Clang: 10.0 (for lli)
* LLVM: 10.0 (for llvm-link)

Compile the SysY runtime under [sysyrt](sysyrt/) using the command below
and move the sylib.ll generated to the project root. 
```
clang -emit-llvm -S sylib.c
```

## Structure

You working directory may look like:
```
.
├── Cbias.jar
├── README.md
├── caseloader.py
├── frontend_tester.py
├── jdk-17.0.3.1
│   ├── ...
├── out
│   ├── ...
├── run.py
├── sylib.ll
└── testcases
    ├── ...
```

* `jdk-17.0.3.1` is where your java distribute locates.
* `Cbias.jar` is the package of the Cbias project. 
* `out` is a manually created dir for batch test output results.
* `testcases` is a manually created dir for storing testcases.
* `sylib.ll` is the pre-compiled lib SysY runtime to link. 

Tips: If you are using IntelliJ to modifiy Cbias, project artifact can be configured to 
automatically emit a jar new package whenever you change and re-compile the code.

The frontend tester will conduct the following routine over each testcase:

`testcase.sy` =[Cbias.jar]=> `testcase.ll` =[llvm-link]=> `testcase.bc` =[lli]=> `testcase-gen.out`

Then `testcase-gen.out` will be matched with standard output `testcase.out`.


## Usage

You may create a seperated python script as below for the convenience of re-doing batch testing:

```python3
from frontend_tester import FrontendAutoTester 
from caseloader import Loader, TestCase

COMPILER = "./Cbias.jar"
JAVA = "./jdk-17.0.3.1/bin/java"
OUT_DIR = "./out"

scheme = {
    "path" : "testcases/function_test2022",
    "echo" : True
}


if __name__ == '__main__':
    tester = FrontendAutoTester(COMPILER, JAVA, OUT_DIR)
    
    loader = Loader(scheme.get("path"))
    tester.run(loader.testcases, echo_ret=scheme.get("echo"))

```

where the field of `echo` specifies if the return value of the process will be printed out to the output file for answer matching.

The terminal log may look like:

```
HOSTNAME:~/path/CbiasTester/frontend$ python run.py

testcases/function_test2022/00_main.sy                  Accecpted
testcases/function_test2022/01_var_defn2.sy             Accecpted
testcases/function_test2022/02_var_defn3.sy             Accecpted
...
testcases/function_test2022/95_float.sy                 Accecpted
testcases/function_test2022/96_matrix_add.sy            Accecpted
testcases/function_test2022/97_matrix_sub.sy            Accecpted
testcases/function_test2022/98_matrix_mul.sy            Accecpted
testcases/function_test2022/99_matrix_tran.sy           Accecpted
✔ AC: 100/100, CE:   0/100, WA:   0/100
```

Completion status: 
* Accecpted (AC): A testcase end with correct output answer.
* Compilation Error (CE): Errors occured during `testcase.sy` =[Cbias.jar]=> `testcase.ll` =[llvm-link]=> `testcase.bc`.
* Wrong Answer (WA): Errors occured during `testcase.bc` =[lli]=> `testcase-gen.out`, or the answer matching phase.

Under `out` dir, more detailed results and statistical reports will be generated.
