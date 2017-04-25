#include <stdio.h>


#ifndef GPIO_H_
#define GPIO_H_

int gpio_init(int pin, char *direction) ; // sets the direction of a pin. Allowed values are "in" and "out"
void gpio_write(int pin, int value) ; // sets the output value of the pin. Allowed values are 1 and 0.
int gpio_read(int pin) ; // reads input value from the specified GPIO pin. Returns 1 or 0.
int exportGPIO(int pin);
int unexportGPIO(int pin);
int gpio_init(int pin, char *direction) ; // sets the direction of a pin. Allowed values are "in" and "out"


#endif /* GPIO_H_ */
  
