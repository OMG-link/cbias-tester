# CBIAS Tester

This repo is the code of batch tester for compiler project [CBIAS](https://github.com/cabinz/cbias).

## Frontend Tester

Cbias frontend has an IREmitter to emit in-memory intermediate code as .ll text,
which meets text-based LLVM IR format and can be recognized by LLVM tool chain.

Thus, before in-memory IR can be processed by backend to generate assembly code, 
IR can be run by being dumped as text file and conveyed to LLVM tool chain. Batch
test can be perform on frontend for debugging purposes.

## Backend Tester

Uploaded soon.
