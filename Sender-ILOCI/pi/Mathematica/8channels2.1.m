(* ::Package:: *)

(*8channels2.1.m
Modified by cmf 2/7/17
ILOCI data recording at 2Hz rate, sample interval 500ms*)

DeviceWrite["GPIO",17->0];
Print["8channels2.1.m ..Looking for switch for 30 seconds.."];
(*Pause 30 seconds while waiting for the switch*)
Do[
  gpio18in =22/.DeviceRead["GPIO",22];
  If[gpio18in==1,
        DeviceWrite["GPIO",17->1];Break[]];
  Pause[1];,
{i,1,30}];
If[gpio18in==0,Print["8channels2.1.m finishing..nothing done"];Exit[]];

DeviceWrite["GPIO",17->1];
(*LED GPIO 24 should be lit*)
linkmcp3008 = Install["/home/pi/projects/ML_spidev_mcp3008/ML_spidev_mcp3008"];
Print["The link is ", linkmcp3008];
nchannels=8;
(***VERIFY NPOINTS *)
npoints= 3*60*60*2;(*we will get this max number of time values*..3hour*)
(*dt is in usecs*)
dt = 500000-2000; (*500 mseconds is the goal but we subtract a 1.7 msec for the program overhead*)
(*create a file stream object using a log file to increment the same day*)
logname= "/home/pi/8channels2.1.log";
lognumber=Import[logname,"List"][[1]];
lognumber = lognumber +1;
Export[logname,lognumber,"List"]; 

d=Date[];



datename= "/home/pi/"<>ToString[d[[1]]]<>"_"<>ToString[d[[2]]]<>"_"<>ToString[d[[3]]]<>"_"<>ToString[lognumber]<>".dat";
Print["File ",datename," will have size ", (10.0/7.0)*192.0*npoints/(60*200)," KB"];
s = OpenWrite[datename];
adc=SPIDevMcp3008[nchannels,dt];
(*take one measurement and establish a zero time using the time values returned*)
is = nchannels+1;ius = nchannels + 2;
(*these are indexes into the list to get the seconds, and microseconds returned*)
t0secs = adc[[is]];t0usecs = adc[[ius]];

Do[adc=SPIDevMcp3008[nchannels,dt];
(*convert the seconds elapsed to microseconds, as these are the units required*)(*write the time in microseconds, and the channel values to the a list, and write the list to a file, and repeat from 1 to npoints*)
  WriteString[s,adc[[1]]," ",adc[[2]]," ",adc[[3]]," ",adc[[4]]," ",adc[[5]]," ",adc[[6]]," ",adc[[7]]," ",adc[[8]],"\n"];
(*scan for switch*)
  If[Mod[i,20]==0, (*check takes 5ms, called every 10 seconds, interrupts one data point*)
    gpio22in =22/.DeviceRead["GPIO",22];
    (*If hi, Turn off the LED, we are done*)
    If[gpio22in==0,DeviceWrite["GPIO",17->0];npoints= i;Break[]]
  ];
, {i,1,npoints}];

DeviceWrite["GPIO",17->0];  (*We are done,turn off the LED*)
tusecs = (adc[[is]]-t0secs)*1000000+ (adc[[ius]] -t0usecs);
framemsecs=(tusecs - t0usecs)/(npoints)/1000.;
(*Print out our result, and then plot the time versus point number, and the data versus time*)
Print["For ",is-1," channels, the frame time is ",framemsecs," ms."];
Close[s];
descriptionname = datename<>".txt";
descriptionlist = {t0secs,t0usecs,adc[[is]],adc[[ius]] ,npoints};
Export[descriptionname,descriptionlist];
Print["8channels2.1.m is complete!"];
Pause[2];
Exit[];










