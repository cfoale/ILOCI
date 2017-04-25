(* ::Package:: *)

(*RunILOCIv0.91.m  6/26/16 *)
(*0.91 add datafile descriptionfile dat.txt - cmf 6/27/16*)
(*Modified 10/27/16 to add HALT command "sudo halt", 
to rfcomm argument list.  Command is implemented using CMD2*)


(*Check the slide data  switch*)
DeviceWrite["GPIO",17->0];  (*turn off the green LED, we just booted up*)
Print["RunILOCIv0.9.m ..Looking for switch for 30 seconds.."];
(*Pause 30 seconds while waiting for the switch*)
Do[
  gpio22in =22/.DeviceRead["GPIO",22];
(*SIMULATED mcp3008 board*)
  gpio22in=0 (*0 exits*);
  If[gpio22in==1,
    DeviceWrite["GPIO",17->1];(*turn the LED on*)
	Break[]
  ];
  Pause[1];,
  {i,1,30}
];(* llop for 30 seconds*)
If[gpio22in==0,
 Print["RunILOCIv0.9.m finishing..nothing done"];
 Exit[]
];
(*otherwise continue*)
DeviceWrite["GPIO",17->1];
(*LED GPIO 17 should be lit*)
(*****Logging***)
(*create a file stream object using a log file to increment the same day*)

makeNewUpdateName[]:=Block[{updatefilename},
 d=Date[];
 logname= "/home/pi/Mathematica/runnumber.log";
 lognumber=Import[logname,"List"][[1]];
 lognumber = lognumber +1;
 Export[logname,lognumber,"List"]; 
 updatefilename= "/home/pi/Mathematica/"<>ToString[d[[1]]]<>"_"<>ToString[d[[2]]]<>"_"<>ToString[d[[3]]]<>"_"<>ToString[lognumber]<>".m"
];
(*Specify where to put the data updates for further training*)

updatefilename = makeNewUpdateName[];
(***************initialization******************************)
csvfilepath="/home/pi/Mathematica/";
(*Give the file path and name of the classifier to be used*)
classifierfile = csvfilepath <> "ILOCITest8Classifier.m";

(*****data recording*)
frametime=0.2;
(*dt=frametime*10^*6 -2200 *)
dt = Floor[frametime*1000000-2000]; (*SPIDevMcp3008 requires an integer parameter*)(*200 mseconds is the goal but we subtract a 2 msec for the program overhead*)
datename= "/home/pi/Mathematica/"<>ToString[d[[1]]]<>"_"<>ToString[d[[2]]]<>"_"<>ToString[d[[3]]]<>"_"<>ToString[lognumber]<>".dat";
Print["Datename data File is ",datename];
datafilehandle = OpenWrite[datename];

logfilename= "/home/pi/Mathematica/"<>ToString[d[[1]]]<>"_"<>ToString[d[[2]]]<>"_"<>ToString[d[[3]]]<>"_"<>ToString[lognumber]<>"_log.txt";
PutAppend[DateString[]<>":Start",logfilename];

(*Classifier helper functions*)
pN=classify[#,"Probabilities"][[3]]&;
pD=classify[#,"Probabilities"][[1]]&;
pL=classify[#,"Probabilities"][[2]]&;
pR=classify[#,"Probabilities"][[4]]&;

(*data is accessible using SPI*)
GetOneFrame[]:=Module[{linelist},realdata={};
adc=SPIDevMcp3008[nchannels,dt];
(*write the list to the log file handle s*)
  WriteString[datafilehandle,adc[[1]]," ",adc[[2]]," ",adc[[3]]," ",adc[[4]]," ",adc[[5]]," ",adc[[6]]," ",adc[[7]]," ",adc[[8]],"\n"];
(* write the list to a list realdata for use by classify. More than one frame can be added if classify looks at data history (derivatives) *)
linelist={adc[[1]],adc[[2]],adc[[3]],adc[[4]],adc[[5]],adc[[6]],adc[[7]],adc[[8]]};
AppendTo[realdata,linelist];
nframes=nframes+1;
];

nframes=0;(*initialized*)

(*showOneFramePerformance runs classify by applyin the probability rules.
Choose a threshold value for the action probabilities by setting paction*)
showOneFramePerformance[printQ_]:=Module[{probN,probD,probL,probR,paction},
probN=Part[pN/@realdata,1];
If[probN < 0.0001,probN=0.];(*make really small numbers zero*)
probD=Part[pD/@realdata,1];
If[probD < 0.0001,probD=0.];(*make really small numbers zero*)
probL=Part[pL/@realdata,1];
If[probL < 0.0001,probL=0.];(*make really small numbers zero*)
probR=Part[pR/@realdata,1];
If[probR < 0.0001,probR=0.];(*make really small numbers zero*)
(*add a leading digit to probN based on the action required*)
paction=0.5;
If[probD > paction,probN=probN+2.0];
If[probL > paction,probN=probN+3.0];
If[probR > paction,probN=probN+4.0];
{probN,probD,probL,probR}];

(*Create realistic data for ILOCI sitting on the bench. NOT FOR FLIGHT*)
tableTopILOCI[]:=Module[{real,flight,table},
real=realdata[[1]];
flight={510,598,508,517,171,755,469,755};
table={512,606,511,507,504,179,124,388};
realdata={flight-table+real}
];

(*********************************************************************************************)
(*RFComm functions*)
rfcommConnect[t_]:= Module[{singleread,time,timeout,goodQ},
PutAppend[DateString[]<>":Listening for ILOCIc..",logfilename];
goodQ=False;(*keep track of what has worked during the connection process*)
DeviceClose[commdev];(*Hanup our last event, if it was not done previously*)
rfcomm[HANGUP];
timeout = t;time=0;
While[rfcomm[SHOW]== 0, (*returns 1 when connected*)
(*creates a serial device linked to the bluetooth serial channel 22*)
 rfcomm[CONNECT];(*not a blocking call*)
Pause[1];(*wait until the connection is made*)
time = time + 1;(*increment our timeout clock*)
If[time > timeout,
Print["Make connection time out. Hanging up"];
PutAppend[DateString[]<>":Make connection time out. Hanging up",logfilename];
DeviceClose[commdev];
rfcomm[HANGUP];
Break[]
];
goodQ= True;
];
(*verify we are connected*)
If[FileExistsQ["/dev/rfcomm0"],(*this is proof from linux we are connected*)
Print["Connected to client"];
PutAppend[DateString[]<>":Connected to client",logfilename];
commdev=DeviceOpen["Serial","/dev/rfcomm0"];
goodQ=True,(*so this is Mathematica's access to the serial port*)
(*else*)
Print["/dev/rfcomm0 was not created as expected"];
DeviceClose[commdev];
rfcomm[HANGUP];
goodQ=False;
];
(*receive a response from the listener*)
While[!DeviceExecute[commdev,"SerialReadyQ"],
Pause[1];
If[rfcomm[SHOW]==0,Break[];goodQ=False](*keep checking to see if the connection was dropped*)
];
If[rfcomm[SHOW]==1,
(*the response should be terminated with a new line character byte \n, which is 10 decimal*)
singleread= FromCharacterCode[DeviceReadBuffer[commdev,"ReadTerminator"->10]],
(*else*)
Print["Connection was dropped"];goodQ=False
];
(*verify what we got was "Ready for data"*)
If[singleread == "Ready for data",
DeviceWrite[commdev,"data follows\n"];goodQ=True,
(*else*)
Print["Unexpected response from the client..Hanging up"];
PutAppend[DateString[]<>":Unexpected response from the client..Hanging up",logfilename];
DeviceClose[commdev];
rfcomm[HANGUP];
goodQ=False;
];
goodQ
];
(************************************end of comm***************************************)


(*Sending float values - comm protocol functions*)
sendFloatReceiveCommand[f_]:=Module[{goodQ,trys,singleread,x},
goodQ=False;
trys=0;
(*prevent display of f in MMA scientific notation
as the Python float function cannot read it *)
x=FortranForm[SetPrecision[f,5]];
DeviceWrite[commdev,ToString[x]<>"\n"];
While[trys <  10000,(* a 20 second or so wait*)
If[DeviceExecute[commdev,"SerialReadyQ"],
singleread= DeviceReadBuffer[commdev,"ReadTerminator"->10];
(*Print["recvd ",ToExpression[singleread]]*)
If[Length [singleread]>=0,
goodQ=True;
receivedCommand= FromCharacterCode[singleread];
Break[];
];
];
trys = trys+1;
];
goodQ
];

(*Process the commands from the two lbuttons of the listener*)
(**)
processCommand[]:=Module[{result},
 If[StringLength[receivedCommand]>0,
    Print["Received command "<> receivedCommand];
    PutAppend[DateString[]<>":Received command "<>receivedCommand,logfilename];
 ];
 Switch[receivedCommand,
"CMD1",saveUpdatePairs[],
         "CMD2",Print["Exiting.. for CMD2"];
             PutAppend[DateString[]<>":Exiting ",logfilename];
stopsending=True;runiloci=False,(*this formerly had RFCOMM(HALT), which shutdown RPi2 completely*)
"CMD3",Print["pauseSending[30] not implemented"]
   ];
];

(**)
AddDataToUpdate[]:=Module[{},
If[Length[updatedata]>=nupdates,
(*remove the first measurement in the list, the oldest one*)
updatedata= Take[updatedata,-(nupdates-1)];
];
AppendTo[updatedata,realdata[[1]]];
];

(*saveUpdatePairs is called by processCommands *)
saveUpdatePairs[]:=Module[{existing,newupdates},
If[FileExistsQ[updatefilename],
existing = Import[updatefilename];
         newupdates =Join[existing,updatedata];
Put[newupdates,updatefilename];,
(*else*)
Put[updatedata,updatefilename];
];
 Print["Appended update data to "<>updatefilename];
 PutAppend[DateString[]<>":Appended update data to "<>updatefilename,logfilename];
];



(*Initialize - one time Executable *)

(*Setup the update pair list*)
(*as determined by the listener display horizontal pixel count*)listenerdisplaypoints = 120;(*needs to be defined in one place*)
ILOCIperiod = 10.0; (*time in seconds used to create an ILOCI training rule set*)
nupdates = ILOCIperiod/frametime;updatedata = {};(*a global list containing recent measurements for additional training*)

(*initialize the classifier*)
 (*Initialize the classify method*)
 classify = Get[classifierfile];

 (*Load the SPI analog data Mathlink*)
 linkmcp3008 = Install["/home/pi/projects/ML_spidev_mcp3008/ML_spidev_mcp3008"];

(*initialize the description file time values*)
nchannels=8;
adc=SPIDevMcp3008[nchannels,dt];
(*take one measurement and establish a zero time using the time values returned*)
is = nchannels+1;ius = nchannels + 2;
(*these are indexes into the list to get the seconds, and microseconds returned*)
t0secs = adc[[is]];t0usecs = adc[[ius]];
nframes = 0;(*counter increments each time GetOneFrame[] is called*)


(***********repeated Executable statements***********)
runiloci = True;
While[runiloci,

(*Load the Bluetooth rfcomm Mathlink*)
 linkrfcomm = Install["/home/pi/projects/ML_System/ML_System"];

(*Initialize rfcomm to add Bluetooth channel 22  using Mathlink C functions*)
 {RFCOMMINIT = 0,CONNECT= 1,LISTEN=2, HANGUP = 3,SHOW = 4, PYTHON = 5, HALT = 6};
 rfcomm[RFCOMMINIT];

(*connect to the listener*)
 rfcommConnect[3600]; (*60 minute timeout*)

(*start the main loop*)
 stopsending= False;
 While[!stopsending,
  If[rfcomm[SHOW]==0,
   Print["connection dropped - hanging up"];
   PutAppend[DateString[]<>":Connection dropped - hanging up!",logfilename];
   Break[];
  ];
  GetOneFrame[];(*get a data frames in a list called realdata*)
 (*the next line is for table top ILOCI only*)
 (*tableTopILOCI[];*)(*comment this out. NOT FOR FLIGHT*)
  output=showOneFramePerformance[False];

  AddDataToUpdate[];
  OOF=output[[1]];

  commQ = sendFloatReceiveCommand[OOF];
  If[!commQ,
   Print["comm dropped.."];
   PutAppend[DateString[]<>":Comm dropped!",logfilename];
   Break[];
  ];
  processCommand[];
  
  (****debugging**)
  (*poll our physical switch to see if we should exit*)
  gpio22in =22/.DeviceRead["GPIO",22];
  (*SIMULATED*)
   gpio22in=1;
  If[gpio22in==0,
     DeviceWrite["GPIO",17->0];(*turn the LED off*)
 	stopsending = True;
     runiloci=False;
       PutAppend[DateString[]<>":Switch is off",logfilename];
  ];
  (****end debuggging*)
 ];
(*when connection is dropped, or stopsending is true*)
 DeviceClose[commdev];
 rfcomm[HANGUP];
 Uninstall[linkrfcomm];
] ;(*returns to upper While, repeats initialization*)
tusecs = (adc[[is]]-t0secs)*1000000+ (adc[[ius]] -t0usecs);
framemsecs=(tusecs - t0usecs)/(nframes)/1000.;
Uninstall[linkmcp3008];
(*Print out our result*)
Print["For ",is-1," channels, the frame time is ",framemsecs," ms."];
descriptionname = datename<>".txt";
descriptionlist = {t0secs,t0usecs,adc[[is]],adc[[ius]] ,nframes};
Export[descriptionname,descriptionlist];
(*out of the while loop - we really are done*)
Close[datafilehandle]; (*the same data file is used for all reconnection attempts*)
PutAppend[DateString[]<>":Frame time (ms) "<>ToString[framemsecs],logfilename];
PutAppend[DateString[]<>":RunILOCIv0.9.m is complete",logfilename];
Print["RunILOCIv0.9.m is complete."];
Exit[]; 













