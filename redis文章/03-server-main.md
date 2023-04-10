# 三 从server.main再次看redis启动流程

今天呢，我们从整体的角度来看看redis的启动过程，前面两章内容已经将redis启动时重要的过程详细的讲了一遍，现在呢，我们从整体的过程来看看redis的启动。

main函数是程序启动的入口，现在呢，我们一步一步的去分析他，挖掘他。

## 1 变量定义

main函数的前三行

```c
 struct timeval tv;
    int j;
    char config_from_stdin = 0;

```

这段代码定义了一个名为 `tv` 的 `timeval` 结构体变量和一个 `int` 类型的变量 `j`，以及一个 `char` 类型的变量 `config_from_stdin`，初值为 0。

`timeval` 是 C 语言标准库中的一个结构体，表示时间值，由两个成员组成：`tv_sec` 表示秒数，`tv_usec` 表示微秒数。在这段代码中，我们定义了一个 `timeval` 类型的变量 `tv`，通常用于计算时间差和设置超时等场景。

`int` 类型的变量 `j` 可以用于计数，或者存储整数值。

`char` 类型的变量 `config_from_stdin` 用于标记程序是否需要从标准输入读取配置。该变量的初值为 0，表示程序不需要从标准输入读取配置。当该变量的值为 1 时，表示程序需要从标准输入读取配置。

```c
NAME
       timeval - time in seconds and microseconds

LIBRARY
       Standard C library (libc)

SYNOPSIS
       #include <sys/time.h>

       struct timeval {
           time_t       tv_sec;   /* Seconds */
           suseconds_t  tv_usec;  /* Microseconds */
       };

DESCRIPTION
       Describes times in seconds and microseconds.


```

看到这里，你是不是想起前面读取配置的三种方式了，其中是否从终端中读取就在此处定义了。

## 2 预编译指令-条件测试

```c
#ifdef REDIS_TEST
    if (argc >= 3 && !strcasecmp(argv[1], "test")) {
        int flags = 0;
        for (j = 3; j < argc; j++) {
            char *arg = argv[j];
            if (!strcasecmp(arg, "--accurate")) flags |= REDIS_TEST_ACCURATE;
            else if (!strcasecmp(arg, "--large-memory")) flags |= REDIS_TEST_LARGE_MEMORY;
        }

        if (!strcasecmp(argv[2], "all")) {
            int numtests = sizeof(redisTests)/sizeof(struct redisTest);
            for (j = 0; j < numtests; j++) {
                redisTests[j].failed = (redisTests[j].proc(argc,argv,flags) != 0);
            }

            /* Report tests result */
            int failed_num = 0;
            for (j = 0; j < numtests; j++) {
                if (redisTests[j].failed) {
                    failed_num++;
                    printf("[failed] Test - %s\n", redisTests[j].name);
                } else {
                    printf("[ok] Test - %s\n", redisTests[j].name);
                }
            }

            printf("%d tests, %d passed, %d failed\n", numtests,
                   numtests-failed_num, failed_num);

            return failed_num == 0 ? 0 : 1;
        } else {
            redisTestProc *proc = getTestProcByName(argv[2]);
            if (!proc) return -1; /* test not found */
            return proc(argc,argv,flags);
        }

        return 0;
    }
#endif
```



这段代码是一段预编译指令，主要用于判断当前是否处于测试模式下。

`#ifdef` 指令是一个条件编译指令，用于判断某个宏是否已经被定义过。在这里，`REDIS_TEST` 宏是否被定义过将决定 `#ifdef REDIS_TEST` 到 `#endif` 之间的代码段是否需要被编译。

如果 `REDIS_TEST` 宏已经被定义过，则该代码段将被编译。否则，该代码段将被忽略。

条件编译指令常用于编译时针对不同情况进行不同处理，例如调试模式和发布模式下的代码处理不同，或者针对不同平台进行处理等。在 Redis 中，测试模式下的代码与正式发布版本的代码可能存在一些差异，因此需要使用条件编译指令进行区分。

条件测试这个模块我们放到后面进行讲解。

## 3 预编译指令-进程标题

```c
#ifdef INIT_SETPROCTITLE_REPLACEMENT
    spt_init(argc, argv);
#endif
```

在这里，`#ifdef INIT_SETPROCTITLE_REPLACEMENT` 到 `#endif` 之间的代码段将会被编译，如果在编译 Redis 时定义了 `INIT_SETPROCTITLE_REPLACEMENT` 宏。该宏在 Redis 的 Makefile 中定义，用于告知编译器使用一个自定义的进程标题设置函数 `spt_init()`。

进程标题是指进程在操作系统中显示的名称，通常用于标识进程的用途。在 Redis 中，进程标题默认为 Redis 的运行参数（如端口号、工作目录等）的组合，但是在某些情况下（如在服务端部署时），我们可能希望进程标题能够更直观地反映 Redis 的用途，这时可以使用自定义的进程标题设置函数来实现。

`INIT_SETPROCTITLE_REPLACEMENT` 宏的定义与具体实现有关，可以参考 Redis 的源代码和 Makefile 文件来了解。在这里，我们假设该宏定义了一个值为 1 的整数常量，表示需要启用进程标题的自定义设置。如果该宏被定义，那么就会调用 `spt_init()` 函数来初始化进程标题，该函数的参数为 `argc` 和 `argv`，表示命令行参数的数量和内容。

## 4 设置程序本地信息

```c
    setlocale(LC_COLLATE,"");
```

这行代码使用了 C 标准库中的 `setlocale` 函数，用于设置程序的本地化（locale）信息。

`locale` 是一个 C 语言标准库中的概念，用于描述一组与特定地区和语言相关的参数和规则，例如时间格式、货币符号、字符编码等等。程序的本地化信息通常由操作系统决定，但是程序也可以通过调用 `setlocale` 函数来主动设置本地化信息，以便更好地适应不同的用户环境。

在这里，`setlocale` 函数的第一个参数是 `LC_COLLATE`，表示需要设置的本地化分类信息。`LC_COLLATE` 是一个用于排序和比较字符串的本地化分类，用于定义字符排序的规则。当设置 `LC_COLLATE` 为一个空字符串时，表示使用默认的本地化分类信息，这通常是指操作系统的默认设置。

该函数的第二个参数为一个空字符串，表示使用默认的本地化信息。

在 Redis 中，该代码的作用是设置程序的本地化信息，以便更好地适应不同的语言和地区。这在 Redis 中尤其重要，因为 Redis 是一个全球性的软件，需要支持不同的语言和字符编码。

该函数接受两个参数，分别是本地化分类信息 `category` 和需要设置的本地化信息 `locale`。`category` 表示需要设置的本地化分类信息，它可以是以下常量之一：

![](D:\桌面\note\redis文章\images\setlocale.png)

```c
#include <locale.h>

char *setlocale(int category, const char *locale);
```

- `LC_ALL`：表示设置所有本地化分类信息。
- `LC_COLLATE`：表示设置字符排序和比较的本地化分类信息。
- `LC_CTYPE`：表示设置字符分类和转换的本地化分类信息。
- `LC_MONETARY`：表示设置货币格式的本地化分类信息。
- `LC_NUMERIC`：表示设置数字格式的本地化分类信息。
- `LC_TIME`：表示设置时间格式的本地化分类信息。

`locale` 表示需要设置的本地化信息，它的格式通常是一个字符串，用于指定语言、地区、字符编码等信息。例如，`"en_US.UTF-8"` 表示英语语言、美国地区、UTF-8 编码。

`setlocale` 函数返回一个字符串指针，指向当前的本地化信息字符串。如果设置本地化信息成功，返回值将与第二个参数 `locale` 相同，否则返回一个空指针。

在程序中调用 `setlocale` 函数可以设置本地化信息，以便更好地适应不同的语言和地区。例如，如果程序需要处理多语言的用户界面，就可以根据用户的语言偏好来设置本地化信息，以便正确地显示日期、时间、货币符号等内容。

## 5 初始化时区信息

```c
tzset(); /* Populates 'timezone' global. */.
```

`tzset()` 函数是 C 标准库中的一个函数，用于初始化时区信息。

在 Unix/Linux 系统中，时间和时区是密切相关的。当系统初始化时，需要读取环境变量 `TZ`，以确定当前所在时区。`tzset()` 函数的作用就是根据 `TZ` 环境变量的值来设置时区信息，并将相应的信息保存到全局变量 `timezone` 和 `daylight` 中。

`timezone` 是一个整型变量，表示当前时区与 UTC（协调世界时）的时差，以秒为单位。如果当前时区比 UTC 早，那么 `timezone` 将是一个正值；如果当前时区比 UTC 晚，那么 `timezone` 将是一个负值。

`daylight` 是一个布尔型变量，表示当前时区是否使用夏令时。如果当前时区使用夏令时，那么 `daylight` 的值为非零（通常为 1）；否则 `daylight` 的值为零。

在调用 `tzset()` 函数之后，程序就可以通过访问全局变量 `timezone` 和 `daylight` 来获取当前的时区信息了。需要注意的是，`tzset()` 函数只需要在程序启动时调用一次即可，通常不需要重复调用。

## 6 内存分配失败回调函数

```c
zmalloc_set_oom_handler(redisOutOfMemoryHandler);
void redisOutOfMemoryHandler(size_t allocation_size) {
    serverLog(LL_WARNING,"Out Of Memory allocating %zu bytes!",
        allocation_size);
    serverPanic("Redis aborting for OUT OF MEMORY. Allocating %zu bytes!",
        allocation_size);
}
```

`zmalloc_set_oom_handler` 函数是 Redis 中一个用于处理内存分配失败的回调函数，它用于设置内存分配失败时的处理函数。

在 Redis 中，内存分配失败时会调用 `zmalloc` 函数，如果分配失败，就会触发 Redis 的 out of memory (OOM) 事件。默认情况下，Redis 的 OOM 事件处理方式是直接调用 `exit(1)` 函数，退出 Redis 进程。但是，如果你希望在发生内存分配失败时执行一些特定的操作，例如记录日志或者释放一些资源，就可以使用 `zmalloc_set_oom_handler` 函数来设置自定义的处理函数。

例如，`zmalloc_set_oom_handler(redisOutOfMemoryHandler)` 的作用是将 `redisOutOfMemoryHandler` 函数注册为 Redis 内存分配失败时的处理函数。如果 Redis 在内存分配时遇到问题，将会自动调用该处理函数，并执行其中的逻辑。这样，你就可以在 Redis 发生内存分配失败时进行特定的操作了。

```c
static void (*zmalloc_oom_handler)(size_t) = zmalloc_default_oom;
static void zmalloc_default_oom(size_t size) {
    fprintf(stderr, "zmalloc: Out of memory trying to allocate %zu bytes\n",
        size);
    fflush(stderr);
    abort();
}
```

```c
void zmalloc_set_oom_handler(void (*oom_handler)(size_t)) {
    zmalloc_oom_handler = oom_handler;
}
```

Redis 实现在内存分配失败时能够执行错误处理函数的关键在于两个方面：

1. 使用了 `zmalloc` 函数库作为 Redis 的内存分配器：Redis 使用 `zmalloc` 作为内存分配器而不是 C 语言标准库中的 `malloc` 函数。`zmalloc` 函数库是一个基于 `malloc` 的封装，它在 `malloc` 的基础上添加了一些特性，例如内存分配跟踪、内存对齐等。同时，`zmalloc` 还提供了 `zmalloc_set_oom_handler` 函数，它能够让开发者注册一个函数，当 Redis 在内存分配失败时会调用该函数。
2. 在 `zmalloc` 函数库中，重写了 `malloc` 和 `free` 函数：`zmalloc` 函数库重写了 C 语言标准库中的 `malloc` 和 `free` 函数，以实现自己的内存分配器。在 `zmalloc` 中，重写的 `malloc` 函数在内存分配失败时不是返回 NULL，而是调用了错误处理函数。而且在 `zmalloc` 中还提供了一个 `zmalloc_oom` 函数，**它会触发 Redis 的 OOM 事件，这个事件将会使 Redis 执行错误处理函数**。

因此，当 Redis 在分配内存时发现内存不足，就会调用错误处理函数。这个错误处理函数可以是开发者自己编写的、记录错误日志、尝试释放内存或者其他操作，以确保 Redis 不会因为内存不足而崩溃。

在 `zmalloc` 函数库中，重写的 `malloc` 函数被称为 `zmalloc` 函数，它是 Redis 中用于分配内存的函数。

`zmalloc` 函数与标准的 `malloc` 函数非常相似，但有一些区别。主要区别如下：

1. `zmalloc` **函数会对分配的内存进行额外的跟踪和处理**，例如记录分配的内存大小和地址，内存对齐等。
2. **`zmalloc` 函数会在分配内存时检查是否有足够的内存可用，如果没有足够的内存，它会调用 Redis 的错误处理函数，而不是返回 NULL**。
3. `zmalloc` 函数会维护一个内存池，用于提高分配和释放内存的效率。
4. `zmalloc` 函数还提供了其他一些功能，例如重置内存池、获取内存池的统计信息等。

因此，通过使用 `zmalloc` 函数库，Redis 能够更好地控制内存的分配和释放，并且在内存分配失败时能够执行错误处理函数。

```c
void *zmalloc(size_t size) {
    void *ptr = ztrymalloc_usable(size, NULL);
    if (!ptr) zmalloc_oom_handler(size);
    return ptr;
}
```

这段代码是 Redis 中的 `zmalloc` 函数的实现。它的主要作用是分配一块指定大小的内存，并返回一个指向该内存块的指针。

具体来说，`zmalloc` 函数首先调用 `ztrymalloc_usable` 函数尝试分配指定大小的内存。如果分配成功，则直接返回指向该内存块的指针。如果分配失败，则调用 `zmalloc_oom_handler` 函数来处理内存不足的情况。

`zmalloc_oom_handler` 函数是 Redis 中的内存不足处理函数。它的主要作用是执行一些错误处理操作，例如打印错误消息、释放一些已分配的内存等。这样可以确保 Redis 不会在内存不足的情况下崩溃，而是能够优雅地处理该问题。

总之，`zmalloc` 函数是 Redis 中用于分配内存的核心函数之一，它确保了 Redis 在分配内存时的安全性和可靠性。

## 7 初始化随机数发生器

```c
  	gettimeofday(&tv,NULL);
    srand(time(NULL)^getpid()^tv.tv_usec);
    srandom(time(NULL)^getpid()^tv.tv_usec);
    init_genrand64(((long long) tv.tv_sec * 1000000 + tv.tv_usec) ^ getpid());
    crc64_init();
```

这段代码主要用于初始化随机数发生器。具体来说，它执行以下操作：

1. 调用 `gettimeofday` 函数获取当前时间，并存储到 `tv` 结构体中。
2. 使用当前进程的进程 ID、时间戳、以及微秒数作为种子，通过 `srand` 和 `srandom` 函数初始化随机数发生器。
3. 调用 `init_genrand64` 函数，使用当前时间的秒数和微秒数、以及进程 ID 作为种子，初始化一个 64 位随机数发生器。
4. 调用 `crc64_init` 函数初始化 CRC64 校验表。

**这些操作的目的是为了在 Redis 运行期间产生各种随机数，以及在需要进行校验和计算时使用 CRC64 校验表。这样可以增加 Redis 的安全性和可靠性，确保 Redis 在各种情况下都能正常运行。**

## 8 设置文件权限

```c
 umask(server.umask = umask(0777));
```

`umask` 函数用于设置当前进程的文件创建屏蔽字。在 Redis 中，该语句的作用是将当前进程的文件创建屏蔽字设置为 `0777`，并将返回值赋值给 `server.umask` 变量。

`umask` 函数的作用是屏蔽掉进程的某些权限，比如读、写、执行等权限，使其不能被文件创建系统调用所继承。例如，如果文件创建屏蔽字设置为 `022`，则表示屏蔽掉组和其他用户的写权限，使得创建的文件默认权限为 `-rw-r--r--`。

在 Redis 中，通过将文件创建屏蔽字设置为 `0777`，可以确保 Redis 在创建文件时不会受到任何限制，这对于一些需要频繁创建和操作文件的场景非常重要，比如 AOF 持久化和 RDB 持久化等。

## 9 哈希种子

```c
  	uint8_t hashseed[16];
    getRandomBytes(hashseed,sizeof(hashseed));
    dictSetHashFunctionSeed(hashseed)
```

在这段代码中，Redis 使用 `getRandomBytes` 函数生成一个 16 字节的随机字节数组 `hashseed`，然后将其作为种子调用 `dictSetHashFunctionSeed` 函数，设置哈希函数的种子。哈希函数的种子是一个常量，它影响到哈希函数的散列结果，用于减少哈希冲突，提高哈希表的效率。

在 Redis 中，哈希表被广泛用于实现各种数据结构，如字典、集合、有序集合等，哈希函数的性能对于 Redis 的性能有很大的影响。为了防止哈希碰撞，Redis 在启动时生成一个随机的种子，并将其用作哈希函数的种子。这样，即使在同一组键值对中，如果键的散列值相同，那么哈希函数也会以不同的方式处理这些键值对，减少哈希碰撞的可能性，提高 Redis 的性能。

## 10 检测哨兵模式

```c
 	char *exec_name = strrchr(argv[0], '/');
    if (exec_name == NULL) exec_name = argv[0];
    server.sentinel_mode = checkForSentinelMode(argc,argv, exec_name);
  
```

1. 通过 `strrchr()` 函数获取程序名 `argv[0]` 中最后一个 `/` 字符之后的字符串（即程序名），并将其保存到 `exec_name` 变量中。
2. 如果程序名中没有 `/` 字符，说明 `argv[0]` 本身就是程序名，将其直接保存到 `exec_name` 变量中。
3. 调用 `checkForSentinelMode()` 函数检查是否以 Sentinel 模式运行，并将检查结果保存到 `server.sentinel_mode` 变量中。

```c
int checkForSentinelMode(int argc, char **argv, char *exec_name) {
    if (strstr(exec_name,"redis-sentinel") != NULL) return 1;

    for (int j = 1; j < argc; j++)
        if (!strcmp(argv[j],"--sentinel")) return 1;
    return 0;
}
```

具体实现是，首先根据参数`argv[0]`中的可执行文件名（不包括路径）判断是否以redis-sentinel命名，如果是，返回1；否则，遍历命令行参数`argv`，如果发现"--sentinel"参数，返回1，否则返回0。

## 11 初始化服务器配置

```c
initServerConfig();
```



熟悉吧，这就是我们前两章讲得配置文件,在这里我就不详细描述了，简单的概述一下

`initServerConfig()`是Redis中用来初始化服务器配置结构体的函数。在该函数中，会将服务器配置结构体的各个成员变量设置为默认值，然后根据启动参数以及配置文件的设置修改这些默认值。

具体来说，该函数会先将所有的配置项都设置为默认值，然后读取`redis.conf`配置文件中的配置项，如果启动参数中存在与配置文件中相同的配置项，则以启动参数中的值为准。最后，根据`sentinel_mode`变量的值来决定是否进行哨兵模式下的配置。

## 12 ACL权限控制模块

```c
ACLInit()
```

`ACLInit()`函数是Redis中用来初始化ACL权限控制模块的函数。在该函数中，会初始化一些数据结构，以支持后续的ACL操作。

具体来说，该函数会初始化一个全局的ACL权限列表，以及多个用于ACL操作的数据结构，如命令表（command table）、用户表（user table）、角色表（role table）等。在初始化过程中，该函数会从配置文件中读取默认的ACL规则，并将其加入到全局的ACL权限列表中。同时，该函数还会将`defaultUser`用户和`defaultPassword`密码设置为默认的登录凭据，以便在没有指定具体凭据的情况下，使用这些凭据进行登录。

这一块具体的代码还是比较复杂的，在后续中，我会详细的为大家进行讲解。

## 13 Redis初始化模块系统

```c
moduleInitModulesSystem();
```

`moduleInitModulesSystem()` 是 Redis 5.0 引入的新函数，它的作用是初始化 Redis 的模块系统。

Redis 模块系统允许开发者通过动态加载模块，扩展 Redis 的功能。模块系统允许开发者通过 Redis 提供的 API 进行模块开发，同时模块也可以在 Redis 运行时加载、卸载，而无需停止 Redis 服务。

`moduleInitModulesSystem()` 函数在 Redis 启动时被调用，用于初始化模块系统。这个函数会在 Redis 的服务器状态中创建一个模块列表，然后遍历加载所有已经在 Redis 配置文件中配置的模块。

如果开发者希望编写自己的 Redis 模块，可以通过调用 Redis 模块 API 进行编写，并将编写好的模块编译成动态库文件。在 Redis 启动时，将这些动态库文件加载到 Redis 的模块系统中，就可以在 Redis 中使用自己编写的模块。

## 14 TLS层初始化

```c
  tlsInit();
```

`tlsInit()`函数是Redis服务器TLS（传输层安全性）支持的一部分。它在服务器初始化期间调用，用于设置TLS上下文。

在以下是TLS初始化的步骤概述：

1. 调用OpenSSL库的初始化函数`SSL_library_init()`和`OpenSSL_add_all_algorithms()`，以初始化和加载OpenSSL支持库。
2. 调用`SSL_CTX_new()`函数创建一个新的TLS上下文对象，该对象用于TLS连接的创建和配置。
3. 调用`SSL_CTX_set_ecdh_auto()`函数以启用自动选择椭圆曲线密钥交换算法，这是一种更安全的方式来生成加密密钥。
4. 调用`SSL_CTX_set_session_cache_mode()`函数启用TLS会话缓存，以提高TLS连接的性能。
5. 调用`SSL_CTX_set_verify()`函数设置TLS连接的验证模式，可以配置为验证服务器证书或客户端证书，或者不进行证书验证。
6. 调用`SSL_CTX_use_certificate_chain_file()`和`SSL_CTX_use_PrivateKey_file()`函数加载服务器证书和私钥，以便使用TLS进行加密通信。
7. 调用`SSL_CTX_set_cipher_list()`函数设置TLS连接支持的加密算法列表，以确保TLS连接的安全性。
8. 最后，为了提供更好的性能和安全性，Redis使用`setsockopt()`函数启用TCP Fast Open（TFO）特性，这将允许连接更快地建立。

通过以上步骤，`tlsInit()`函数初始化了Redis服务器的TLS支持，并为加密通信创建了安全的TLS上下文。