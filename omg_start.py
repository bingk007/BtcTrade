#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  @author: WuBingBing

import threading
import analyze

if __name__ == '__main__':
    print('Start!')
    while True:
        try:
            analyze.Analyze().analyze_data('omgusdt','omg')
        except Exception as ex:
            print(Exception, ":", ex)

