# How to use

This script is designed to run on x86 machine to generate the assembly files and transfer them to ARM machine. You can use this as follow:

1. Copy the java archive of compiler & test file into this folder.
2. Configure the path of the corresponding file in [run.py](run.py).
3. Run [run.py](run.py).

> **ATTENTION**: The script use SFTP to transfer, so you should make sure the Raspberry & x86 in the same network.

The tester will create a folder containing the output file in the Raspberry Pi and the OUT_DIR, then you need to run [backend_tester_arm](../backend_tester_arm) on Raspberry to run the assemble file.

# If you want more

You can uncomment the cross compile code and install an arm-gcc on x86 machine to generate object file directly.