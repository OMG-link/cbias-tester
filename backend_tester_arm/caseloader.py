from genericpath import exists
import os
from pathlib import Path
from sys import stdout
import shutil

IN = 'in/'
STD_OUT = 'std_out/'

class TestCase:
    """A TestCase store the path to a single testcase and its metadata.
    
    Attributes:
        s_path: A Path to the source (.sy) 
        in_path: A Path to the possible input file (.in)
        std_out_path: A Path to the standard output file (.out)
        name: A string of the testcase name w/o file type postfix
        ll_name: A string of file name of llvm-ir generated (.ll)
        bc_name: A string of file name of the interpretable bitcode file after linking (.bc)
        gen_out_name: A string of file name of the execution output from the compiled program 
                    (-gen.out)
    """

    def __init__(self, s_path:str, std_out_path:str, in_path:str=None) -> None:
        """Initialzie a TestCase.
        """
        # Path to the source (.s) 
        self.s_path = Path(s_path)
        # Path to the possible input file (.in)
        self.in_path = Path(in_path) if in_path else None
        # Path to the standard output file (.out)
        self.std_out_path = Path(std_out_path)
        # Name of the testcase w/o file type postfix
        self.name = self.s_path.name.replace(".s", "")
        # File name for object generated
        self.out_name = self.name + ".out"
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
        if not copy_path.exists():
            os.makedirs(copy_path)
        shutil.copyfile(self.s_path, copy_path/(self.s_path.name))
        if not self.in_path is None:
            shutil.copyfile(self.in_path, copy_path/(self.in_path.name))
        shutil.copyfile(self.std_out_path, copy_path/(self.std_out_path.name))
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
        # If the path points to a testable file (.s).
        if p.is_file() and p.suffix == '.s':
            std_out_path = Path(STD_OUT + (p.name.replace(".s", ".out")))
            in_path = Path(IN + (p.name.replace(".s", ".in")))
            self.testcases.append(TestCase(p, std_out_path, in_path if in_path.exists() else None))
        # If the path points to a existing dir,
        # add all testable files into self.testcases.
        elif p.is_dir():
            for file in sorted(p.glob('*.s')):
                std_out_path = Path(STD_OUT + (file.name.replace(".s", ".out")))
                in_path = Path(IN + (file.name.replace(".s", ".in")))
                self.testcases.append(TestCase(file, std_out_path, in_path if in_path.exists() else None))


if __name__ == '__main__':
    loader = Loader('testcases/myTestcases')
