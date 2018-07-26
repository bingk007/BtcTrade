#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  @author: WuBingBing
import time
import datetime
import re

class Common:

    def get_time(self):
        t_now_new = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        TimeNow = datetime.datetime.strptime(t_now_new, '%Y-%m-%d %H:%M:%S')
        return TimeNow
