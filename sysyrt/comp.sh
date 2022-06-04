# compile the SysY runtime using the command below
# and move the sylib.ll generated to the project root. 
clang -emit-llvm -S sylib.c