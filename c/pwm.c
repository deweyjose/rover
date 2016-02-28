/*
 * pwm.c:
 *	This tests the hardware PWM channel.
 *
 * Copyright (c) 2012-2013 Gordon Henderson. <projects@drogon.net>
 ***********************************************************************
 * This file is part of wiringPi:
 *	https://projects.drogon.net/raspberry-pi/wiringpi/
 *
 *    wiringPi is free software: you can redistribute it and/or modify
 *    it under the terms of the GNU Lesser General Public License as published by
 *    the Free Software Foundation, either version 3 of the License, or
 *    (at your option) any later version.
 *
 *    wiringPi is distributed in the hope that it will be useful,
 *    but WITHOUT ANY WARRANTY; without even the implied warranty of
 *    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *    GNU Lesser General Public License for more details.
 *
 *    You should have received a copy of the GNU Lesser General Public License
 *    along with wiringPi.  If not, see <http://www.gnu.org/licenses/>.
 ***********************************************************************
 */

#include <wiringPi.h>

#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

int main (int argc, char * argv[]) {

  printf("Raspberry Pi wiringPi PWM test program\n");

  if (wiringPiSetup() == -1) {
    exit(1) ;
  }

  pinMode (1, PWM_OUTPUT) ;
  pwmSetRange(1024);
  pwmSetClock(400);
  pwmSetMode(0);

  if (argc > 2) {
    int min = atoi(argv[1]);
    int max = atoi(argv[2]);
    int dly = atoi(argv[3]);
    int x = 0;
    for (; x < 2; x++) {
      int i = min;
      for (; i < max; i++) {
	printf("%d\n", i);
	pwmWrite(1, i);
        delay(dly);
      }
      for (; i > min; i--) {
	printf("%d\n", i);
	pwmWrite(1, i);
	delay(dly);
      }
    }
  
    pwmWrite(1, min);
  } else {
    pwmWrite(1, atoi(argv[1]));
  }

  return 0 ;
}
