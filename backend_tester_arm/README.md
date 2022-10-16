# How to use

This script is designed to run on ARM machine to run the assembly file and compare the answer.

Requirements:

1. GCC
2. Python 3+

You can use this as follow:

1. Copy all standard file ending with '.in' & '.out' into two different folder
2. Configure the **IN** & **STD_OUT** in [caseloader.py](caseloader.py)
3. Each time the x86 server transfer file to ARM, you need to modify the **path** in [pi_run.py](pi_run.py), then run it