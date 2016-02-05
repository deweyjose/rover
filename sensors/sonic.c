/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

/* 
 * File:   sonic.c
 * Author: dewey
 *
 * Created on January 27, 2016, 9:53 PM
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <limits.h>
#include <errno.h>
#include <time.h>
#include <stdint.h>
#include <pthread.h>
#include <wiringPi.h>
#include <hiredis.h>

// =================================================

#define SPEED_SOUND     17150
#define BILLION         1E9
#define TRIGGER_DELAY   10

// =================================================

int                 g_echo         = 0;
int                 g_trigger      = 0;
int                 g_violations   = 0;
int                 g_filter_count = 0;
double              g_min_distance = 0.0;
bool                g_up           = false;
char                g_direction[30];
char                g_command[30];
struct timespec     g_start;
struct timespec     g_stop;
pthread_mutex_t     g_lock;
redisContext *      g_context      = NULL;

// =================================================

void read_clock(struct timespec * ts) {
    if (clock_gettime(CLOCK_REALTIME, ts) == -1) {
        fprintf(stderr, "Unable to get realtime clock: %s\n", strerror (errno)) ;
        exit(EXIT_FAILURE);
    }
}

double calculate_distance(struct timespec * start, struct timespec * stop) {
    double x = (stop->tv_sec - start->tv_sec) + (stop->tv_nsec - start->tv_nsec);
    return (x / BILLION) * SPEED_SOUND;
}

bool valid_distance(double distance) {
    return distance > 0 && distance < 1000;
}

// =================================================

void trigger() {
    digitalWrite(g_trigger, 1); 
    delayMicroseconds(TRIGGER_DELAY);
    digitalWrite(g_trigger, 0);
}

// =================================================

void monitor() {  
    if (digitalRead(g_echo) == 1) {
        read_clock(&g_start);
        g_up = true;
    } else {
        if (g_up) {
            read_clock(&g_stop);
            double distance = calculate_distance(&g_start, &g_stop);
            if (valid_distance(distance)) {
                if (distance < g_min_distance) {
                    g_violations++;
                    if (g_violations > g_filter_count) {
                        if (rand() % 100 < 10) {
                            fprintf(stderr, "%d violations. distance %lf, sending %s\n", g_violations, distance, g_command);
                        }
                        char buffer[30];
                        sprintf(buffer, "PUBLISH rover %s", g_command);
                        redisCommand(g_context, buffer);
                        g_violations = 0;
                    }
                } else {
                    g_violations = 0;
                }
            }
        }
        
        g_up = false;     
    }    
}

// =================================================

redisContext * rconnect(const char * server, const int port) {
    redisContext * context = redisConnect(server, port);
    if (context != NULL && context->err) {
        printf("Error: %s\n", context->errstr);       
        context = NULL;
    }
    return context;
}

// =================================================

bool setup_wiring_pi() {
    if (wiringPiSetup () < 0) {
        fprintf(stderr, "Unable to setup wiringPi: %s\n", strerror(errno));
        return false;
    }
    
    if (wiringPiISR (g_echo, INT_EDGE_BOTH, &monitor) < 0) {
        fprintf(stderr, "Unable to setup ISR: %s\n", strerror(errno));
        return false;
    }
    
    pinMode(g_trigger, OUTPUT);
    
    digitalWrite(g_trigger, 0); 
    
    delay(1000);   
    
    if (piHiPri(50) < 0) {
        fprintf(stderr, "Unable to set priority to 50: %s\n", strerror(errno));
        return false;
    }    
    
    return true;
}

// =================================================

void usage() {
    printf("usage:   sonic <redis ip> <redis port> <min> <max> <filter count> <reading delay>\n");
    printf("example: sonic 127.0.0.1 6379 2.2 55.5 5 15\n");
}

// =================================================

int main(int argc, char** argv) {        
    if (argc != 9) {
        usage();
        return (EXIT_FAILURE);
    }
    
    char * redis_server   = argv[1];
    int    redis_port     = atoi(argv[2]);
           g_min_distance = atof(argv[3]);
           g_filter_count = atoi(argv[4]);
    int    reading_delay  = atoi(argv[5]);
           g_trigger      = atoi(argv[6]);
           g_echo         = atoi(argv[7]); 
           g_up           = false;
           
           sprintf(g_direction, "%s", argv[8]);
           sprintf(g_command, "stop_%s", g_direction);
           
    printf("%s:%d, min %lf, filter %d, delay %d, direction %s, trigger %d, echo %d\n", 
            redis_server, redis_port, g_min_distance, g_filter_count, reading_delay, g_direction, g_trigger, g_echo);
    
    g_context = rconnect(redis_server, redis_port);
    
    if (!setup_wiring_pi()) {
        return (EXIT_FAILURE);
    }        
    
    if (pthread_mutex_init(&g_lock, NULL) != 0){
        printf("mutex init failed\n");
        return false;
    }     
    
    while(true) { 
        trigger(); 
        delay(reading_delay);       
    }
    
    return (EXIT_SUCCESS);
}

