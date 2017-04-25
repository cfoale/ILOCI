#ifndef MCP3008SPI_H
#include <time.h>  //needed for clock_gettime

    #define MCP3008SPI_H
	void mcp3008Spi(char* devspi, unsigned char spiMode, unsigned int spiSpeed, unsigned char spibitsPerWord);
	int spiOpen(char* devspi);
	int spiClose();
	int spiWriteRead( unsigned char *data, int length);
	int get_mcp3008_channels(int vals[], int nchannels,  struct timespec* ptp);
	
	

#endif
