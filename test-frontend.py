import subprocess
import os
from datetime import datetime
from pathlib import Path
import filecmp
from typing import List, Optional

from caseloader import TestCase, Loader


class FrontendAutoTester:

    def __init__(self, compiler_path:str, testcases:List[TestCase], 
        java_path:str, out_dir:str) -> None:
        """A FrontendAutoTester is for testing the compiler frontend (generating .ll/.bc files)
        on a given batch of testcases by compiling the .sy sources, interpretively executing
        the generated .bc file, and comparing its output with the standard answser of the
        testcases.

        Args:
            compiler_path: A string of path to the compiler jar package.
            testcases: A list of TestCase to be test on.
            java_path: A string of path to the java interpreter (under JDK/bin/).
            out_dir: A string of path to the directory for storing results.

        The constructor will also create a new directory named after current datetime 
        under current executing path for storing test results and intermediate files.

        * Presume the runtime library sylib.ll is under current directory.
        """
        self.java_path = Path(java_path)
        self.compiler_path = Path(compiler_path)
        self.testcases = testcases
        self.root_dir = Path(out_dir)/Path('testgen-' + datetime.now().strftime(r"%m%d-%H%M%S"))
        self.ll_dir = self.root_dir/"ll"
        self.out_dir = self.root_dir/"out"
        self.res_path = self.root_dir/"result.txt"

        # Create a dir to store generated files.
        os.makedirs(self.root_dir)
        os.makedirs(self.ll_dir)
        os.makedirs(self.out_dir)

    def run(self) -> None:
        """Run through all the testcases to generate results.
        """
        with open(self.res_path, 'w+') as res_file:
            for testcase in self.testcases:
                out_path = self.out_dir/testcase.gen_out_name

                self.run_ll(
                    self.gen_ll(testcase), out_path, testcase.in_path
                )

                msg = '{}\t\t\t{}\n'.format(
                    testcase.sy_path,
                    'Correct' if self.match(out_path, testcase.std_out_path) else 'Wrong'
                )
                res_file.write(msg)
    
    def gen_ll(self, testcase:TestCase) -> str:
        """Generate interpretable .bc file for lli.

        Args:
            testcase: A TestCase to be compiled.
        
        Returns:
            A string of path to the bitcode generated.

        The testcase will be firstly compiled by the compiler to generate the 
        (intermediate) .ll file, which will then be linked with the SysY runtime
        by llvm-link producing self-contained .bc bitcode file.
        Presume the runtime library sylib.ll is under current directory.
        """
        # Compile the .sy file with our compiler.
        ll_path = f"{self.ll_dir}/{testcase.ll_name}"
        cmd_compile = (
            f"{self.java_path}"
            f" -jar {self.compiler_path}"
            f" -s {testcase.sy_path}"
            f" -emit-llvm {ll_path}"
        )
        os.system(cmd_compile)

        # Link sysY runtime into the generated .ll file
        # retrieving the interpretable .bc file.
        bc_path = f"{self.ll_dir}/{testcase.bc_name}"
        cmd_link = f"llvm-link {ll_path} sylib.ll -o {bc_path}"
        os.system(cmd_link)

        return bc_path

    def run_ll(self, bc_path:str, out_path:str, in_path:Optional[str]=None) -> None:
        """Run a interpretable (self-contained) .ll file using lli.

        Args:
            ll_path: A string of the path to the interpretable bitcode file.
            out_path: A string of the path to the file for stdout (output).
            in_path: [Optional] A string of the path to the file for stdin (intput).
        """
        args = ['lli', bc_path]

        with open(out_path, 'a+') as out_file:
            if in_path is None: # Has input
                p = subprocess.run(args, stdout=out_file)
            else:               # No input
                with open(in_path, 'r') as in_file:
                    p = subprocess.run(args, stdin=in_file, stdout=out_file)
            subprocess.run(f"echo {p.returncode}".split(), stdout=out_file)

    def match(self, file1:str, file2:str) -> bool:
        """Match contents of the two files.
        
        Args:
            file1: A string of the path to the 1st text file.
            file2: A string of the path to the 2nd text file.

        Returns:
            True if the two files are identical. Otherwise, return False.
        """
        return filecmp.cmp(file1, file2, shallow=False)
        

if __name__ == "__main__":
    compiler_path = "./Cbias.jar"
    java_path = "./jdk-17.0.3.1/bin/java"
    out_dir = "./out"

    loader = Loader("testcases/stepcases")
    tester = FrontendAutoTester(compiler_path, loader.testcases, java_path, out_dir)

    tester.run()
