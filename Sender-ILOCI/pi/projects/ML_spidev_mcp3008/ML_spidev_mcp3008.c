//Modified by cmf - 5/9/16 for LFI series 2 testing, clock speed adjusted in mcp3008spi.c to provide a
// measurement time of 15 msecs
// the long measurement time (blocking call) is considered one way to reduce measurement
//signal variation greater than 60 Hz . An RC filter will also be used

#include <stdio.h>
#include <unistd.h>	  //defines usleep(int t_in_microseconds)
#include <time.h>  //needed for clock_gettime
#include <stdint.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/spi/spidev.h>
#include "mcp3008Spi.h"
#include <mathlink.h>

//USED as build.  Use mcc -g ...for debugging, launching here first, then Install[linkname] in Mathematia
//mcc ML_spidev_mcp3008.tm ML_spidev_mcp3008.c -o ML_spidev_mcp3008 mcp3008Spi.o -lrt
//mcp3008Spi.o was created in Project spidev_mcp3008, and should be copied to this project folder, and listed as build

#define MCP3008MAXCHANNELS 8

int runmcp3008(int v[], int nv, int* psecs, int* pusecs ){
//NOW RUN SPI ON THE mcp3008	

	struct timespec nanotime;

	int badxfers = 0;
	
	if(spiOpen("/dev/spidev0.0")< 0){
		return -1;
	}

	badxfers=get_mcp3008_channels(v, nv, &nanotime);
	*psecs = nanotime.tv_sec;
	*pusecs = nanotime.tv_nsec/1000;
		
	spiClose();
	
	return badxfers;
}


	
void spidev_mcp3008(int  nchannels, int dt) {
	int nx = nchannels + 2;//we will return the channels and two time values as a list
	int px[nx];
	int i = 0;
	
	if((nchannels < 1) || (nchannels > MCP3008MAXCHANNELS) ) { //we are asking more that mcp3008 can do
		for(i=0;i< nx;i++) px[i] = -1;//-1 is a flag the call had bad arguments
		MLPutIntegerList(stdlink, px, nx);
		return ;
	}
		
	int v[nchannels];
	int secs = 0;
	int usecs = 0;
	
	if(dt==0) {
		runmcp3008(v,nchannels,&secs,&usecs);
	}else{ //wait for elapsed time dt
		usleep(dt);
		runmcp3008(v,nchannels,&secs,&usecs);
	}
	

	for(i=0;i< nchannels;i++){
		px[i] = v[i];
	}
	i = nchannels; //to be sure we are indexed 2 from the end of px
	px[i] = secs;
	i++;
	px[i] = usecs;
	
	MLPutIntegerList(stdlink, px, nx);//list returned has nx elements

}




int main(int argc, char* argv[])
{
	return MLMain(argc, argv);
}

