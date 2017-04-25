/* gpio.c has the functions originally in gpio.h*/

#include "gpio.h"
#include <unistd.h>	  //defines usleep(int t_in_microseconds)

#define GPIO_PATH "/sys/class/gpio/"

const char path[] = "/sys/class/gpio/gpio";
char pinpath[40];

void gpio_write(int pin, int value) { // sets the output value of the pin. Allowed values are 1 and 0.
  sprintf(pinpath, "%s%d/value", path, pin);
  FILE *f;
  f = fopen(pinpath, "w");
  fprintf(f, "%d", value);
  fclose(f);
}

int gpio_read(int pin) { // reads input value from the specified GPIO pin. Returns 1 or 0.
  sprintf(pinpath, "%s%d/value", path, pin);
  FILE *f;
  f = fopen(pinpath, "r");
  int x;
  if ((x = fgetc(f))!=EOF){
    x = (x==49); /* Returns 1 if the input value is HIGH. (fgetc returns 49 when the input value is HIGH). Returns 0 if it is low.
		   */
  }else{
    x = -1;        // -1 is returned when there is an error.
  }
  fclose(f);
  return x;       
}

int exportGPIO(int pin){	
	char gpioexport[40];
	sprintf(gpioexport,"%sexport",GPIO_PATH);
	printf("creating file %s\n",gpioexport);
	
	FILE *f;
	f = fopen(gpioexport, "w");
	if(f==NULL) { 
		printf("Unable to export gpio %d..\n",pin);
		return -1;
	}
	fprintf(f, "%d",pin);
	fclose(f);
	// need to give Linux time to set up the sysfs structure
	usleep(250000); // 250ms delay
	return 0;
}

int unexportGPIO(int pin){
	char gpiounexport[40];
	sprintf(gpiounexport,"%sunexport",GPIO_PATH);
	printf("creating file %s\n",gpiounexport);
	
	FILE *f;
	f = fopen(gpiounexport, "w");
	if(f==NULL) { 
		printf("Unable to unexport gpio %d..\n",pin);
		return -1;
	}
	fprintf(f, "%d",pin);
	fclose(f);
	// need to give Linux time to set up the sysfs structure
	usleep(250000); // 250ms delay
	return 0;
}

int gpio_init(int pin, char *direction) { // sets the direction of a pin. Allowed values are "in" and "out"
  FILE *f;
  sprintf(pinpath, "%s%d/direction", path,  pin);
  f = fopen(pinpath, "w");
  if(f==NULL) { 
		printf("Unable to open %s..\n",pinpath);
		return 0;
  }
  fprintf(f, "%s", direction);
  fclose(f);
  return 1;
}
