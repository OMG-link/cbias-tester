import subprocess
import os
import shutil
from datetime import datetime
from pathlib import Path
import filecmp
from typing import List, Optional

from caseloader import TestCase, Loader


class BackendAutoTester:
    def __init__(self, gen_dir:str):
        self.root_dir = Path(gen_dir)
        self.compilerr_dir = self.root_dir/"ce-cases"
        self.wrongans_dir = self.root_dir/"wa-cases"
        self.log_path = self.root_dir/"result.log"
        self.stat_path = self.root_dir/"stat.log"
        self.max_path_width = 45
        
        if self.wrongans_dir.exists():
            self.delete_dir(self.wrongans_dir)
        os.makedirs(self.wrongans_dir)
        if self.compilerr_dir.exists():
            self.delete_dir(self.compilerr_dir)
        os.makedirs(self.compilerr_dir)

    def delete_dir(self, path:Path):
        if path.exists():
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                for file in path.iterdir():
                    self.delete_dir(file)
                path.rmdir()


    def run(self, 
        testcases: List[TestCase], echo_ret:bool=True, terminal_log=True) -> None:
        """Run through all the testcases to generate results.

        Args:
            echo_ret: Bool indicating if to echo the process return codes to .out files.
        """
        # Adjust logging format.
        new_width = max([len(str(tc.s_path)) for tc in testcases])
        if new_width > self.max_path_width:
            self.max_path_width = new_width
        # Statistic Info
        cnt_wrongans = 0
        cnt_compilerr = 0
        cnt_accept = 0

        # Run.
        with open(self.log_path, 'a+') as log_file, open(self.stat_path, 'a+') as stat_file:
            # Loop through each test case.
            for testcase in testcases:                
                out_path = self.root_dir/testcase.gen_out_name
                s_path = self.root_dir/testcase.s_path.name

                if terminal_log:
                    print(str(testcase.s_path).ljust(self.max_path_width, ' ') + f' \tRunning', 
                    end='\r')

                o_path = self.gen_out(testcase)
                if o_path is None:
                    status = 'Compilation Error'
                    cnt_compilerr += 1
                    # Copy the error-compiled testcase to the CE-directory.
                    p = testcase.copy_to(self.compilerr_dir)
                else:
                    self.run_asm(o_path, out_path, testcase.in_path)
                    if self.match(out_path, testcase.std_out_path):
                        status = 'Accecpted'
                        cnt_accept += 1
                    else:
                        status = 'Wrong Answer'
                        cnt_wrongans += 1
                        # Copy the wrongly answered testcase to the WA-directory.
                        p = testcase.copy_to(self.wrongans_dir)
                        shutil.copyfile(out_path, p/testcase.gen_out_name)
                
                log = (
                    str(testcase.s_path).ljust(self.max_path_width, ' ')
                    + f' \t{status}\n'
                )
                log_file.write(log)
                if terminal_log:
                    print(log, end='')
            # Statistical conclusion.
            stat_conclu = (
                f'AC: {cnt_accept:>3}/{len(testcases)}, '
                f'CE: {cnt_compilerr:>3}/{len(testcases)}, '
                f'WA: {cnt_wrongans:>3}/{len(testcases)}\n'
            )
            stat_file.write(stat_conclu)
            if terminal_log:
                print(stat_conclu, end='')

    
    def gen_out(self, testcase:TestCase) -> str:
        # Compile the .sy file with our compiler.
        out_path = self.root_dir / testcase.name
        cmd_compile = (
            f"gcc"
            f" {testcase.s_path}"
            f" -o {out_path}"
            f" -L ."
            f" -lsysy"
            # f" -march=armv7"
            # f" -mcpu=cortex-a7"
            # f" -mfloat-abi=hard"
        )
        subprocess.run(
            cmd_compile.split(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        # If the compiler didn't successfully generate an .ll file.
        if not os.path.exists(out_path):
            return None

        return out_path


    def run_asm(self, 
        o_path:str, out_path:str, in_path:Optional[str]=None, echo_ret:bool=True
    ) -> None:
        cmd_run = f'./{o_path}'
        with open(out_path, 'w+', encoding="utf-8") as out_file:
            # Has input
            if in_path is None: 
                p = subprocess.run(
                    cmd_run.split(), 
                    stdout=out_file,
                    stderr=subprocess.DEVNULL,
                    encoding="utf-8"
                )
            # No input
            else:               
                with open(in_path, 'r') as in_file:
                    p = subprocess.run(
                        cmd_run.split(), 
                        stdin=in_file, 
                        stdout=out_file,
                        stderr=subprocess.DEVNULL,
                        encoding="utf-8"
                    )

            # Echo the return value to the output if required.
            if echo_ret:
                # If the execution generates any output, and the last character
                # is not a newline ('\n'), then
                # echo to switch to a new line for the return value.
                if os.path.getsize(out_path) > 0:
                    with open(out_path, 'r', encoding="utf-8") as f:
                        last_ch = f.read()[-1]
                    if last_ch != '\n':
                        subprocess.run('echo', stdout=out_file)
                subprocess.run(f'echo {p.returncode}'.split(), stdout=out_file)
            

    def match(self, file1:str, file2:str) -> bool:
        return filecmp.cmp(file1, file2, shallow=False)
