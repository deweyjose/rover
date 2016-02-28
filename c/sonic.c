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
#include <unistd.h>
#include <syslog.h>
#include <stdlib.h>
#include <stdbool.h>
#include <limits.h>
#include <errno.h>
#include <time.h>
#include <stdint.h>
#include <pthread.h>
#include <wiringPi.h>
#include <hiredis.h>
#include <stdio.h>
#include <gsl/gsl_statistics.h>

// =================================================

#define SPEED_SOUND     17150
#define BILLION         1E9
#define TRIGGER_DELAY   10
#define HISTORY_SIZE    10
#define VARIANCE_LIMIT  5

// =================================================

bool                g_use_syslog    = true;
int                 g_echo          = 0;
int                 g_trigger       = 0;
double              g_min_distance  = 0.0;
double              g_variance_limit= 10.0;
char                g_command[30];

struct timespec     g_start;
struct timespec     g_stop;

double              g_history[HISTORY_SIZE];
int                 g_index         = 0;
int                 g_readings      = 0;

redisContext *      g_context       = NULL;

// =================================================

void read_clock(struct timespec * ts) {
    if (clock_gettime(CLOCK_REALTIME, ts) == -1) {
        syslog(LOG_ERR, "Unable to get realtime clock: %s", strerror(errno)) ;
        exit(EXIT_FAILURE);
    }
}

double calculate_distance(struct timespec * start, struct timespec * stop) {
    double x = (stop->tv_sec - start->tv_sec) + (stop->tv_nsec - start->tv_nsec);
    return (x / BILLION) * SPEED_SOUND;
}

// =================================================

int get_history_index() {
    // if we're at the end restart at the beginning
    if (g_index == HISTORY_SIZE-1) {
        g_index = 0;        
    }
    return g_index++;
}

void dump_statistics(const int count) {
    syslog(LOG_INFO, "The sample mean is %g"        , gsl_stats_mean    (g_history, 1, count));
    syslog(LOG_INFO, "The estimated variance is %g" , gsl_stats_variance(g_history, 1, count));
    syslog(LOG_INFO, "The largest value is %g"      , gsl_stats_max     (g_history, 1, count));
    syslog(LOG_INFO, "The smallest value is %g"     , gsl_stats_min     (g_history, 1, count));    
}

void monitor() {  
    if (digitalRead(g_echo) == 1) {
        read_clock(&g_start);        
    } else {        
        read_clock(&g_stop);
        
        ++g_readings;
        
        double distance = calculate_distance(&g_start, &g_stop);
                
        g_history[get_history_index()] = distance;   
        
        int entries = g_readings >= HISTORY_SIZE ? HISTORY_SIZE-1 : g_index;
        
        double variance = gsl_stats_variance(g_history, 1, entries);
        
        if (rand() % 100 < 1) {
            dump_statistics(entries);
        }
        
        if (distance < g_min_distance) {                
            if (variance >= g_variance_limit) {
                syslog(LOG_WARNING, "ignoring distance %lf, variance %lf > limit %lf", distance, variance, g_variance_limit);            
            } else {
                syslog(LOG_WARNING, "distance %lf, sending %s", distance, g_command);            
                redisCommand(g_context, g_command);                    
            }
        }        
    }    
}

// =================================================

redisContext * rconnect(const char * server, const int port) {
    redisContext * context = redisConnect(server, port);
    if (context != NULL && context->err) {
        syslog(LOG_CRIT, "Error: %s", context->errstr);       
        context = NULL;
    }
    return context;
}

// =================================================

void trigger() {
    digitalWrite(g_trigger, 1); 
    delayMicroseconds(TRIGGER_DELAY);
    digitalWrite(g_trigger, 0);
}

// =================================================

bool setup_wiring_pi() {
    if (wiringPiSetup () < 0) {
        syslog(LOG_CRIT, "Unable to setup wiringPi: %s", strerror(errno));
        return false;
    }
    
    if (wiringPiISR (g_echo, INT_EDGE_BOTH, &monitor) < 0) {
        syslog(LOG_CRIT, "Unable to setup ISR: %s", strerror(errno));
        return false;
    }
    
    pinMode(g_trigger, OUTPUT);
    
    digitalWrite(g_trigger, 0); 
    
    delay(1000);   
    
    if (piHiPri(50) < 0) {
        syslog(LOG_CRIT, "Unable to set priority to 50: %s", strerror(errno));
        return false;
    }    
    
    return true;
}

// =================================================

int main(int argc, char** argv) {            
    char * redis_server     = argv[1];
    int    redis_port       = atoi(argv[2]);
           g_min_distance   = atof(argv[3]);           
    int    trigger_delay    = atoi(argv[4]);
           g_trigger        = atoi(argv[5]);
           g_echo           = atoi(argv[6]); 
    char * command          = argv[7];
           g_variance_limit = atof(argv[8]);
    
    sprintf(g_command, "PUBLISH rover %s", command);       
    
    openlog(NULL, LOG_CONS|LOG_PID, LOG_USER);
    
    syslog(LOG_INFO, "%s:%d, min %lf, delay %d, command %s, trigger %d, echo %d, variance %lf", 
            redis_server, redis_port, g_min_distance, trigger_delay, g_command, g_trigger, g_echo, g_variance_limit);
    
    g_context = rconnect(redis_server, redis_port);
    
    if (!setup_wiring_pi()) { 
        return (EXIT_FAILURE); 
    }
    
    while(true) { 
        trigger(); 
        delay(trigger_delay); 
    }
    
    return (EXIT_SUCCESS);
}
