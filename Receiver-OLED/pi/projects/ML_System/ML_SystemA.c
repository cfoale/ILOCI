
#include <stdio.h>
#include <string.h>
#include <unistd.h>	  //defines usleep(int t_in_microseconds)
#include <time.h>  //needed for clock_gettime
#include <stdint.h>
#include <fcntl.h>
#include <stdlib.h>  // used by system("  ")

#include <mathlink.h>

//USED as build.  Use mcc -g ...for debugging, launching here first, then Install[linkname] in Mathematia
//mcc ML_spidev_mcp3008.tm ML_spidev_mcp3008.c -o ML_spidev_mcp3008 -lrt

#define RFCOMMINIT	0
#define CONNECT 	1
#define LISTEN 		2
#define HANGUP		3
#define SHOW		4

extern int toggleSP = 22 ; //global variable which holds last 

int rfcomm(int ncmd){
	FILE *in;
	extern FILE *popen();
	char buff[1024];
	//int ret=0;
	char* pnt = NULL;
	
	//choose what we are to do based on ncmd
	switch(ncmd){
		case RFCOMMINIT :
		//sudo hciconfig hci0 reset
			if(!(in = popen("sudo hciconfig hci0 piscan", "r"))){
			//printf("Unable to open popen\n");
			return -1;
			}
			while(fgets(buff, sizeof(buff), in)!=NULL){
				//printf("%s", buff);
			}
			usleep(1000000);//give the system a chance to do i dont know what...
			if(toggleSP== 22){
				if(!(in = popen("sudo sdptool add --channel=22 SP", "r"))){
					return -1;
				}
			}else{
				if(!(in = popen("sudo sdptool add --channel=21 SP", "r"))){
					return -1;
				}
			}
			while(fgets(buff, sizeof(buff), in)!=NULL){
				//printf("%s", buff);
			}
			usleep(1000000);
			break;
		
		case CONNECT :
			if(!(in = popen("sudo rfcomm connect /dev/rfcomm0 &", "r"))){
				//printf("Unable to open popen\n");
				return -1;
			}
	
			while(fgets(buff, sizeof(buff), in)!=NULL){
				//printf("%s", buff);
			}
			
			break;
		
		case LISTEN :
			if(toggleSP== 22){
				if(!(in = popen("sudo rfcomm listen /dev/rfcomm0 22 &", "r"))){
					return -1;
				}
			}else{
				if(!(in = popen("sudo rfcomm listen /dev/rfcomm0 21 &", "r"))){
					return -1;
				}
			}
			
	
			while(fgets(buff, sizeof(buff), in)!=NULL){
				//printf("%s", buff);
			}
					
			break;
			
		case HANGUP	:
			if(!(in = popen("sudo rfcomm release /dev/rfcomm0 &", "r"))){
			//printf("Unable to open popen\n");
			return -1;
			}
			usleep(1000000);
			while(fgets(buff, sizeof(buff), in)!=NULL){
				//printf("%s", buff);
			}
			//now toggle the serial port to be used next time
			if(toggleSP==22){
				toggleSP = 21;
			}else{
				toggleSP = 22;
			}
			break;
			
		case SHOW	:
			if(!(in = popen("rfcomm show /dev/rfcomm0", "r"))){
			//printf("Unable to open popen\n");
			return -1;
			}
	
			while(fgets(buff, sizeof(buff), in)!=NULL){
				//printf("%s", buff);
			}
			pnt = strstr(buff,"conn");
			if(pnt==NULL){
				return 0;
			}else{
				return 1;
			}
			break;
		default :
		
			return -1; //did not find a corresponding action
		
	}
	
	pclose(in);
	
	//MLPutByteString(stdlink,buff,sizeof(buff));
	return ncmd;
	
}

int main(int argc, char* argv[])
{
	return MLMain(argc, argv);
}

