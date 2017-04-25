
#include <mathlink.h>

int addtwo(int i, int j) {
	return i+ j;
}

//NOT used, as requires mcc or mprep
//cc -Wall -o  "%e" "%f" -lML32i4 -lm -lpthread -lrt -lstdc++ -ldl -luuid
//

//USED as build
//mcc addtwo.tm addtwo.c -o addtwo

int main(int argc, char* argv[])
{
	return MLMain(argc, argv);
}
