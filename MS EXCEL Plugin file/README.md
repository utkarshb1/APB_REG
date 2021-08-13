# Interactive-Register-Debugging for MS-EXCEL on Windows.
**wiki Link**: https://wiki.coverify.com/Register-Verification-using-Gnumeric <br>
**NOTE**: This implementation is for MS-Excel - Linux client via TCP -IP using Xlwings version 0.24.1 <br/>
**Pre-requisites to be installed**: <br> Windows Host: xlwings<br>
Linux Client: EUVM, Icarus Verilog, Gnumeric, GCC
## Steps to be followed
1. Clone this repository to your working directory
```
$cd path/to/your/working/directory 
$git clone  https://github.com/utkarshb1/Interactive-Register-Debugging.git
```
2. Setting up xlwings <br/>Watch & Follow - https://youtu.be/5iyL9tMw8vA
3. Open the register Specification sheet in Micro-Enabled mode in MS-EXCEL.
4. Enable all the settings as mentionedin the video link provided in Step 2.
5. Enter the file location of plugin file in UDF Modules without the extension.
6. Now click on the Import Functions, as shown in the below picture. <br/>https://drive.google.com/file/d/1kAdJZ19QMiXZED4qrIr3kWjBX_lBLX4l/view?usp=sharing
7. Make sure that all pre-requisite for Linux client are satisfied and is in path. <br/> <br/>**Note**: Make sure that EUVM is in your PATH, example `echo $PATH` = `/home/user/Intern_Project/euvm-1.0-beta14/bin`:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin
8. Make sure that the IP Address and Port is same in Windows Host & Linux Client, If not same then change them in xlwings plugin file in Windows and apb.d on Linux. 
9. To run the functions: <br/>
  In an empty cell write function `=write(start_range:end_range)` where start_range and end_range are the cells of MS-EXCEL representing the data to be passed to the function and then hit enter. For eg, to perform write operation on Register 2, the arguments will be, `=write(B8:I8)`. If the write operation is successful you’ll be able to see 'DONE' in the same cell.<br/><br/>
  Similar approach is for read operation, `=read(start_range:end_range)`<br/>
10. After you’re done with the simulation, write function `=exit()` in any empty cell to stop the Simulation.
