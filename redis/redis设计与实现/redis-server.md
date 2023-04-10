# redis-server

## server.h

### 1 client

```c
typedef struct client {
    uint64_t id;            /* Client incremental unique ID. */
    uint64_t flags;         /* Client flags: CLIENT_* macros. */
    connection *conn;
    int resp;               /* RESP protocol version. Can be 2 or 3. */
    redisDb *db;            /* Pointer to currently SELECTed DB. */
    robj *name;             /* As set by CLIENT SETNAME. */
    sds querybuf;           /* Buffer we use to accumulate client queries. */
    size_t qb_pos;          /* The position we have read in querybuf. */
    size_t querybuf_peak;   /* Recent (100ms or more) peak of querybuf size. */
    int argc;               /* Num of arguments of current command. */
    robj **argv;            /* Arguments of current command. */
    int argv_len;           /* Size of argv array (may be more than argc) */
    int original_argc;      /* Num of arguments of original command if arguments were rewritten. */
    robj **original_argv;   /* Arguments of original command if arguments were rewritten. */
    size_t argv_len_sum;    /* Sum of lengths of objects in argv list. */
    struct redisCommand *cmd, *lastcmd;  /* Last command executed. */
    struct redisCommand *realcmd; /* The original command that was executed by the client,
                                     Used to update error stats in case the c->cmd was modified
                                     during the command invocation (like on GEOADD for example). */
    user *user;             /* User associated with this connection. If the
                               user is set to NULL the connection can do
                               anything (admin). */
    int reqtype;            /* Request protocol type: PROTO_REQ_* */
    int multibulklen;       /* Number of multi bulk arguments left to read. */
    long bulklen;           /* Length of bulk argument in multi bulk request. */
    list *reply;            /* List of reply objects to send to the client. */
    unsigned long long reply_bytes; /* Tot bytes of objects in reply list. */
    list *deferred_reply_errors;    /* Used for module thread safe contexts. */
    size_t sentlen;         /* Amount of bytes already sent in the current
                               buffer or object being sent. */
    time_t ctime;           /* Client creation time. */
    long duration;          /* Current command duration. Used for measuring latency of blocking/non-blocking cmds */
    int slot;               /* The slot the client is executing against. Set to -1 if no slot is being used */
    dictEntry *cur_script;  /* Cached pointer to the dictEntry of the script being executed. */
    time_t lastinteraction; /* Time of the last interaction, used for timeout */
    time_t obuf_soft_limit_reached_time;
    int authenticated;      /* Needed when the default user requires auth. */
    int replstate;          /* Replication state if this is a slave. */
    int repl_start_cmd_stream_on_ack; /* Install slave write handler on first ACK. */
    int repldbfd;           /* Replication DB file descriptor. */
    off_t repldboff;        /* Replication DB file offset. */
    off_t repldbsize;       /* Replication DB file size. */
    sds replpreamble;       /* Replication DB preamble. */
    long long read_reploff; /* Read replication offset if this is a master. */
    long long reploff;      /* Applied replication offset if this is a master. */
    long long repl_applied; /* Applied replication data count in querybuf, if this is a replica. */
    long long repl_ack_off; /* Replication ack offset, if this is a slave. */
    long long repl_ack_time;/* Replication ack time, if this is a slave. */
    long long repl_last_partial_write; /* The last time the server did a partial write from the RDB child pipe to this replica  */
    long long psync_initial_offset; /* FULLRESYNC reply offset other slaves
                                       copying this slave output buffer
                                       should use. */
    char replid[CONFIG_RUN_ID_SIZE+1]; /* Master replication ID (if master). */
    int slave_listening_port; /* As configured with: REPLCONF listening-port */
    char *slave_addr;       /* Optionally given by REPLCONF ip-address */
    int slave_capa;         /* Slave capabilities: SLAVE_CAPA_* bitwise OR. */
    int slave_req;          /* Slave requirements: SLAVE_REQ_* */
    multiState mstate;      /* MULTI/EXEC state */
    int btype;              /* Type of blocking op if CLIENT_BLOCKED. */
    blockingState bpop;     /* blocking state */
    long long woff;         /* Last write global replication offset. */
    list *watched_keys;     /* Keys WATCHED for MULTI/EXEC CAS */
    dict *pubsub_channels;  /* channels a client is interested in (SUBSCRIBE) */
    list *pubsub_patterns;  /* patterns a client is interested in (SUBSCRIBE) */
    dict *pubsubshard_channels;  /* shard level channels a client is interested in (SSUBSCRIBE) */
    sds peerid;             /* Cached peer ID. */
    sds sockname;           /* Cached connection target address. */
    listNode *client_list_node; /* list node in client list */
    listNode *postponed_list_node; /* list node within the postponed list */
    listNode *pending_read_list_node; /* list node in clients pending read list */
    RedisModuleUserChangedFunc auth_callback; /* Module callback to execute
                                               * when the authenticated user
                                               * changes. */
    void *auth_callback_privdata; /* Private data that is passed when the auth
                                   * changed callback is executed. Opaque for
                                   * Redis Core. */
    void *auth_module;      /* The module that owns the callback, which is used
                             * to disconnect the client if the module is
                             * unloaded for cleanup. Opaque for Redis Core.*/

    /* If this client is in tracking mode and this field is non zero,
     * invalidation messages for keys fetched by this client will be send to
     * the specified client ID. */
    uint64_t client_tracking_redirection;
    rax *client_tracking_prefixes; /* A dictionary of prefixes we are already
                                      subscribed to in BCAST mode, in the
                                      context of client side caching. */
    /* In updateClientMemoryUsage() we track the memory usage of
     * each client and add it to the sum of all the clients of a given type,
     * however we need to remember what was the old contribution of each
     * client, and in which category the client was, in order to remove it
     * before adding it the new value. */
    size_t last_memory_usage;
    int last_memory_type;

    listNode *mem_usage_bucket_node;
    clientMemUsageBucket *mem_usage_bucket;

    listNode *ref_repl_buf_node; /* Referenced node of replication buffer blocks,
                                  * see the definition of replBufBlock. */
    size_t ref_block_pos;        /* Access position of referenced buffer block,
                                  * i.e. the next offset to send. */

    /* Response buffer */
    size_t buf_peak; /* Peak used size of buffer in last 5 sec interval. */
    mstime_t buf_peak_last_reset_time; /* keeps the last time the buffer peak value was reset */
    int bufpos;
    size_t buf_usable_size; /* Usable size of buffer. */
    char *buf;
} client;

```

1. `fd`：客户端套接字文件描述符。
2. `name`：客户端名字，由客户端自己指定。如果客户端没有指定，那么就会被设置为格式为`ip:port`的字符串。
3. `db`：客户端当前正在使用的数据库。
4. `querybuf`：输入缓冲区，用于保存客户端发送来的命令请求。
5. `querybuf_peak`：输入缓冲区曾经达到过的峰值大小。
6. `reqtype`：当前正在处理的请求类型。
7. `reqid`：当前请求的ID。Redis支持多个命令可以在同一时间处理（比如pipelining），这个ID可以用于区分不同的命令。
8. `argc`：当前请求中参数的数量。
9. `argv`：当前请求中参数的数组，每个元素都是一个`robj`对象。
10. `cmd`：指向当前正在执行的命令对象。
11. `lastcmd`：指向最近一次执行的命令对象。
12. `cflags`：客户端标志位，包含了一些关于客户端的状态信息。
13. `authenticated`：表示这个客户端是否已通过认证。
14. `peerid`：如果这个客户端是一个主节点的从节点，那么这个字段表示它所属的主节点的ID。
15. `pending_write_bytes`：等待发送给客户端的缓冲区大小。
16. `reply_bytes`：等待发送给客户端的回复缓冲区大小。
17. `bufpos`：回复缓冲区中待发送内容的起始位置。
18. `obuf_soft_limit_reached_time`：当回复缓冲区大小超过软性限制时，Redis会记录一个时间戳。
19. `watched_keys`：一个链表，保存着客户端正在监视的键空间。
20. `pubsub_patterns`：一个链表，保存着客户端正在订阅的频道和模式。
21. `peer_addr`：客户端的地址信息。
22. `resp`：客户端的回复缓冲区，用于保存命令执行的返回结果。

### 2 user

```c
typedef struct {
    sds name;       /* The username as an SDS string. */
    uint32_t flags; /* See USER_FLAG_* */
    list *passwords; /* A list of SDS valid passwords for this user. */
    list *selectors; /* A list of selectors this user validates commands
                        against. This list will always contain at least
                        one selector for backwards compatibility. */
    robj *acl_string; /* cached string represent of ACLs */
} user;
```

`user` 结构体表示一个 Redis 用户，具体字段解释如下：

- `name`：用户名，使用 sds 字符串表示。
- flag用户的一些属性标识，包括以下值：
  1. `USER_FLAG_ENABLED`：用户是否启用。
  2. `USER_FLAG_ALLCOMMANDS`：用户是否可以执行所有命令。
  3. `USER_FLAG_NOPASS`：用户是否不需要密码验证。
  4. `USER_FLAG_ALLKEYS`：用户是否可以访问所有键。
  5. `USER_FLAG_ALLCHANNELS`：用户是否可以访问所有频道。
  6. `USER_FLAG_NOROOT`：用户是否不是 root 用户。
- `passwords`：一个包含 SDS 字符串的列表，表示此用户可以使用的密码。
- `selectors`：一个包含 Redis 命令所属的命名空间的列表，表示此用户有权访问的命名空间。
- `acl_string`：一个缓存的 ACL 字符串表示形式，可以用于向客户端显示 ACL 配置信息。

### 3 RedisDB

```c
typedef struct redisDb {
    dict *dict;                 /* The keyspace for this DB */
    dict *expires;              /* Timeout of keys with a timeout set */
    dict *blocking_keys;        /* Keys with clients waiting for data (BLPOP)*/
    dict *ready_keys;           /* Blocked keys that received a PUSH */
    dict *watched_keys;         /* WATCHED keys for MULTI/EXEC CAS */
    int id;                     /* Database ID */
    long long avg_ttl;          /* Average TTL, just for stats */
    unsigned long expires_cursor; /* Cursor of the active expire cycle. */
    list *defrag_later;         /* List of key names to attempt to defrag one by one, gradually. */
    clusterSlotToKeyMapping *slots_to_keys; /* Array of slots to keys. Only used in cluster mode (db 0). */
} redisDb;
```

它包含了一个 Redis 数据库中所有的键值对数据，以及一些跟这些键值对有关的元信息。具体来说，这个结构体包含了以下字段：

- `dict`：一个字典，用于存储键值对数据。
- `expires`：一个字典，存储有过期时间的键值对的过期时间信息。
- `blocking_keys`：一个字典，存储正在阻塞等待数据的客户端对应的键。
- `ready_keys`：一个字典，存储已经等待了一段时间后被推送数据的键。
- `watched_keys`：一个字典，存储在多个客户端的事务中被 WATCH 命令监视的键。
- `id`：一个整数，表示该数据库的编号。
- `avg_ttl`：一个长整型数值，表示数据库中所有带过期时间的键的平均 TTL 时间。
- `expires_cursor`：一个无符号长整型数值，表示数据库中所有带过期时间的键的过期时间信息的游标。
- `defrag_later`：一个链表，存储需要逐个进行碎片整理的键名。
- `slots_to_keys`：一个数组，存储了集群模式下，当前数据库中的槽位与键的对应关系。