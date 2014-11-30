#!/bin/bash

# send a kill request for the pid in the beat.pid file.  This means, of course, that you need to run this script in the right directory
kill -TERM `cat beat.pid`
