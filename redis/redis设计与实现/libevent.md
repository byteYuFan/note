# libevent

## 1.Libevent的地基-event_base

在使用libevent的函数之前，需要先申请一个或event_base结构，相当于盖房子时的地基。在event_base基础上会有一个事件集合，可以检测哪个事件是激活的（就绪）。

通常情况下可以通过event_base_new函数获得event_base结构。

```c
     struct event_base *event_base_new(void);
```

申请到event_base结构指针可以通过event_base_free进行释放。

  ```c
     void event_base_free(struct event_base *)
  ```



如果fork出子进程，想在子进程继续使用event_base，那么子进程需要对event_base重新初始化，函数如下：

```c
int event_reinit(struct event_base *base);
```

**对于不同系统而言，event_base就是调用不同的多路IO接口去判断事件是否已经被激活，对于linux系统而言，核心调用的就是epoll，同时支持poll和select。**

## 2.等待事件产生-循环等待event_loop      

Libevent在地基打好之后，需要等待事件的产生，也就是等待想要等待的事件的激活，那么程序不能退出，对于epoll来说，我们需要自己控制循环，而在libevent中也给我们提供了api接口，类似where(1)的功能.函数如下：

```c
int event_base_loop(struct event_base *base, int flags);
```

flags的取值：

```c
只触发一次，如果事件没有被触发，阻塞等待
#define EVLOOP_ONCE	0x01
```

```c
非阻塞方式检测事件是否被触发，不管事件触发与否，都会立即返回
#define EVLOOP_NONBLOCK	0x02
```

而大多数我们都调用libevent给我们提供的另外一个api：

```c
int event_base_dispatch(struct event_base *base);
```

调用该函数，相当于没有设置标志位的event_base_loop。程序将会一直运行，直到没有需要检测的事件了，或者被结束循环的api终止。

```c
int event_base_loopexit(struct event_base *base, const struct timeval *tv);
	int event_base_loopbreak(struct event_base *base);
struct timeval {
	long    tv_sec;                    
	long    tv_usec;   
}
```

两个函数的区别是如果正在执行激活事件的回调函数，那么event_base_loopexit将在事件回调执行结束后终止循环（如果tv时间非NULL，那么将等待tv设置的时间后立即结束循环），而event_base_loopbreak会立即终止循环

### 3.事件驱动-event

事件驱动实际上是libevent的核心思想，本小节主要介绍基本的事件event。

主要的状态转化：

![img](file:///D:/系统缓存/msohtmlclip1/01/clip_image002.jpg)