from pathlib import Path


class TestCase:
    def __init__(self, sy_path:str, std_out_path:str, in_path:str=None) -> None:
        """A TestCase instance store the path to a single testcase and its metadata.
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
        # File name for output log file
        self.gen_out_name = self.name + "-gen.out"


class Loader:
    def __init__(self) -> None:
        pass