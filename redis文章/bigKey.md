# Redis-BigKEY

## 1. 什么是BigKEY

查看[阿里云Redis开发规范](https://developer.aliyun.com/article/531067)，我们可以得知BigKEY是这样定义的：

在Redis中，一个字符串最大512MB，一个二级数据结构（例如hash、list、set、zset）可以存储大约40亿个(2^32-1)个元素，但实际上中如果下面两种情况，我就会认为它是bigkey。

1. 字符串类型：它的big体现在单个value值很大，一般认为超过10KB就是bigkey。
2. 非字符串类型：哈希、列表、集合、有序集合，它们的big体现在元素个数太多（不要超过5000）。

## 2. BigKEY的危害

### 2.1. 内存空间不均匀

假设有一个Redis集群，由多个节点组成，每个节点都负责存储和处理一部分数据。集群中的数据会根据一致性哈希算法进行分片和分配。

现在假设集群中的某个节点（Node A）存储了一个大型键值对，它占用了大量的内存空间。由于这个大型键值对的存在，Node A的内存使用率很高，可能接近或达到了内存的上限。

当集群中的其他节点（Node B、Node C等）需要执行写入操作时，根据一致性哈希算法，这些写入操作会被路由到Node A。由于Node A的内存已经几乎耗尽，它可能无法存储新的数据。

在这种情况下，可能会发生以下问题：

1. 写入失败：当集群中的其他节点无法将数据写入Node A时，写入操作会失败。这可能导致数据丢失或客户端的写入请求被拒绝。
2. 数据不一致：由于集群中的不同节点存储了不同的数据，当其中一个节点无法存储新的数据时，数据的一致性可能会受到影响。一些节点可能具有更新的数据，而另一些节点可能具有旧的数据，导致数据不一致的状态。
3. 集群负载不均衡：由于大型键值对的存在，导致部分节点的内存使用率高于其他节点。这可能导致集群的负载不均衡，某些节点承载了更多的请求和数据负担，而其他节点相对空闲。

### 2.2. 超时阻塞

当一个Redis实例中存在一个非常大的字符串值时，例如一个键的值是一个几百兆甚至几个G的字符串，这个大型键值对的读写操作可能会导致阻塞问题。

假设有一个Redis键名为"large_value"，其对应的字符串值非常大。现在有一个写操作需要更新这个键的值，同时有多个读操作需要获取该键的值。

以下是一个示例的代码片段，模拟了这种情况：

```python
package main

import (
	"context"
	"fmt"
	"github.com/redis/go-redis/v9"
	"strings"
	"sync"
)

var rdb = redis.NewClient(&redis.Options{
	Addr:     "localhost:6379",
	Password: "",
	DB:       0,
})
var ctx = context.Background()

func init() {
	if err := rdb.Ping(ctx).Err(); err != nil {
		panic(err)
	}
}
func main() {
	// 创建一个 WaitGroup 用于等待所有操作完成
	var wg sync.WaitGroup

	// 创建一个 Goroutine 执行写操作
	wg.Add(1)
	go writeOperation(&wg)

	// 创建多个 Goroutine 执行读操作
	for i := 0; i < 5; i++ {
		wg.Add(1)
		go readOperation(&wg)
	}

	// 等待所有操作完成
	wg.Wait()

	// 关闭 Redis 连接
	err := rdb.Close()
	if err != nil {
		fmt.Println("Failed to close Redis connection:", err)
	}
}

// writeOperation 向redis写
func writeOperation(wg *sync.WaitGroup) {
	defer wg.Done()
	largeValue := generateLargeValue(100000000)
	err := rdb.Set(ctx, "large_key", largeValue, 0).Err()
	if err != nil {
		fmt.Println("Write operation failed:", err)
		return
	}
	fmt.Println("Write operation completed.")
}

// readOperation 读操作函数，获取大型键值对的值
func readOperation(wg *sync.WaitGroup) {
	defer wg.Done()
	value, err := rdb.Get(ctx, "large_key").Result()
	if err != nil {
		fmt.Println("Read operation failed:", err)
		return
	}
	fmt.Println("Read operation completed. Value length:", len(value))
}

// generateLargeValue 生成较大的字符串值
func generateLargeValue(size int) string {
	return strings.Repeat("X", size)
}
```

```shell

127.0.0.1:6379> MEMORY USAGE large_key
(integer) 100663352
127.0.0.1:6379> get large_key
```

我们查看redis发现该键确实挺大的哈，所以假如你现在使用了get命令，咳咳咳~~

```shell
Read operation failed: read tcp 192.168.197.1:52937->192.168.197.129:6379: i/o timeout
Write operation failed: write tcp 192.168.197.1:52939->192.168.197.129:6379: i/o timeout
Read operation failed: read tcp 192.168.197.1:52941->192.168.197.129:6379: i/o timeout
Read operation failed: read tcp 192.168.197.1:52938->192.168.197.129:6379: i/o timeout
Read operation failed: read tcp 192.168.197.1:52940->192.168.197.129:6379: i/o timeout
Read operation failed: read tcp 192.168.197.1:52942->192.168.197.129:6379: i/o timeout
```

这是上面代码运行的结果，结果发现都超时阻塞了。

### 2.3. 网络拥塞

假设有一个名为"big_key"的键，它存储的值大小为1MB。现有一个具有1000个客户端并发访问的场景，每个客户端每秒钟都需要获取"big_key"的值。这样就会导致每秒钟产生1000MB的网络流量。

对于普通的千兆网卡（1 Gbps）的服务器来说，其理论上的最大传输速率为125MB/s。然而，考虑到其他网络负载、操作系统和硬件的开销，实际可用的带宽可能会更低。

在这种情况下，每秒钟产生1000MB的网络流量超出了服务器网络带宽的限制。这将导致网络拥塞和性能下降，甚至可能导致其他服务受到影响。

此外，如果服务器采用单机多实例的方式进行部署，意味着多个实例共享相同的网络带宽和硬件资源。当一个实例的客户端大量访问"big_key"时，网络流量的增加可能会对其他实例产生影响，降低它们的性能和响应能力。

这种情况下的后果可能包括：

- 网络拥塞和延迟增加：大量的网络流量超出了服务器网络带宽的限制，导致网络拥塞，影响其他网络通信和响应时间。
- 响应时间延长：由于服务器负载过高，无法及时处理客户端的请求，导致响应时间延长。
- 服务不可用：如果服务器无法处理大量的请求和流量，可能会导致服务不可用，甚至崩溃。

因此，对于大型键值对（bigkey），特别是在高并发访问的场景下，需要谨慎设计和管理，以避免对网络带宽和服务器性能产生过大的压力。多实例的方式来部署，也就是说一个bigkey可能会对其他实例造成影响，其后果不堪设想。

### 2.4.  过期删除

当一个大键（bigkey）在 Redis 中设置了过期时间，并且没有启用 Redis 4.0 引入的过期异步删除（lazyfree-lazy-expire yes）选项时，会存在阻塞 Redis 的风险。

在 Redis 中，过期键的删除是通过内部的循环事件来处理的。当键过期时，Redis 会在适当的时间点检查并删除过期键。这个过期删除操作是在 Redis 的主线程中执行的，因此会阻塞主线程的执行，导致其他操作无法得到及时响应。

以下是这种情况的详细说明：

1. 设置过期时间：使用 Redis 的命令（如 `SET`）设置键的过期时间，例如 `EXPIRE key_name seconds`。
2. 内部循环事件：Redis 会周期性地检查过期键并删除它们。这个过期删除操作是在 Redis 主线程中顺序执行的，即一个接一个地检查每个键的过期时间并删除过期的键。
3. 阻塞 Redis 主线程：当有大量的键需要过期删除时，如果这些键的删除操作耗时较长，就会阻塞 Redis 主线程的执行。这意味着主线程无法及时处理其他请求和操作，导致响应延迟增加。

### 2.5. 迁移困难

在对大键（bigkey）进行迁移时，使用 Redis 的 `MIGRATE` 命令可能会面临一些问题。 `MIGRATE` 命令实际上是通过组合使用 `DUMP`、`RESTORE` 和 `DEL` 命令来完成数据迁移的原子操作。以下是关于大键迁移可能遇到的问题：

1. 迁移失败：由于大键的数据量较大，进行 `DUMP` 操作可能会消耗大量的时间和内存资源。如果在迁移过程中发生网络故障或迁移操作超时，可能导致迁移失败并丢失部分数据。此外，如果目标实例上的内存不足以容纳大键的数据，也会导致迁移失败。
2. 阻塞 Redis：大键的迁移通常需要较长的时间，这会导致执行 `MIGRATE` 命令的 Redis 实例在迁移过程中被阻塞。这会影响其他请求和操作的响应时间，并可能导致客户端的阻塞和性能下降。

## 3. BigKEY产生原因

1. 社交类：粉丝列表 在社交应用中，粉丝列表是一个常见的大键示例。当明星或大V的粉丝数量庞大时，粉丝列表的大小可能会快速增长，成为一个 bigkey。这样的 bigkey 可能会影响读取和更新操作的性能，因为它需要处理大量的数据。对于这种情况，可以考虑采用分页加载、按需加载或使用其他技术手段来优化数据访问和管理。
2. 统计类：按天存储用户集合 在统计功能或网站中，按天存储用户集合也可能导致 bigkey。例如，每天将用户的相关数据存储在 Redis 中，随着时间的推移，这个键的大小会不断增长。大规模的用户集合可能会占用大量的内存和网络带宽，对 Redis 实例的性能产生负面影响。对于这种情况，可以考虑使用合适的数据分片或分区策略，或者定期归档或压缩旧数据，以减小 bigkey 的大小。
3. 缓存类：缓存数据从数据库加载 缓存数据是 Redis 的常见用途之一。然而，在缓存数据时，需要注意缓存的对象大小和相关的关联数据。当缓存对象非常大或包含大量关联数据时，可能导致 bigkey 的出现。这会影响读取和存储的性能，并且增加网络传输的开销。在缓存设计中，需要权衡数据的实际需求和缓存的大小，确保缓存对象合理且高效地使用。

## 4. 如何发现BigKEY

### 4.1. redis-cli --bigkeys

redis-cli提供了--bigkeys来查找bigkey，例如下面就是一次执行结果：

```shell
[root@localhost myconfig]# redis-cli --bigkeys

# Scanning the entire keyspace to find biggest keys as well as
# average sizes per key type.  You can use -i 0.1 to sleep 0.1 sec
# per 100 SCAN commands (not usually needed).

[00.00%] Biggest string found so far '"k60919"' with 6 bytes
[00.00%] Biggest string found so far '"k371827"' with 7 bytes
[29.13%] Biggest string found so far '"k1000000"' with 8 bytes
[42.53%] Biggest hash   found so far '"customer:001"' with 1 fields
[76.47%] Biggest string found so far '"large_key"' with 100000000 bytes
[100.00%] Sampled 1000000 keys so far

-------- summary -------

Sampled 1000002 keys in the keyspace!
Total key length in bytes is 6888917 (avg len 6.89)

Biggest   hash found '"customer:001"' has 1 fields
Biggest string found '"large_key"' has 100000000 bytes

0 lists with 0 items (00.00% of keys, avg size 0.00)
1 hashs with 1 fields (00.00% of keys, avg size 1.00)
1000001 strings with 106888896 bytes (100.00% of keys, avg size 106.89)
0 streams with 0 entries (00.00% of keys, avg size 0.00)
0 sets with 0 members (00.00% of keys, avg size 0.00)
0 zsets with 0 members (00.00% of keys, avg size 0.00)

```

可以看到--bigkeys给出了每种数据结构的top 1 bigkey，同时给出了每种数据类型的键值个数以及平均大小。

--bigkeys对问题的排查非常方便，但是在使用它时候也有几点需要注意。

```
1. 建议在从节点执行，因为--bigkeys也是通过scan完成的。
2. 建议在节点本机执行，这样可以减少网络开销。
3. 如果没有从节点，可以使用--i参数，例如(--i 0.1 代表100毫秒执行一次)4. --bigkeys只能计算每种数据结构的top1，如果有些数据结构非常多的bigkey，也搞不定，毕竟不是自己写的东西嘛
```

### 4.2. debug object

```shell
127.0.0.1:6379> DEBUG object large_key
Value at:0x7f3c7defb2c0 refcount:1 encoding:raw serializedlength:1136381 lru:7212560 lru_s                                                                           econds_idle:18
```

### 4.3. memory usage

```shell
127.0.0.1:6379> MEMORY USAGE large_key
(integer) 100663352
```

memory usage相比debug object还是要精确一些的。

## 5. 发现BigKEY如何删除

可以看到对于string类型，`del`删除速度还是可以接受的。但对于二级数据结构，随着元素个数的增长以及每个元素字节数的增大，删除速度会越来越慢，存在阻塞Redis的隐患。所以在删除它们时候建议采用渐进式的方式来完成：hscan、ltrim、sscan、zscan。

```
如果你使用Redis 4.0+，一条异步删除unlink就解决，就可以忽略下面内容。
```

### 5.1. string

一般来说，对于string类型使用del命令不会产生阻塞。

```shell
del bigkey
```

### 5.2. hash

使用hscan命令，每次获取部分(例如100个)field-value，在利用hdel删除每个field(为了快速可以使用pipeline)。

### 5.3. list

Redis并没有提供lscan这样的API来遍历列表类型，但是提供了ltrim这样的命令可以渐进式的删除列表元素，直到把列表删除。

### 5.4. set

使用sscan命令，每次获取部分(例如100个)元素，在利用srem删除每个元素。

### 5.5.  sorted set

使用zscan命令，每次获取部分(例如100个)元素，在利用zremrangebyrank删除元素。

## 6. 如何优化

1. 数据拆分：如果一个大的数据结构被存储为一个 bigkey，可以考虑将其拆分为多个小的数据结构。例如，将一个大的哈希表拆分为多个小的哈希表，或将一个大的列表拆分为多个小的列表。这样可以减小单个键的大小，降低对 Redis 的负载。
2. 字段选择：在缓存数据时，只缓存业务上需要的字段，而不是将整个对象或数据集都存储为 bigkey。通过选择性地缓存字段，可以减少存储空间的占用和网络传输的数据量。
3. 数据压缩：对于大型数据结构，可以考虑使用数据压缩算法对数据进行压缩，然后存储在 Redis 中。这样可以减小键的大小，节省存储空间，并在传输数据时减少网络流量。
4. 定期清理：针对设置了过期时间的 bigkey，可以定期进行清理。使用过期异步删除的配置可以减少清理操作对 Redis 的阻塞影响。定期清理可以避免 bigkey 占用过多的内存资源，并保持 Redis 的性能稳定。
5. 数据分片：如果 bigkey 的读写频率很高，可以考虑使用 Redis 的分片技术，将数据分散到多个 Redis 实例上。这样可以均衡负载，减少单个实例的压力，提高整体性能和可扩展性。
6. 数据预热：在系统启动或负载较低的时候，可以通过预先加载和填充 bigkey 的方式，将数据提前加载到 Redis 中。这样可以避免在高负载时期突然加载大量数据而导致的性能问题。
7. 合理设置 Redis 的内存限制：根据实际情况和可用内存资源，合理设置 Redis 的内存限制。避免给 Redis 分配过小的内存，导致频繁的内存回收操作，影响性能。
8. 本地缓存：减少访问redis次数，降低危害，但是要注意这里有可能因此本地的一些开销（例如使用堆外内存会涉及序列化，bigkey对序列化的开销也不小）

# 面试题

## 1. 海量数据里查询某一固定前缀的key

在 Redis 中，没有直接的命令来查询具有固定前缀的 key。但是，我们可以使用 SCAN 命令来实现类似的功能。下面是使用 Redis CLI（命令行界面）演示如何查询具有固定前缀的 key：

```shell
# 设置一些示例数据
SET key1 value1
SET key2 value2
SET key3 value3
SET prefix1_key1 value4
SET prefix1_key2 value5
SET prefix2_key1 value6

# 使用 SCAN 命令查询具有固定前缀的 key
SCAN 0 MATCH prefix1*

# 输出结果
1) "0"
2) 1) "prefix1_key2"
   2) "prefix1_key1"
```

在上面的例子中，我们使用 SCAN 命令进行了前缀为 "prefix1" 的 key 查询。命令的返回结果包含两个部分，第一个部分是下一个迭代的游标，第二个部分是匹配的 key 列表。根据实际情况，您可以根据需要使用不同的匹配模式进行查询。

请注意，SCAN 命令的迭代过程需要多次执行，直到游标为 "0" 才表示所有的 key 已经迭代完成。对于非常大的数据集，可能需要多次执行 SCAN 命令来获取所有的匹配 key。

```go
package main

import (
	"context"
	"fmt"
	"github.com/redis/go-redis/v9"
	"log"
)

var rdb = redis.NewClient(&redis.Options{
	Addr:     "192.168.197.129:6379",
	Password: "",
	DB:       0,
})
var ctx = context.Background()

func init() {
	if err := rdb.Ping(ctx).Err(); err != nil {
		panic(err)
	}
}

func main() {
	prefix := "pogf_*"
	result, err := searchKeysWithPrefix(rdb, prefix)
	if err != nil {
		log.Fatal(err)
	}
	for _, v := range result {
		fmt.Println(v)
	}
}

// searchKeysWithPrefix 在redis里面查询指定前缀的值，并返回集合，失败返回err
func searchKeysWithPrefix(client *redis.Client, prefix string) ([]string, error) {
	var matchingKeys []string

	// 使用 Scan 命令查询具有固定前缀的 key
	cursor := uint64(0)
	for {
		keys, nextCursor, err := client.Scan(context.Background(), cursor, prefix, 0).Result()
		if err != nil {
			return nil, err
		}

		matchingKeys = append(matchingKeys, keys...)

		if nextCursor == 0 {
			break
		}

		cursor = nextCursor
	}

	return matchingKeys, nil
}

```

## 2. 如何生产上限制key*/flushdb/flushall等危险命令的使用

1. **修改 Redis 配置文件**：在 Redis 的配置文件中，可以使用 `rename-command` 选项来重命名某个命令，将其修改为不可执行的名称。例如，可以将 `FLUSHDB` 命令重命名为一个不存在的命令，这样任何尝试执行 `FLUSHDB` 的请求都会失败。

   ```conf
   rename-command FLUSHDB ""
   rename-command FLUSHALL ""
   rename-command keys * ""
   ```

   请注意，这会影响到整个 Redis 实例，因此在执行此操作之前请谨慎考虑。

2. **自定义 Redis 命令**：通过自定义 Redis 命令，您可以完全控制命令的逻辑，并可以选择禁止或限制某些操作。您可以使用 Redis 的 Lua 脚本功能来实现自定义命令。编写一个 Lua 脚本，实现您期望的逻辑，并在需要时调用该脚本代替危险命令的使用。

   ```lua
   local keys = redis.call('KEYS', '*')
   for i=1, #keys do
       redis.call('DEL', keys[i])
   end
   return "OK"
   
   ```

   这个脚本首先使用 `KEYS` 命令获取所有的键，然后通过循环逐个删除这些键，模拟了 `FLUSHDB` 命令的效果。最后，它返回 "OK" 表示操作成功。

   您可以将以上 Lua 脚本保存为一个文件（例如 `flushdb.lua`），然后通过 Redis 的 `EVAL` 命令来执行它：

   ```shell
   EVAL "local keys = redis.call('KEYS', '*') for i=1, #keys do redis.call('DEL', keys[i]) end return 'OK'" 0
   ```

   

   3.**使用代理或中间件**：如果您在生产环境中使用 Redis 的客户端库来访问 Redis 服务器，您可以在客户端层面拦截和处理特定命令的请求。通过自定义的代理或中间件，您可以检查传入的命令，并根据需要禁止或限制某些命令的执行。

   例如，在使用 Go 语言的情况下，您可以编写一个 Redis 代理，通过拦截和处理命令请求，根据需要禁止或拒绝执行危险命令。

## 3. 惰性释放lazyfree你了解过吗？

在 Redis 中，惰性释放是指延迟回收已过期键和已删除键所占用的内存空间。

当 Redis 中的键过期或被删除时，并不立即释放它们所占用的内存。相反，Redis 会将这些过期或已删除键标记为"过期"，并在后续的操作中进行惰性释放。只有当有新的写操作需要使用内存时，Redis 才会将部分或全部的过期键从内存中释放，以腾出空间供新的数据使用。

惰性释放的优点在于避免了频繁的内存回收操作，减少了回收内存的开销，提高了系统的性能。然而，它也带来了一些潜在的问题。由于内存的释放是延迟进行的，如果有大量的过期键或已删除键堆积，可能会导致内存占用持续增加，直到达到 Redis 的内存限制。这可能会影响 Redis 的性能，并导致内存溢出的风险。

为了解决惰性释放可能导致的问题，Redis 引入了主动回收机制，可以通过配置项 `lazyfree-lazy-expire` 和 `lazyfree-lazy-server-del` 进行控制。当这些配置项为 "no" 时，Redis 将在每次访问过期键或已删除键时立即释放相应的内存，而不是等待惰性释放。

## 4. 生产上redis数据库有1000w记录，你如何遍历，key*可以吗？

在 Redis 中，使用 `KEYS` 命令并不适合在生产环境下遍历大量的键。`KEYS` 命令会阻塞 Redis 的主线程，并且随着键数量的增加，遍历时间会变得越来越长，严重影响 Redis 的性能。

如果你需要遍历 Redis 数据库中的大量键，有以下几种可行的方式：

1. 使用迭代器（Iterator）：通过编写脚本或程序，使用 Redis 的 SCAN 命令配合迭代器功能进行逐步遍历。SCAN 命令支持游标分批次获取键，避免阻塞主线程。你可以使用编程语言中的 Redis 客户端库来实现这种迭代器逻辑。
2. 使用有序集合（Sorted Set）：将键存储在有序集合中，以键作为成员，可以设置一个固定的分值，然后使用有序集合的范围查询功能（ZRANGE 或 ZRANGEBYSCORE）来获取一批符合条件的键。
3. 使用 Redis Streams：将键作为消息发送到 Redis Streams 中，然后使用消费者组（Consumer Group）和 XREAD 命令来逐个消费键。