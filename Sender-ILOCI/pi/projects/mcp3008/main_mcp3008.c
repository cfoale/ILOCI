/*
 * main_mcp3008.c
 * 
 * Copyright 2015  Faero

 */


#include <stdio.h>
#include "gpio.h"
#include "mcp3008.h"  //includes gpio.h, defines GPIO_PATH
#include <unistd.h>	  //defines usleep(int t_in_microseconds)
#include <time.h>  //needed for clock_gettime
#define LED 26  //gpio 26

int main(int argc, char **argv)
{
	exportGPIO(LED);
	exportGPIO(4);
	exportGPIO(27);
	exportGPIO(5);
	exportGPIO(17);
	/* Prints the value of the input "0" of the MCP 3008 */
	if(!gpio_init(LED,"out")){
		printf("Aborting..\n");
		unexportGPIO(LED);
	}
		
	int i=0;
	for(i=0;i<2;i++){
		gpio_write(LED,1);
		usleep(500000);
		gpio_write(LED,0);
		usleep(500000);
	}
		
	int value=0;
	clockid_t clk_id = CLOCK_REALTIME;
	struct timespec tp, start,finish;
	int result = 0;
	result = clock_gettime(clk_id, &tp);
	start.tv_nsec = tp.tv_nsec;
	printf("start at %ld\n", start.tv_nsec);
	int nsamples = 50;
	
	init_mcp3008(4, 27, 5, 17);//sets the directions of the gpio pins
	for(i=0;i<nsamples;i++){ 
		value = mcp3008_value(0, 4, 27, 5, 17);
		printf("value is %d\n", value);
	}
	
	result = clock_gettime(clk_id, &tp);
	finish.tv_nsec = tp.tv_nsec;
	printf("finish at %ld\n", finish.tv_nsec);
	long dt = (finish.tv_nsec - start.tv_nsec);
	double frequency = ((double) nsamples*1000000000)/((double) dt);
	printf("DeltaT  %ld nanosecs at frequency %f Hz\n",dt,frequency);
	//at full speed it seems to give about 144 Hz with debug on, or 140 Hz release code.
	unexportGPIO(LED);
	unexportGPIO(4);
	unexportGPIO(27);
	unexportGPIO(5);
	unexportGPIO(17);
	return 1;


}

