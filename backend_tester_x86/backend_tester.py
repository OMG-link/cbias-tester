import subprocess
import os
import shutil
from datetime import datetime
from pathlib import Path
from mySftp import MainWindow
import filecmp
from typing import List, Optional

from caseloader import TestCase, Loader


class BackendAutoTester:
    """An auto tester for the backend testing batch of test cases all at once.
    """

    def __init__(self, compiler_path:str, java_path:str, gen_dir:str, sftpArg) -> None:
        """Initialize a BackendAutoTester.
        """
        self.java_path = Path(java_path)
        self.compiler_path = Path(compiler_path)
        self.root_dir = Path(gen_dir)/Path('testgen-' + datetime.now().strftime(r"%m%d-%H%M%S"))
        self.asm_dir = self.root_dir/"asm"
        self.out_dir = self.root_dir/"out"
        self.log_path = self.root_dir/"result.log"
        self.stat_path = self.root_dir/"stat.log"
        self.wrongans_dir = self.root_dir/"wa-cases"
        self.compilerr_dir = self.root_dir/"ce-cases"
        
        self.max_path_width = 45
        self.dst = '/home/pi/test/testgen-' + datetime.now().strftime(r"%m%d-%H%M%S")
        self.dst1 = '/home/pi/test/in'
        self.dst2 = '/home/pi/test/std_out'

        self.sftp = MainWindow(sftpArg)
        self.sftp.startup()

        # Create a dir to store generated files.
        os.makedirs(self.root_dir)
        os.makedirs(self.asm_dir)
        os.makedirs(self.out_dir)
        os.makedirs(self.wrongans_dir)
        os.makedirs(self.compilerr_dir)

    def run(self, 
        testcases: List[TestCase], echo_ret:bool=True, terminal_log=True) -> None:
        """Run through all the testcases to generate results.

        Args:
            echo_ret: Bool indicating if to echo the process return codes to .out files.
        """
        # Adjust logging format.
        new_width = max([len(str(tc.sy_path)) for tc in testcases])
        if new_width > self.max_path_width:
            self.max_path_width = new_width
        # Statistic Info
        cnt_wrongans = 0
        cnt_compilerr = 0
        cnt_trans = 0

        # Run.
        with open(self.log_path, 'a+') as log_file, open(self.stat_path, 'a+') as stat_file:
            # Loop through each test case.
            for testcase in testcases:                
                out_path = self.out_dir/testcase.gen_out_name
                s_path = self.asm_dir/testcase.s_name

                if terminal_log:
                    print(str(testcase.sy_path).ljust(self.max_path_width, ' ') + f' \tRunning', 
                    end='\n')

                o_path = self.gen_asm(testcase)
                if o_path is None:
                    status = 'Compilation Error'
                    cnt_compilerr += 1
                    # Copy the error-compiled testcase to the CE-directory.
                    p = testcase.copy_to(self.compilerr_dir)
                    if os.path.exists(s_path):
                        shutil.copyfile(s_path, p/(s_path.name))
                else:
                    print(str(testcase.sy_path).ljust(self.max_path_width, ' ') + f' \tCompiled', 
                    end='\n')
                    OK = self.trans_asm(testcase)
                    if OK == 'ERROR':
                        status = 'Transmit Fail'
                        cnt_wrongans += 1
                    else:
                        status = 'Transmitted'
                        cnt_trans += 1
                log = (
                    str(testcase.sy_path).ljust(self.max_path_width, ' ')
                    + f' \t{status}\n'
                )
                log_file.write(log)
                if terminal_log:
                    print(log, end='')
            # Statistical conclusion.
            stat_conclu = (
                f'TS: {cnt_trans:>3}/{len(testcases)}, '
                f'CE: {cnt_compilerr:>3}/{len(testcases)}, '
                f'ER: {cnt_wrongans:>3}/{len(testcases)}\n'
            )
            stat_file.write(stat_conclu)
            if terminal_log:
                print(stat_conclu, end='')
            self.sftp.shutdown()

    
    def gen_asm(self, testcase:TestCase) -> str:
        # Compile the .sy file with our compiler.
        s_path = f"{self.asm_dir}/{testcase.s_name}"
        cmd_compile = (
            f"{self.java_path}"
            f" -jar {self.compiler_path}"
            f" -s {testcase.sy_path}"
            f" -o {s_path}"
        )
        subprocess.run(
            cmd_compile.split(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        # If the compiler didn't successfully generate an .ll file.
        if not os.path.exists(s_path):
            return None
        
        o_path = f"{self.asm_dir}/{testcase.o_name}"
        # cmd_link = f"arm-none-eabi-gcc {s_path} -L . -lsysy -o {o_path} -mcpu=cortex-a7 -mfloat-abi=hard"
        # subprocess.run(
        #     cmd_link.split(),
        #     stdout=subprocess.DEVNULL,
        #     stderr=subprocess.DEVNULL
        # )
        # # If the llvm-linker didn't successfully generate a .bc file.
        # if not os.path.exists(o_path):
        #     return None

        return o_path

    def trans_asm(
        self, testcase:TestCase
    ):
        replace = False
        return self.sftp.upload(f"{self.asm_dir}/{testcase.s_name}", self.dst, replace)
        # self.sftp.upload(f"{self.asm_dir}/{testcase.o_name}", self.dst, replace)