//mcp3008Spi.c
//Modified by cmf - for LFI series 2 testing, clock speed adjusted to provide a measurement time of 15 msecs
// the long measurement time (blocking call) might be desirable to reduce measurement signal variation greater than 60 Hz
/***********************************************************************
 * This header file contains the mcp3008Spi class definition.
 * Its main purpose is to communicate with the MCP3008 chip using
 * the userspace spidev facility.
 * The code contains four global variables:
 * mode        -> defines the SPI mode used. In our case it is SPI_MODE_0.
 * bitsPerWord -> defines the bit width of the data transmitted.
 *        This is normally 8. Experimentation with other values
 *        didn't work for me
 * speed       -> Bus speed or SPI clock frequency. According to
 *                https://projects.drogon.net/understanding-spi-on-the-raspberry-pi/
 *            It can be only 0.5, 1, 2, 4, 8, 16, 32 MHz.
 *                Will use 1MHz for now and test it further.
 * spifd       -> file descriptor for the SPI device
 *
 * The spiOpen initialize the above
 * variables and then open the appropriate spidev device .
 * 
 * The spiWriteRead() function sends the data "data" of length "length"
 * to the spidevice and at the same time receives data of the same length.
 * Resulting data is stored in the "data" variable after the function call.*/

#include <stdio.h>
#include <string.h>  //memset uses this
#include <unistd.h>	  //defines usleep(int t_in_microseconds)
#include <time.h>  //needed for clock_gettime
#include <fcntl.h>  //used by IOCTRL open device
#include <sys/ioctl.h>  //required by spidev
#include <linux/spi/spidev.h>
#include "mcp3008Spi.h"



/*************************************************
 * spiOpen() initializes these..
 * ***********************************************/
//global variables
	unsigned char mode;
    unsigned char bitsPerWord;
    unsigned int speed;
    int spifd;
    int usleepdelay;
    
   
   
/**********************************************************
 * spiOpen() :function is called by the main program
 * It is responsible for opening the spidev device
 * "devspi" and then setting up the spidev interface.
 * global variables are used to configure spidev.
 * They must be set appropriately in
 * this function.
 * *********************************************************/
int spiOpen(char* devspi){
	mode = SPI_MODE_0 ;
    bitsPerWord = 8;
    //Series 2 LIFI requires a low sample rate of 2-4 Hz.
    //10KHz is the recommended minimum MCP3008 clock rate.
    //1MHz divided by 2^6 = 64 gives 15625 Hz, which is greater than 10Khz.
    speed = 15625; // For LIFI Series1 it was 1 MHz seems to give good accuracy, and is fast
    spifd = -1;
    usleepdelay = 1*1000000/speed; // a constant I used to space out spiWriteRead calls, which were failing.  zeroize spi[] fixed this

    int statusVal = -1;
    spifd = open(devspi, O_RDWR);
    if(spifd < 0){
        printf("could not open SPI device\n");
        return(0);
    }

    statusVal = ioctl (spifd, SPI_IOC_WR_MODE, &mode);
    if(statusVal < 0){
        printf("Could not set SPIMode (WR)...ioctl fail\n");
        return(0);
    }

    statusVal = ioctl (spifd, SPI_IOC_RD_MODE, &mode);
    if(statusVal < 0) {
      printf("Could not set SPIMode (RD)...ioctl fail\n");
      return 0;;
    }

    statusVal = ioctl (spifd, SPI_IOC_WR_BITS_PER_WORD, &bitsPerWord);
    if(statusVal < 0) {
      printf("Could not set SPI bitsPerWord (WR)...ioctl fail\n");
      return 0;
    }

    statusVal = ioctl (spifd, SPI_IOC_RD_BITS_PER_WORD, &bitsPerWord);
    if(statusVal < 0) {
      printf("Could not set SPI bitsPerWord(RD)...ioctl fail\n");
      return 0;
    }

    statusVal = ioctl (spifd, SPI_IOC_WR_MAX_SPEED_HZ, &speed);
    if(statusVal < 0) {
      printf("Could not set SPI speed (WR)...ioctl fail");
      return 0;
    }

    statusVal = ioctl (spifd, SPI_IOC_RD_MAX_SPEED_HZ, &speed);
    if(statusVal < 0) {
      printf("Could not set SPI speed (RD)...ioctl fail\n");
      return 0;
    }
    usleep(usleepdelay);
    return statusVal;
}

/***********************************************************
 * spiClose(): Responsible for closing the spidev interface.
 * *********************************************************/

int spiClose(){
    int statusVal = -1;
    statusVal = close(spifd);
        if(statusVal < 0) {
      printf("Could not close SPI device\n");
      return statusVal;
    }

    return statusVal;
}


 
    
/********************************************************************
 * This function writes data "data" of length "length" to the spidev
 * device. Data shifted in from the spidev device is saved back into
 * "data".
 * ******************************************************************/
int spiWriteRead( unsigned char *data, int length){

  struct spi_ioc_transfer spi[length];
  int i = 0;
  int retVal = -1;

// one spi transfer for each byte

/*This is the definition of the spi_transfer structure found in kernel.org
struct spi_transfer {
  const void * tx_buf;
  void * rx_buf;
  unsigned len;
  dma_addr_t tx_dma;
  dma_addr_t rx_dma;
  struct sg_table tx_sg;
  struct sg_table rx_sg;
  unsigned cs_change:1;
  unsigned tx_nbits:3;
  unsigned rx_nbits:3;
#define SPI_NBITS_SINGLE	0x01
#define SPI_NBITS_DUAL		0x02
#define SPI_NBITS_QUAD		0x04
  u8 bits_per_word;
  u16 delay_usecs;
  u32 speed_hz;
  struct list_head transfer_list;
};  
*/

	//CMF added this... it fixed lots of random errors..
	memset(spi,0,sizeof(spi));  //CRITICAL !!!documentation says zeroize everything you dont use
	
  for (i = 0 ; i < length ; i++){
    spi[i].tx_buf        = (unsigned long)(data + i); // transmit from "data"
    spi[i].rx_buf        = (unsigned long)(data + i) ; // receive into "data"
    spi[i].len           = sizeof(*(data + i)) ;
    spi[i].delay_usecs   =  0; //microseconds to delay after this transfer before (optionally) changing the chipselect status, then starting the next transfer or completing this spi_message. 
    spi[i].speed_hz      = speed ;
    spi[i].bits_per_word = bitsPerWord ;
    spi[i].cs_change = 0;  //affects chipselect after this transfer completes 
  }

 retVal = ioctl (spifd, SPI_IOC_MESSAGE(length), &spi) ;

 if(retVal < 0){
    perror("Problem transmitting spi data..ioctl\n");
    return retVal;
 }

return retVal;

}


//This is the way to get data passed to the a2dVal array, using nchannels.  Nano time is placed into the ptp structure
//If the SPI is some how not working well, losing bytes, then bad transfers result.
int get_mcp3008_channels(int a2dVal[], int nchannels, struct timespec* ptp){
    unsigned char a2dChannel = 0;
    unsigned char data[3];
    unsigned char byte0, byte2,chbyte;
    byte0 = 1;  //  first byte transmitted -> start bit
    byte2 = 0; // third byte transmitted....don't care
    int gooddata = 0;
    int badtransfers = 0;
    
    for(a2dChannel=0; a2dChannel < nchannels; a2dChannel++){
		chbyte = 0b10000000 |( ((a2dChannel & 7) << 4)); // second byte transmitted -> (SGL/DIF = 1, D2=D1=D0=0)
		gooddata = 0;
		while(!gooddata){
			data[0] = byte0;  //  first byte transmitted -> start bit
			data[1] = chbyte;
			data[2] = byte2; //dont care
			if(spiWriteRead(data, sizeof(data) ) > 0) 
				gooddata = 1;
			else
				badtransfers++;
			//usleep(usleepdelay); //I was using this when I had bad xfers on the first call to spiWriteRead.  initial zeroizing spi[] structure fixed this.
		}
		a2dVal[a2dChannel] = 0;
		a2dVal[a2dChannel]  = (data[1]<< 8) & 0b1100000000; //merge data[1] & data[2] to get result
		a2dVal[a2dChannel]  |=  (data[2] & 0xff);
		//printf("We got good data: %d\n",  a2dVal[a2dChannel] );
	}
	clock_gettime(CLOCK_REALTIME, ptp);
	//if(badtransfers > 0) printf("Bad xfers %d\n",  badtransfers );
	return badtransfers;
}

