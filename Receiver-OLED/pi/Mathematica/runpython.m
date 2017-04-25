(* ::Package:: *)

(*runpython.nb*)
(*load the Mathlink system rfcomm, to execute a python script running the ILOCI listener*)
(*Exit[];*)
linkrfcomm = Install["/home/pi/projects/ML_System/ML_System"];
(*Initialize the rfcomm variable PYTHON*)
PYTHON=5;
(*rfcomm[PYTHON] executes "sudo python /home/pi/projects/OLEDPython/iloci2_graph.py"
The function does not return until it is terminated by dropping the connection, 
and pushing the button, which causes the python script to exit. 
 The While loop terminates when the reboot 
button on GPIO 24 is held pressed at the same time as the save data switch*)
(********************* SET runlisten to True for operations, False so it runs only one loop for debug *****)
runlisten=True;
While[runlisten,
 result = rfcomm[PYTHON];  (*NOTE: rfcomm[PYTHON] has to be updated with new file name*)
 If[result == -1, Print["rfcomm(PYTHON) did not succeed - check the path to iloci2_graph.py"];
	Break[];,
(*else*)
	 Print["python iloci2_graph.py terminated - restarting it.."];
 ];
 Pause[1];
 gpio24=24/.DeviceRead["GPIO",24];
 If[gpio24==0,runlisten = False];
];
Print["gpio24 is ",gpio24," runlisten is ", runlisten ];
Exit[];








