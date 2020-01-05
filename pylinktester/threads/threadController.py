#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import threading

from . import spliderThread,testThread

# 加把锁，保护共享的变量
g_mutex = threading.Lock()


class threadController:
    '''
    线程管理器，初始化爬虫/检测线程，运行完退出
    '''

    def __init__(self, threadNumber, urlQuence, urlSync, deepth):
        # threadNumber  线程数，
        # urlQuence  爬取的 url 集合;
        # urlSync   同步获取 url 链接
        # deepth 表示层级深度
        global g_mutex
        self.threadNumber = threadNumber
        self.urlQuence = urlQuence
        self.urlSync = urlSync
        self.deepth = deepth
        self.spliderThreadPool = []
        self.testThreadPool = []
        self.mutex = g_mutex

    def start(self):
        for i in range(self.threadNumber):
            self.runSplider()
            if i == 0:  # 第一个爬虫需要爬一些预备链接供之后的爬虫使用
                time.sleep(10)
        # 等待爬虫线程都开启之后再开启测试线程
        for i in range(self.threadNumber * 2):
            self.runTest()

        self.waitUntilEnd()

    def runSplider(self):
        st = spliderThread.spliderThread(self.urlQuence, self.urlSync, self.deepth, self.mutex)
        self.spliderThreadPool.append(st)
        st.start()

    def runTest(self):
        tt = testThread.testThread(self.urlSync, self.spliderThreadPool, self.mutex)
        self.testThreadPool.append(tt)
        tt.start()

    def waitUntilEnd(self):
        for st in self.spliderThreadPool:
            st.join()
            print("spliderThread[%s] 爬取完毕!" % st.getName())
        for tt in self.testThreadPool:
            tt.join()
            print("testThread[%s] 检测完毕!" % tt.getName())
