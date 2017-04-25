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


//GEANY BUILD LINE - remove -g for release
//gcc -Wall -g -o "%e" "%f" mcp3008Spi.o -lrt
	
int main(int argc, char **argv)
{
	
	//NOW RUN SPI ON THE mcp3008	

	struct timespec tp, start, nanotime;
	
	int nsamples = 100000;//statistical number of calls to get frequency
	int v[8];
	int i;
	long usecs = 0;
	long nsecs = 0;
	int secs = 0;
	int badxfers = 0;
	
	
	if(spiOpen("/dev/spidev0.0")< 0){
		return -1;
	}
	
	clock_gettime(CLOCK_REALTIME, &tp);
	start.tv_nsec = tp.tv_nsec;
	start.tv_sec = tp.tv_sec;
	
	for(i=0;i<nsamples;i++){ 
		badxfers=get_mcp3008_channels(v, 8, &nanotime);
		if(badxfers) printf("There were %d bad SPI transfer requests before getting data..\n", badxfers);
		secs = (nanotime.tv_sec - start.tv_sec );
		nsecs = (nanotime.tv_nsec -start.tv_nsec) ;
		usecs = nsecs/1000 + 1000000*secs;
		printf("%ld %d %d %d %d %d %d %d %d\n",usecs, v[0],v[1],v[2],v[3],v[4],v[5],v[6],v[7]);
	}
	
	double frequency = ((double) nsamples*1000000)/((double) usecs);
	//error in display of usecs now corrected to adjust for nsamples - cmf -5/9/16
	printf("DeltaT  %ld usecs at frequency %f Hz\n",usecs/nsamples ,frequency);
	//printf("%d %d %d %d %d %d %d %d\n",v[0],v[1],v[2],v[3],v[4],v[5],v[6],v[7]);
	
	spiClose();
	
	return 0;
}

