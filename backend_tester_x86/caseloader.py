from genericpath import exists
import os
from pathlib import Path
from sys import stdout
import shutil


class TestCase:
    """A TestCase store the path to a single testcase and its metadata.
    
    Attributes:
        sy_path: A Path to the source (.sy) 
        in_path: A Path to the possible input file (.in)
        std_out_path: A Path to the standard output file (.out)
        name: A string of the testcase name w/o file type postfix
        ll_name: A string of file name of llvm-ir generated (.ll)
        bc_name: A string of file name of the interpretable bitcode file after linking (.bc)
        gen_out_name: A string of file name of the execution output from the compiled program 
                    (-gen.out)
    """

    def __init__(self, sy_path:str, std_out_path:str, in_path:str=None) -> None:
        """Initialzie a TestCase.
        """
        # Path to the source (.sy) 
        self.sy_path = Path(sy_path)
        # Path to the possible input file (.in)
        self.in_path = Path(in_path) if in_path else None
        # Path to the standard output file (.out)
        self.std_out_path = Path(std_out_path)
        # Name of the testcase w/o file type postfix
        self.name = self.sy_path.name.replace(".sy", "")
        # File name for llvm-ir generated
        self.ll_name = self.name + ".ll"
        # File name for the interpretable bitcode file after linking. 
        self.bc_name = self.name + ".bc"
        # File name for assemble generated
        self.s_name = self.name + ".s"
        # File name for object generated
        self.o_name = self.name + ".o"
        # File name for output log file
        self.gen_out_name = self.name + "-gen.out"

    def copy_to(self, dest:str) -> Path:
        """Copy all files realted to a testcase to a given directory.

        Args:
            dest: String of the path to the target directory.
        Returns:
            pathlib.Path to the directory created by the methods for storing the copy of the files.
        """
        copy_path = Path(dest)/self.name
        os.makedirs(copy_path)
        shutil.copyfile(self.sy_path, copy_path/(self.sy_path.name))
        return copy_path


class Loader:
    """Loader helps to load TestCase according to a given file path or directory.

    Attributes:
        testcases: A List of TestCases (to be test).
    """

    def __init__(self, path:str) -> None:
        """Intialize a Load according to a given path.
        
        If the path points to a testable file (.sy file), load the file specified
        as a single TestCase. If the path points to an existing directory, load all
        testable files under the directory into the testcase list.
        """
        self.testcases = []

        p = Path(path)
        # If the path points to a testable file (.sy).
        if p.is_file() and p.suffix == '.sy':
            std_out_path = p.with_suffix('.out')
            in_path = p.with_suffix('.in')
            self.testcases.append(
                TestCase(p, std_out_path, in_path if in_path.exists() else None)
            )
        # If the path points to a existing dir,
        # add all testable files into self.testcases.
        elif p.is_dir():
            for file in sorted(p.glob('*.sy')):
                std_out_path = file.with_suffix('.out')
                in_path = file.with_suffix('.in')
                self.testcases.append(
                    TestCase(file, std_out_path, in_path if in_path.exists() else None)
                )


if __name__ == '__main__':
    loader = Loader('testcases/myTestcases')
