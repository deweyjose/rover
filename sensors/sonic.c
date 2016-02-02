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

#define TRIGGER_FRONT   4
#define TRIGGER_REAR    7

#define ECHO_FRONT      5
#define ECHO_REAR       6

#define STOP_FORWARD    "stop_forward";
#define STOP_REVERSE    "stop_reverse";

// =================================================

struct monitorspec {
    const char *    command;
    int             trigger;
    int             echo;
    struct timespec start;
    struct timespec stop;
    int             violations;
    pthread_mutex_t lock;
    void *          func;
};

// =================================================

struct monitorspec  g_front;
struct monitorspec  g_rear;

double              g_min_distance = 0.0;
int                 g_filter_count = 0;
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
    return distance > 2 && distance < 400;
}

// =================================================

void trigger(struct monitorspec * spec) {
    digitalWrite(spec->trigger, 1); 
    delayMicroseconds(TRIGGER_DELAY);
    digitalWrite(spec->trigger, 0);
}

// =================================================

void monitor(struct monitorspec * spec) {    
    if (digitalRead(spec->echo) == 1) {
        read_clock(&spec->start);                       
    } else {        
        read_clock(&spec->stop);       
        double distance = calculate_distance(&spec->start, &spec->stop);
        if (valid_distance(distance)) {
            pthread_mutex_lock(&spec->lock);
            if (distance < g_min_distance) {
                spec->violations++;
                if (spec->violations > g_filter_count) {                    
                    fprintf(stderr, "%d violations. distance %lf, sending %s\n", spec->violations, distance, spec->command);
                    char buffer[30];
                    sprintf(buffer, "PUBLISH rover %s", spec->command);
                    redisCommand(g_context, buffer);
                    spec->violations = 0;
                }
            } else {
                spec->violations = 0;
            }
            pthread_mutex_unlock(&spec->lock);
        }
    }
}

void monitor_front(void) {    
    monitor(&g_front);
}

void monitor_rear(void) {    
    monitor(&g_rear);    
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
    
    if (piHiPri(50) < 0) {
        fprintf(stderr, "Unable to set priority to 50: %s\n", strerror(errno));
        return false;
    }    
    
    return true;
}

// =================================================

bool initialize_monitorspec(struct monitorspec * spec, int trigger, int echo) {
    if (pthread_mutex_init(&spec->lock, NULL) != 0){
        printf("mutex init failed\n");
        return false;
    }
    spec->trigger = trigger;
    spec->echo    = echo;
    
    pinMode(spec->trigger, OUTPUT);
    
    if (wiringPiISR (spec->echo, INT_EDGE_BOTH, spec->func) < 0) {
        fprintf(stderr, "Unable to setup ISR: %s\n", strerror(errno));
        return false;
    }
    
    digitalWrite(spec->trigger, 0); delay(1000);
    
    return true;
}

// =================================================

void usage() {
    printf("usage:   sonic <redis ip> <redis port> <min> <max> <filter count> <reading delay>\n");
    printf("example: sonic 127.0.0.1 6379 2.2 55.5 5 15\n");
}

// =================================================

int main(int argc, char** argv) {        
    if (argc != 6) {
        usage();
        return (EXIT_FAILURE);
    }
    
    char * redis_server   = argv[1];
    int    redis_port     = atoi(argv[2]);
           g_min_distance = atof(argv[3]);
           g_filter_count = atoi(argv[4]);
    int    reading_delay  = atoi(argv[5]);
      
    printf("%s:%d, min %lf, filter %d, delay %d\n", redis_server, redis_port, g_min_distance, g_filter_count, reading_delay);
    
    g_context = rconnect(redis_server, redis_port);
    
    if (!setup_wiring_pi()) {
        return (EXIT_FAILURE);
    }        
    
    g_front.func = monitor_front;
    g_rear .func = monitor_rear;
    
    g_front.command = STOP_FORWARD;
    g_rear .command = STOP_REVERSE;
    
    if (!initialize_monitorspec(&g_front, TRIGGER_FRONT, ECHO_FRONT)) { return (EXIT_FAILURE); }
    if (!initialize_monitorspec(&g_rear , TRIGGER_REAR , ECHO_REAR )) { return (EXIT_FAILURE); }
    
    while(true) { 
        trigger(&g_front); 
        trigger(&g_rear); 
        delay(reading_delay);
    }
    
    return (EXIT_SUCCESS);
}

