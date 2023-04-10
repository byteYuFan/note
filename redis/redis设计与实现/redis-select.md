## redis-select

ae_select.c文件实现了 Redis 的事件驱动框架的 IO 多路复用部分，其中使用了 select 系统调用来监听多个文件描述符的 IO 事件。具体来说，该文件实现了以下功能：

1. 封装了 select 系统调用，使其具有可读性和可维护性，提供了类 Unix epoll API 的接口，如 aeCreateFileEvent，aeDeleteFileEvent，aeGetFileEvents 等。
2. 提供了一个简单的时间事件处理器，用于处理定时任务。
3. 使用链表实现了文件事件和时间事件的管理，其中每个事件均由一个 aeFileEvent 结构体来表示。
4. 根据不同操作系统的特点，使用了不同的技巧提高 select 系统调用的效率。

总之，ae_select.c 文件是 Redis 事件驱动框架中重要的组成部分，是实现 IO 多路复用的核心模块之一。

## 1 redis事件驱动框架

Redis使用了一个基于事件驱动的框架，称为"==an event-driven I/O library=="，或简称"ae"（"an event library"）。**Redis的事件驱动框架使用了与操作系统提供的I/O复用机制相同的函数，比如`select()`、`poll()`、`epoll()`等**。

Redis的事件驱动框架被封装在`ae.c`和`ae.h`两个文件中。其中，`ae.c`包含了事件驱动框架的具体实现，而`ae.h`包含了相应的头文件和API定义。

Redis的事件驱动框架基于事件循环（event loop）模型，使用一个主循环来监听各种事件（文件描述符、定时器等），并调用相应的处理函数来处理这些事件。事件循环的主要流程如下：

1. 创建一个事件处理器（event loop），并初始化相应的数据结构。
2. 注册事件处理器要监听的文件描述符、定时器等事件。
3. 进入事件循环，等待事件的发生。
4. 当事件发生时，调用相应的事件处理函数来处理事件。
5. 处理完事件后，继续等待下一个事件的发生。

Redis的事件驱动框架提供了一些常用的事件处理函数，如`aeCreateFileEvent()`、`aeCreateTimeEvent()`、`aeDeleteFileEvent()`、`aeDeleteTimeEvent()`等，这些函数可以用于注册和删除文件描述符、定时器等事件。Redis还提供了一些辅助函数，如`aeGetFileEvents()`、`aeMain()`等，用于获取当前正在监听的事件、启动事件循环等。

通过使用事件驱动框架，Redis可以高效地处理大量的并发请求，同时提供了灵活的定时器、延迟任务等功能，保证了Redis的高可用性和可扩展性。

### 2 结构体

```c
typedef struct aeApiState {
    fd_set rfds, wfds;
    /* We need to have a copy of the fd sets as it's not safe to reuse
     * FD sets after select(). */
    fd_set _rfds, _wfds;
} aeApiState;
```

这是 Redis 事件驱动框架中与底层 I/O 多路复用机制相关的结构体定义之一。其中，`aeApiState` 结构体用于封装底层的多路复用机制，它包含以下几个成员：

- `fd_set rfds`：读文件描述符集合，用于存放待检测是否可读的文件描述符。
- `fd_set wfds`：写文件描述符集合，用于存放待检测是否可写的文件描述符。
- `fd_set _rfds`：`rfds` 的备份，**用于在 `select()` 系统调用之前进行数据备份**，避免在 `select()` 返回之后修改了 `rfds` 集合，造成数据混乱。
- `fd_set _wfds`：`wfds` 的备份，与 `_rfds` 相同作用。

其中，`fd_set` 是一个数据结构，通常是一个`	位向量`，在 Linux 系统下被定义为 `__kernel_fd_set` 类型。它的每一位表示一个文件描述符，位为 1 表示该文件描述符可以进行指定的 I/O 操作，否则为 0。通过这些文件描述符集合，`aeApiState` 结构体可以实现对文件描述符的异步监控，及时发现并处理事件。

### 3  aeApiCreate

```c
static int aeApiCreate(aeEventLoop *eventLoop) {
    aeApiState *state = zmalloc(sizeof(aeApiState));

    if (!state) return -1;
    FD_ZERO(&state->rfds);
    FD_ZERO(&state->wfds);
    eventLoop->apidata = state;
    return 0;
}
```

这是 Redis 事件驱动框架中的一个函数，用于在底层创建一个新的 IO 多路复用状态实例并初始化它。这个函数会创建一个 `aeApiState` 结构体实例，并将 `eventLoop` 的 `apidata` 属性指向这个结构体实例。

在 `aeApiCreate` 函数中，首先使用 `zmalloc` 函数为 `aeApiState` 结构体实例分配内存。然后，通过 `FD_ZERO` 函数将 `state` 结构体实例中的 `rfds` 和 `wfds` 属性初始化为一个空的文件描述符集合。最后，将 `eventLoop` 的 `apidata` 属性指向这个 `state` 实例。

此函数的返回值为 0 表示成功创建并初始化 IO 多路复用状态实例，返回 -1 则表示创建失败。

### 4aeApiResize

```c
static int aeApiResize(aeEventLoop *eventLoop, int setsize) {
    AE_NOTUSED(eventLoop);
    /* Just ensure we have enough room in the fd_set type. */
    if (setsize >= FD_SETSIZE) return -1;
    return 0;
}

static void aeApiFree(aeEventLoop *eventLoop) {
    zfree(eventLoop->apidata);
}
```

这个函数是在 event loop 调整 setsize（最大连接数）时被调用的。因为 fd_set 类型有大小限制，最大只能为 FD_SETSIZE，因此这个函数主要是确保 setsize 不超过这个限制。如果超过了，返回 -1，否则返回 0。这里 AE_NOTUSED 宏是一个空宏定义，用于标记这个参数没有被使用。

### 5 aeApiAddEven

```c
static int aeApiAddEvent(aeEventLoop *eventLoop, int fd, int mask) {
    aeApiState *state = eventLoop->apidata;

    if (mask & AE_READABLE) FD_SET(fd,&state->rfds);
    if (mask & AE_WRITABLE) FD_SET(fd,&state->wfds);
    return 0;
}
```

这段代码实现了向事件驱动框架中添加一个新的事件。参数`fd`表示待添加事件所对应的文件描述符，参数`mask`表示待添加事件的类型，可以是`AE_READABLE`、`AE_WRITABLE`、`AE_READABLE | AE_WRITABLE`之一，分别对应可读事件、可写事件、可读可写事件。

在函数内部，首先获取到事件驱动框架的`apidata`成员，这个成员是框架实现的API状态。然后根据`mask`参数将文件描述符添加到对应的`rfds`或`wfds`集合中，以便在下一次事件循环中检测到该文件描述符上的事件。最后返回0表示添加事件成功。

### 6  aeApiDelEvent

```c
static void aeApiDelEvent(aeEventLoop *eventLoop, int fd, int mask) {
    aeApiState *state = eventLoop->apidata;

    if (mask & AE_READABLE) FD_CLR(fd,&state->rfds);
    if (mask & AE_WRITABLE) FD_CLR(fd,&state->wfds);
}
```

`aeApiDelEvent`函数用于删除指定文件描述符上的指定事件。

首先，它通过访问 `eventLoop` 中的 `apidata` 字段获取到 `aeApiState` 结构体指针 `state`。

然后，根据传入的参数 `mask` 中包含的事件类型，从 `state->rfds` 或 `state->wfds` 中移除对应的文件描述符。这里使用 `FD_CLR` 宏实现。

注意，如果删除的事件在下一次事件循环前被重新添加，则它将不会被删除。

### 7 aeApiPoll

`aeApiPoll` 是 Redis 事件驱动框架中使用 `select` 函数实现的 IO 多路复用函数。以下是函数的实现代码

```c
static int aeApiPoll(aeEventLoop *eventLoop, struct timeval *tvp) {
    aeApiState *state = eventLoop->apidata;
    int retval, j, numevents = 0;

    memcpy(&state->_rfds,&state->rfds,sizeof(fd_set));
    memcpy(&state->_wfds,&state->wfds,sizeof(fd_set));

    retval = select(eventLoop->maxfd+1,
                &state->_rfds,&state->_wfds,NULL,tvp);
    if (retval > 0) {
        for (j = 0; j <= eventLoop->maxfd; j++) {
            int mask = 0;
            aeFileEvent *fe = &eventLoop->events[j];

            if (fe->mask == AE_NONE) continue;
            if (fe->mask & AE_READABLE && FD_ISSET(j,&state->_rfds))
                mask |= AE_READABLE;
            if (fe->mask & AE_WRITABLE && FD_ISSET(j,&state->_wfds))
                mask |= AE_WRITABLE;
            eventLoop->fired[numevents].fd = j;
            eventLoop->fired[numevents].mask = mask;
            numevents++;
        }
    } else if (retval == -1 && errno != EINTR) {
        panic("aeApiPoll: select, %s", strerror(errno));
    }

    return numevents;
}
```

该函数会先将事件循环中记录的待监听文件描述符的 `fd_set` 拷贝到 `_rfds` 和 `_wfds` 中，然后调用 `select` 函数进行等待。在 `select` 函数返回后，函数会遍历事件循环中的所有文件事件，查看它们是否已经准备好，如果准备好了，则将其放到就绪文件事件数组中。最后函数返回就绪的文件事件个数。

### 8 *aeApiName

```c
static char *aeApiName(void) {
    return "select";
}

```

