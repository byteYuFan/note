# Redis和MySQL的爱恨情仇

## 1. 稍微介绍一哈子

Redis和MySQL是在现代应用程序开发中扮演着重要角色的两个数据存储技术。**Redis是一个快速、高性能的键值存储系统，它以其出色的性能和灵活性而闻名。它能够将数据存储在内存中，并提供快速的读写操作，使其非常适合作为缓存层，用于加速对常用数据的访问。**

与之相反，MySQL是一个广泛使用的关系型数据库管理系统，它**以其可靠的数据持久性和复杂查询功能而受到欢迎。MySQL提供了强大的事务支持、数据完整性和高度可靠的持久化存储，使其成为长期数据存储和管理结构化数据的理想选择。**

尽管Redis和MySQL在数据存储和访问方面具有不同的特点，但它们也可以协同工作，相互补充，以解决特定问题。它们在应用程序中的合作可以带来一系列优势，例如提高应用程序的性能、实现数据的实时同步、实现分布式锁机制等。

在Redis和MySQL的合作中，常见的应用场景是将Redis作为`缓存层`，用于存储频繁访问的数据，以减轻MySQL数据库的负载并提高应用程序的响应速度。通过将数据缓存到Redis，应用程序可以快速访问经常使用的数据，而不必每次都访问MySQL数据库。

此外，Redis还可以与MySQL配合实现数据同步和备份。通过订阅和发布机制，Redis可以接收MySQL数据库的变更事件，并将这些事件传递给其他订阅者，从而实现实时数据的更新和备份。

然而，Redis和MySQL合作也可能面临一些挑战。例如，数据一致性可能是一个问题，因为缓存数据的过期和更新可能导致Redis和MySQL之间的数据不一致。另外，在高并发环境下，如何平衡读写操作和资源利用也是需要考虑的问题。

为了解决这些问题，需要采取一些策略和解决方案。例如，可以通过合理设置缓存失效策略和数据更新通知机制来确保Redis和MySQL之间的数据一致性。同时，还可以使用缓存预热和合理分配读写请求等性能优化策略来提高系统的整体性能。

下面呢，我会详细的谈谈这些功能以及解决方案。

## 2. Redis作为MySQL缓存

在探讨Redis作为MySQL缓存的角色和功能之前，让我们以一段幽默的MySQL和Redis对话作为开场，轻松地引入这个问题。

### 2.1. 一段小小的对话

MySQL：嘿，Redis，听说你是一个很受欢迎的小伙子，大家都在谈论你的快速读写操作和高性能。

Redis：没错，MySQL老兄。我确实是个小伙子，而且我非常快。我有多快呢，嘿嘿我可以在毫秒级别为你提供数据。

MySQL：哦，你是在夸自己呢？但是你要知道，我可是个成熟稳重的家伙，可以提供可靠的数据持久性和复杂查询。

Redis：是的，我听说过你的可靠性和复杂性，MySQL老兄。但是有时候，你处理大量的读请求时会感到吃力吧？

MySQL：是的，这确实是我的一点小弱点。但是我在处理事务和管理结构化数据方面可是一把好手。

Redis：那么，我有个提议，MySQL老兄。为什么我们不合作一下？我可以作为你的缓存层，帮助你加速对常用数据的访问，减轻你的负载压力。

MySQL：啊哈哈哈哈哈哈，Redis小伙子，你是想成为我的助手吗？你有什么特别的能力呢？

Redis：嘿，MySQL老兄，我可以将经常访问的数据存储在我的内存中，这样就能快速地满足读取请求，而不必每次都麻烦你。

MySQL：哦，这听起来不错。你是说，我可以专注于处理事务和复杂查询，而你负责提供快速的读取服务？

Redis：正是如此！我们可以携手合作，将我们各自的优势发挥到极致，实现更高效的应用程序开发。

通过这段幽默的MySQL和Redis对话，我们引入了Redis作为MySQL缓存的概念。它展示了Redis的快速读取能力和MySQL的可靠性与复杂性之间的互补关系。下面，我们将更深入地探讨Redis作为MySQL缓存的实际应用和优势。

### 2.2. 为什么需要这样一个缓存层

我们常常听别人说，要在应用程序和真实数据库之间增加一个缓存层，这样会加快应用程序的处理速度，减少数据库的压力，下面我将会稍微谈一下为什么这样做。

#### 2.2.1. 提高读取性能：

直接查询MySQL数据库可能需要进行复杂的查询操作和磁盘访问，特别是在高并发情况下，可能导致数据库性能下降。这是由于MySQL数据库的存储结构和工作原理决定的。

**MySQL数据库通常使用磁盘存储数据，而磁盘的读写速度相对较慢，尤其是在高并发读取的情况下。**当应用程序发起查询请求时，MySQL数据库需要执行复杂的查询操作，比如联接多个表、执行聚合函数或排序等，这些操作可能需要涉及大量的磁盘读取和计算。

在高并发情况下，频繁访问MySQL数据库会导致数据库负载增加，磁盘的读写操作变得更加频繁和缓慢。这可能导致数据库性能下降，响应时间增加，甚至出现数据库连接池耗尽、请求超时等问题。

然而，通过引入缓存层（如Redis），应用程序可以快速访问缓存中的数据，避免了频繁访问MySQL数据库的开销，从而提高读取性能。缓存层将常用的数据存储在内存中，读取数据的速度非常快，远远超过了磁盘的读取速度。因此，应用程序可以直接从缓存中获取数据，无需执行复杂的查询操作和磁盘访问，大大减少了读取数据的时间和开销。

通过使用缓存层，应用程序可以将读取频繁的数据缓存在Redis中，并设置合适的缓存策略，如过期时间或更新策略，以保持数据的一致性。这样，在高并发情况下，应用程序可以直接从缓存中获取数据，避免了对MySQL数据库的频繁访问，减轻了数据库的负载，提高了读取性能和整体系统的响应速度。

#### 2.2.2. 增加系统的可扩展性

1. 缓存层的水平扩展： 缓存层本身具备水平扩展的能力。通过增加缓存服务器的数量，可以分散并发请求的负载，提供更高的并发读取能力。这种水平扩展方式可以在保持系统稳定性的同时，有效地扩展系统的处理能力，增强了系统的可扩展性。
2. 分布式缓存架构： 缓存层常常采用分布式架构，可以将缓存数据分布在多个节点上。这样，在高并发的情况下，可以通过增加缓存节点来扩展缓存层的容量和吞吐量。分布式缓存架构提供了更高的数据存储容量和处理能力，以应对大规模系统的需求。
3. 解耦数据库和应用程序： 缓存层的引入使得应用程序可以直接从缓存中获取数据，而无需直接与数据库进行交互。这种解耦合的设计模式使得应用程序和数据库之间的耦合度降低，提高了系统的可维护性和可扩展性。在需要对数据库进行升级或更换时，缓存层可以提供平滑过渡的机制，不会对应用程序产生太大的影响。

### 2.3. 图示

未使用缓存层的操作流程：

![](D:\桌面\note\redis文章\images\5271.png)

使用缓存层的操作流程：

![](D:\桌面\note\redis文章\images\5272.png)

### 2.4. 代码测试

#### 2.4.1. 测试环境搭建

下面我将会用GO和python来测试一下有缓存层和没有缓存层的具体区别。

测试环境：MySQL 8.0

```shell
docker run --name mysql_redis -p 3310:3306 -e MYSQL_ROOT_PASSWORD=123456 -d  mysql
CREATE TABLE `user` (
  `id` bigint NOT NULL,
  `username` varchar(100) NOT NULL,
  `age` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
INSERT into user VALUES(1,"redis-test",18)
```

首先，我们使用 Docker 运行了一个名为 "mysql_redis" 的容器，并将容器内部的 MySQL 服务的 3306 端口映射到主机的 3310 端口。同时，我们通过设置环境变量的方式，将 MySQL 的 root 用户密码设置为 "123456"。这个容器是以后台模式运行的，这样我们就可以在后台进行数据库操作而无需干扰我们的工作。

接下来，我们在 MySQL 数据库中创建了一个名为 `user` 的表。这个表具有三个列，分别是 `id` (bigint)，`username` (varchar(100)) 和 `age` (int)。我们还将 `id` 列指定为主键，以确保表中每一行的唯一性和快速查询。

最后，我们向 `user` 表中插入了一条数据。这条数据的 `id` 是 1，`username` 是 "redis-test"，`age` 是 18。这样，我们就有了一条示例数据，可以用来测试和验证表的功能。

通过执行上述操作，我们成功地设置了一个 MySQL 容器，创建了一个名为 `user` 的表，并向表中插入了一条数据。这为我们后续的测试提供了基础数据，以便我们可以针对这个表进行各种查询、更新或删除等操作，并验证表的功能和性能。

请注意，在实际场景中，您可能需要根据您的具体需求和环境进行相应的调整和修改。

#### 2.4.2. 如何进行测试

1. 安装和配置 Redis： 首先，需要安装 Redis 并确保它正常运行在本地环境中。您可以从 Redis 官方网站下载并安装 Redis，然后启动 Redis 服务器。
2. 编写测试代码： 使用您喜欢的编程语言（例如 Go、Python、Java等），编写测试代码来连接到 MySQL 数据库和 Redis，并模拟有无缓存层的情况下执行查询操作。
3. 运行测试代码： 执行测试代码，观察输出结果。代码中的测试分为两部分：无缓存层情况和有缓存层情况。在无缓存层情况下，我们每次都直接查询 MySQL 数据库。而在有缓存层情况下，我们首先尝试从 Redis 缓存中获取数据，如果缓存中不存在，则再去查询 MySQL 数据库，并将查询结果存入缓存。
4. 比较执行时间： 观察测试结果中输出的执行时间。比较无缓存层情况和有缓存层情况下执行5000次查询操作所花费的时间。通常情况下，有缓存层的情况下执行时间应该更短，因为数据可以从快速的内存缓存中获取，而无需每次都去查询 MySQL 数据库。

通过这个测试，您可以评估有无缓存层对查询速度的影响。请注意，实际的测试结果可能会受到各种因素的影响，包括硬件性能、网络延迟和数据量等。因此，建议您在不同的环境和数据规模下进行多次测试，以获得更准确的结果。

#### 2.4.3. 实测

无缓存测试：

```go
func QueryWithoutCache()  {
	// DSN:Data Source Name
	dsn := "root:123456@tcp(docker:3310)/redis-test"
	db, err := sql.Open("mysql", dsn)
	if err != nil {
		panic(err)
	}
	defer db.Close()  // 注意这行代码要写在上面err判断的下面
	// 定义测试的数量
	concurrency := 100000
	// 计时开始
	start := time.Now()
	query := "SELECT * FROM user WHERE id = 1"
	// 并发查询用户ID为1的记录
	for i := 0; i < concurrency; i++ {
			// 执行查询操作
			rows, err := db.Query(query)
			if err != nil {
				fmt.Println("Failed to execute query:", err)
				return
			}
			defer rows.Close()
			for rows.Next() {
				var id int
				var username string
				var age int
				if err := rows.Scan(&id, &username, &age); err != nil {
					fmt.Println("Failed to scan row:", err)
					return
				}
			}

			if err := rows.Err(); err != nil {
				fmt.Println("Error occurred while iterating over rows:", err)
			}
	}

	// 计算执行时间
	elapsed := time.Since(start)
	fmt.Println("执行时间:", elapsed)
}
```

```shell
=== RUN   TestQueryWithoutCache
执行时间: 2m17.3112756s
--- PASS: TestQueryWithoutCache (137.33s)
PASS

```

![](D:\桌面\note\redis文章\images\5273.png)

**有缓存层**

```GO
// QueryWithCache 有缓存层
func QueryWithCache()  {
	// 连接数据库
	dsn := "root:123456@tcp(docker:3310)/redis-test"
	db, err := sql.Open("mysql", dsn)
	if err != nil {
		panic(err)
	}
	defer db.Close()
	redisClient:=redis.NewClient(&redis.Options{
		Addr: "127.0.0.1:6379",
		Password: "",
		DB: 0,
	})
	ctx:=context.Background()
	// 定义并发操作的协程数量
	concurrency := 100000
	// 计时开始
	start := time.Now()
	// 并发查询用户ID为1的记录（带缓存层）
	for i := 0; i < concurrency; i++ {
			// 先尝试从缓存中获取数据
			cacheKey := "user:1"
			_, err := redisClient.Get(ctx, cacheKey).Result()
			if err == nil {
				// 缓存命中，直接使用缓存数据
				continue
			} else if err != redis.Nil {
				// Redis 查询出错
				fmt.Println("Failed to retrieve from cache:", err)
				return
			}

			// 缓存未命中，执行查询操作
			query := "SELECT * FROM user WHERE id = 1"
			rows, err := db.Query(query)
			if err != nil {
				fmt.Println("Failed to execute query:", err)
				return
			}
			defer rows.Close()

			// 遍历查询结果
			for rows.Next() {
				var id int
				var username string
				var age int
				if err := rows.Scan(&id, &username, &age); err != nil {
					fmt.Println("Failed to scan row:", err)
					return
				}

				// 将查询结果存入缓存
				err := redisClient.Set(ctx, cacheKey, fmt.Sprintf("ID: %d, Username: %s, Age: %d", id, username, age), 1*time.Minute).Err()
				if err != nil {
					fmt.Println("Failed to set cache:", err)
				}
			}

			if err := rows.Err(); err != nil {
				fmt.Println("Error occurred while iterating over rows:", err)
			}
	}

	// 计算执行时间
	elapsed := time.Since(start)
	fmt.Println("执行时间:", elapsed)
}
```

```SHELL
=== RUN   TestQueryWithCache
执行时间: 9.1340882s
--- PASS: TestQueryWithCache (9.14s)
PASS
```

**测试结果分析：**

因为这阔是想体现出有缓存层和没有缓存层的区别，因此这阔采用了for循环进行测试，而没有启用goroutine，这样会使得测试效果更加明显。

根据测试结果，可以看出在有缓存层和无缓存层的情况下，执行100000次查询数据库操作的耗时有显著差异。

在有缓存层的情况下，测试函数 `TestQueryWithCache` 执行时间为 9.1340882 秒。这说明在使用缓存层的情况下，大量的查询操作可以从缓存中快速获取结果，避免了频繁访问 MySQL 数据库，从而显著提高了查询性能。

而在无缓存层的情况下，测试函数 `TestQueryWithoutCache` 执行时间为 2 分钟 17.3112756 秒，即约为 137.33 秒。这表明在每次查询时都需要直接访问 MySQL 数据库，进行复杂的查询操作和磁盘访问，导致查询性能显著下降。尤其是在高并发情况下，频繁的数据库访问可能导致连接池资源不足、网络延迟增加等问题，进一步影响了执行时间。

综上所述，通过引入缓存层可以明显提高系统的查询性能。缓存层可以避免频繁访问 MySQL 数据库，减轻数据库的负载压力，并且能够在高并发情况下快速响应查询请求，提高系统的可扩展性和性能表现。

需要注意的是，具体的性能提升取决于缓存的命中率和数据访问模式。如果数据的更新频率较高，缓存的命中率可能会降低，从而影响性能提升的效果。因此，在使用缓存层时，需要综合考虑缓存策略、数据更新机制以及业务需求，以实现最佳的性能优化效果。

附python代码

```shell
pip install mysql-connector-python
pip install redis
```

```python
import time
import mysql.connector
import redis

# 创建 MySQL 数据库连接
mysql_conn = mysql.connector.connect(
    host='192.168.197.129',
    port='3310',
    user='root',
    password='123456',
    database='redis-test'
)

# 创建 Redis 连接
redis_conn = redis.Redis(host='localhost', port=6379, db=0)

# 有缓存层的查询函数
def query_with_cache():
    # 先尝试从缓存中获取数据
    result = redis_conn.get('user:1')
    if result is not None:
        return result.decode()

    # 缓存中不存在，从数据库中查询
    cursor = mysql_conn.cursor()
    query = "SELECT * FROM user WHERE id = 1"
    cursor.execute(query)
    result = cursor.fetchone()

    if result is not None:
        # 将查询结果存入缓存
        redis_conn.set('user:1', str(result), ex=1)  # 设置缓存过期时间为1min
        return str(result)

    return "User not found"

# 无缓存层的查询函数
def query_without_cache():
    cursor = mysql_conn.cursor()
    query = "SELECT * FROM user WHERE id = 1"
    cursor.execute(query)
    result = cursor.fetchone()

    if result is not None:
        return str(result)

    return "User not found"

# 测试有缓存层的情况
start_time = time.time()
for _ in range(100000):
    query_with_cache()
elapsed_time = time.time() - start_time
print("执行时间（有缓存层）：", elapsed_time)

# 测试无缓存层的情况
start_time = time.time()
for _ in range(100000):
    query_without_cache()
elapsed_time = time.time() - start_time
print("执行时间（无缓存层）：", elapsed_time)

# 关闭数据库连接
mysql_conn.close()

```

```shell
wangyufan@wangcomputerair MINGW64 /d/pythonProject/pythonProject1 (develop)
$ python redis-test.py
执行时间（有缓存层）： 12.966132164001465
执行时间（无缓存层）： 262.1109185218811
```

Go语言的执行时间明显比Python语言的执行时间短。这种差距可能是由于：

语言特性和执行模型：Go语言在设计上注重高性能和并发性能，并具有更低的启动时间和更高的执行效率。它是一种编译型语言，代码经过编译后可以直接在机器上执行，无需解释器。相比之下，Python是一种解释型语言，它需要通过解释器逐行解释执行代码，因此在执行速度上可能较慢。

## 3. Redis作为订阅发布的中间件

MySQL（小M）：嘿，Redis老兄，听说你擅长数据存储和处理，你可曾考虑过和我合作？

Redis（大R）：当然啦，小M！我可是个多才多艺的缓存大师。咱们可不只是简单的键值存储哦。

MySQL（小M）：哦？那你是如何帮助我实现数据同步和备份的呢？

Redis（大R）：嘿嘿，小M，我有一个酷炫的特技，叫做订阅和发布机制。

MySQL（小M）：订阅和发布？听起来好像是在搞传媒业务啊。

Redis（大R）：哈哈，不完全是。你可以把我想象成一个广播电台，你只需要在我这里创建一个频道，然后将你的更新消息发布到这个频道上。

MySQL（小M）：哦哦，我明白了。那其他程序或者系统可以通过订阅我的频道来接收这些更新消息，对吧？

Redis（大R）：没错，小M！你真聪明。其他程序可以通过订阅我的频道，实时接收到你的更新消息，并进行相应的处理。这样，我们就实现了数据同步和备份。

MySQL（小M）：嗯，听起来挺靠谱的。有了你这个广播电台，我再也不用担心数据的延迟和丢失了。

Redis（大R）：没错，小M。我可是可靠的数据传输专家。只要你在频道上发布消息，我会尽快将它们送达给订阅者。

MySQL（小M）：太好了！我们合作起来，数据同步和备份就能更加可靠和高效了。

Redis（大R）：没错，小M！我们就是完美的组合。现在让我们一起携手，为数据的安全与可靠保驾护航！

通过这段幽默的对话，我们引入了Redis和MySQL之间的数据同步和备份话题，同时给读者带来了一些轻松和愉快的氛围。接下来，我们可以详细介绍订阅和发布机制的工作原理和具体实现方法。

### 3.1. 什么是订阅和发布

订阅和发布（Publish/Subscribe）是一种消息传递模式，用于在分布式系统中进行消息的发布和接收。它基于一个简单的观察者模式，其中发布者（发布消息的程序）将消息发送给多个订阅者（接收消息的程序），而订阅者则根据自己的兴趣选择订阅感兴趣的消息。

### 3.2. Redis的发布订阅

Redis 发布订阅 (pub/sub) 是一种消息通信模式：发送者 (pub) 发送消息，订阅者 (sub) 接收消息。

Redis 客户端可以订阅任意数量的频道。

下图展示了频道 channel1 ， 以及订阅这个频道的三个客户端 —— client2 、 client5 和 client1 之间的关系：

<img src="D:\桌面\note\redis文章\images\5274.png" style="zoom:67%;" />

当有新消息通过 PUBLISH 命令发送给频道 channel1 时， 这个消息就会被发送给订阅它的三个客户端：

<img src="D:\桌面\note\redis文章\images\5275.png" style="zoom:67%;" />

测试：

client1

```shell
[root@localhost ~]# redis-cli
127.0.0.1:6379> SUBSCRIBE test-01
Reading messages... (press Ctrl-C to quit)
1) "subscribe"
2) "test-01"
3) (integer) 1
```

client2:

```shell
[root@localhost ~]# redis-cli
127.0.0.1:6379> PUBLISH test-01 "test channel test-01"
(integer) 1
```

client1:

```shell
1) "message"
2) "test-01"
3) "test channel test-01"
```

常用命令汇总：

| 命令                                        | 说明                                                         |
| ------------------------------------------- | ------------------------------------------------------------ |
| PSUBSCRIBE pattern [pattern ...]            | 订阅一个或多个符合指定模式的频道。                           |
| PUBSUB subcommand [argument [argument ...]] | 查看发布/订阅系统状态，可选参数 1) channel 返回在线状态的频道。 2) numpat 返回指定模式的订阅者数量。 3) numsub 返回指定频道的订阅者数量。 |
| PUBSUB subcommand [argument [argument ...]] | 将信息发送到指定的频道。                                     |
| PUNSUBSCRIBE [pattern [pattern ...]]        | 退订所有指定模式的频道。                                     |
| SUBSCRIBE channel [channel ...]             | 订阅一个或者多个频道的消息。                                 |
| UNSUBSCRIBE [channel [channel ...]]         | 退订指定的频道。                                             |

### 3.3. MySQL和Redis如何配合

MySQL和Redis可以结合使用发布订阅模式，实现数据的同步和备份。下面是详细的介绍和原理说明：

1. 数据写入MySQL：当应用程序向MySQL数据库写入数据时，例如插入、更新或删除记录，MySQL会将这些操作应用到相应的表中。
2. Redis订阅MySQL的Binlog：Redis作为订阅者，可以通过MySQL的二进制日志（Binlog）功能来监听数据库的变更操作。Binlog是MySQL的日志文件，记录了数据库中发生的所有更改操作。
3. 解析和处理Binlog：Redis订阅者会解析MySQL的Binlog，并提取出相应的操作信息，例如被修改的表、操作类型（插入、更新、删除）以及相应的数据内容。
4. 将数据发布到Redis频道：根据解析得到的操作信息，Redis会将相应的数据发布到特定的Redis频道中。每个频道对应一个表，数据的更新将发布到对应表的频道中。
5. Redis订阅者接收数据更新：Redis订阅者订阅相应的Redis频道，以接收数据的更新。当MySQL中的数据发生变更时，Redis会将这些变更的数据发布到对应的频道中，订阅者即可接收到这些更新数据。
6. 处理数据更新：Redis订阅者接收到更新数据后，可以根据业务需求进行相应的处理。例如，可以将数据存储到Redis缓存中，以提供快速读取访问，或者将数据写入其他数据存储系统进行备份或进一步处理。

通过发布订阅模式，MySQL和Redis实现了解耦和异步处理的方式。MySQL负责处理应用程序的数据写入请求，而Redis作为订阅者通过监听MySQL的Binlog来捕获数据的变更，再将这些变更的数据发布到Redis频道中。订阅者可以根据需求接收这些数据更新，并进行相应的处理，从而实现数据的同步和备份。

这种配合使用的方式可以提高系统的性能和可扩展性。由于Redis的高性能特点和发布订阅模式的异步处理，可以减轻MySQL的读压力，提高读取性能。同时，通过将数据存储在Redis缓存中，可以加快数据的访问速度，降低数据库的负载。此外，由于Redis支持集群和分布式部署，可以实现数据的水平扩展和高可用性。

总而言之，MySQL和Redis配合使用发布订阅模式可以实现数据的同步和备份，提高系统的性能和可扩展性。MySQL负责数据的写入，而Redis通过订阅MySQL的Binlog来捕获数据的变更并发布到Redis频道中，订阅者可以接收这些数据更新并进行相应处理。这种方式实现了解耦和异步处理，提供了更灵活和高效的数据管理方式。

### 3.4. 实操举例

1. 开启MySQL binlog日志功能

```shell
log-bin=mysql-bin
log-bin-index=mysql-bin.index
```

2.启动监控程序，这里以GO语言为例子：

```go
package main

import (
	"context"
	"fmt"
	"github.com/go-mysql-org/go-mysql/mysql"
	"github.com/go-mysql-org/go-mysql/replication"
	"github.com/redis/go-redis/v9"
)

func main() {
	// 连接 Redis
	redisClient := redis.NewClient(&redis.Options{
		Addr:     "localhost:6379",
		Password: "", // 如果需要密码
		DB:       0,  // 默认数据库
	})

	// 创建 Binlog 解析器
	cfg := replication.BinlogSyncerConfig{
		ServerID: 100,
		Flavor:   "mysql",
		Host:     "docker",
		Port:     3310,
		User:     "root",
		Password: "123456",
	}

	syncer := replication.NewBinlogSyncer(cfg)

	// 获取最新的 Binlog 位置
	pos := mysql.Position{
		Name: "mysql-bin.000001",
		Pos:  4,
	}

	// 开始监听 Binlog 变更
	streamer, err := syncer.StartSync(pos)
	if err != nil {
		fmt.Println("Failed to start Binlog sync:", err)
		return
	}

	// 创建上下文
	ctx := context.Background()

	// 监听 Binlog 事件
	for {
		ev, err := streamer.GetEvent(ctx)
		if err != nil {
			fmt.Println("Failed to get Binlog event:", err)
			continue
		}

		// 处理行事件
		switch e := ev.Event.(type) {
		case *replication.RowsEvent:
			// 处理行事件，获取需要的数据
			for _, row := range e.Rows {
				// 根据需要处理行数据
				// 获取表名、列名和对应的值
				tableName := string(e.Table.Schema) + "." + string(e.Table.Table)
				columnNames := make([]string, len(e.Table.ColumnName))
				for i, colNameBytes := range e.Table.ColumnName {
					columnNames[i] = string(colNameBytes)
				}

				values := row
				// 将数据发布到 Redis
				redisClient.Publish(ctx, "binlog_data", fmt.Sprintf("Table: %s, Columns: %v, Values: %v", tableName, columnNames, values))
			}
		}
	}
}

```

3. 向MySQL插入一条数据

```mysql
mysql> insert into test(column_a) values('test01'),('test02');
Query OK, 2 rows affected (0.00 sec)
Records: 2  Duplicates: 0  Warnings: 0
```

4. 观察redis

````shell
127.0.0.1:6379> SUBSCRIBE binlog_data
Reading messages... (press Ctrl-C to quit)
1) "subscribe"
2) "binlog_data"
3) (integer) 1
1) "message"
2) "binlog_data"
3) "Table: redis_test.test, Columns: [], Values: [10 test01 <nil>]"
1) "message"
2) "binlog_data"
3) "Table: redis_test.test, Columns: [], Values: [11 test02 <nil>]"
````



以上就是一个简单的redis发布订阅模式，现在，我们就可以通过订阅来执行相关的操作了，具体就由大家实现了，我简单的举一个例子：

```go
err := redisClient.Set(ctx, "cache_key", receivedData, 0).Err()
if err != nil {
    // 处理存储错误
}
```

存储到Redis缓存中：使用Redis的SET命令将接收到的数据存储到指定的缓存键中。

## 4. MySQL和Redis的一致性问题

MySQL: 嘿，Redis兄弟，听说你最近在高并发下表现得很出色啊！

Redis: 哈哈，当然啦，MySQL老弟！我可是一把好手，处理并发就像是我玩魔术一样轻松自如！

MySQL: 哦，是吗？那我可要考验一下你的本事了！你知道吗，在高并发环境下，我们可能会遇到一些不一致的问题。

Redis: 哎呀，MySQL老兄，你别吓唬我啦！我可是信誉卓著的，怎么可能出现不一致的情况呢？

MySQL: 哈哈，别自信得太早啊，Redis兄弟！想象一下，当有许许多多的客户端同时向我们发送写请求时，你会怎么处理呢？

Redis: 哦，这个嘛，当然是按照顺序一个一个地执行啦！我可是很有条理的！

MySQL: 但是，如果其中一个客户端的写请求在我还没来得及处理完之前就到了你那里，你会怎么办呢？

Redis: 嗯，我会尽力处理，但有时候可能会因为忙碌而延迟执行，这样会导致数据不一致吗？

MySQL: Bingo！正是这个问题！当有多个客户端同时修改同一份数据时，如果我还没来得及更新你的数据，你的读操作可能就会获取到旧的数据，导致不一致性。

Redis: 哎呀，这可不好玩了！那我们怎么解决这个问题呢？

MySQL: 嗯，我们可以采用一些技术手段来确保一致性。比如，我们可以使用事务来保证一组操作的原子性，要么全部成功，要么全部失败。

Redis: 哦，原来如此！这样就能避免中间状态的数据被读取到了。

MySQL: 对，还可以采用分布式锁来控制并发访问，只允许一个客户端对数据进行修改。

Redis: 哈哈，MySQL老兄，你的解决方案真是妙不可言！我们一起努力，让数据的一致性在高并发下也能得到保障！

### 4.1. 缓存双写一致性

缓存双写一致性是指在使用缓存系统（如Redis）与数据库（如MySQL）进行数据存储时，保持两者之间的数据一致性。当数据发生变化时，需要同时更新数据库和缓存，以确保数据的准确性和一致性。

我的理解是，缓存双写一致性是通过在数据写入时采取一定的策略和措施，确保数据库和缓存之间的数据保持同步。这是由于数据库和缓存之间存在一定的延迟和异步性，导致在数据写入数据库后，缓存中的数据可能尚未及时更新。

给缓存设置过期时间，定期清理缓存并回写，是保证最终一致性的解决方案。

我们可以对存入缓存的数据设置过期时间，所有的**写操作以数据库为准**，对缓存操作只是尽最大努力即可。也就是说如果数据库写成功，缓存更新失败，那么只要到达过期时间，则后面的读请求自然会从数据库中读取新值然后回填缓存，达到一致性，切记，要以mysql的数据库写入库为准。

下面呢我将会介绍四种更新策略：

### 4.2. 先更新数据库在更新缓存

> 1.  先更新mysql的某商品的库存，当前商品的库存是100，更新为99个。
> 2.   先更新mysql修改为99成功，然后更新redis。
> 3.   此时假设异常出现，更新redis失败了，这导致mysql里面的库存是99而redis里面的还是100 。
> 4.   上述发生，会让数据库里面和缓存redis里面数据不一致，读到redis脏数据

> 【先更新数据库，再更新缓存】，A、B两个线程发起调用
>
> **【正常逻辑】**
>
> 1 A update mysql 100
>
> 2 A update redis 100
>
> 3 B update mysql 80
>
> 4 B update redis 80
>
> **【异常逻辑】多线程环境下，A、B两个线程有快有慢，有前有后有并行**
>
> 1 A update mysql 100
>
> 3 B update mysql 80
>
> 4 B update redis 80
>
> 2 A update redis 100
>
> 最终结果，mysql和redis数据不一致，o(╥﹏╥)o，
>
> mysql80,redis100

### 4.3. 先更新缓存在更新数据库

> 【先更新缓存，再更新数据库】，A、B两个线程发起调用
>
> **【正常逻辑】**
>
> 1 A update redis 100
>
> 2 A update mysql 100
>
> 3 B update redis 80
>
> 4 B update mysql 80
>
> **【异常逻辑】多线程环境下，A、B两个线程有快有慢有并行**
>
> A update redis  100
>
> B update redis  80
>
> B update mysql 80
>
> A update mysql 100
>
> ----mysql100,redis80



### 4.4. 先删除缓存在更新数据库

（1）请求A进行写操作，删除redis缓存后，工作正在进行中，更新mysql......A还么有彻底更新完mysql，还没commit

（2）请求B开工查询，查询redis发现缓存不存在(被A从redis中删除了)

（3）请求B继续，去数据库查询得到了mysql中的旧值(A还没有更新完)

（4）请求B将旧值写回redis缓存

（5）请求A将新值写入mysql数据库 

上述情况就会导致不一致的情形出现。 

| 时间 | 线程A                                                      | 线程B                                                        | 出现的问题                                                   |
| ---- | ---------------------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| t1   | 请求A进行写操作，删除缓存成功后，工作正在mysql进行中...... |                                                              |                                                              |
| t2   |                                                            | 1 缓存中读取不到，立刻读mysql，由于A还没有对mysql更新完，读到的是旧值 2 还把从mysql读取的旧值，写回了redis | 1 A还没有更新完mysql，导致B读到了旧值 2 线程B遵守回写机制，把旧值写回redis，导致其它请求读取的还是旧值，A白干了。 |
| t3   | A更新完mysql数据库的值，over                               |                                                              | redis是被B写回的旧值，mysql是被A更新的新值。出现了，数据不一致问题。 |

如果数据库更新失败或超时或返回不及时，导致B线程请求访问缓存时发现redis里面没数据，缓存缺失，B再去读取mysql时，从数据库中读取到旧值，还写回redis，导致A白干了，o(╥﹏╥)o

### 4.4. 先更新数据库在删除缓存

| 时间 | 线程A                  | 线程B                                   | 出现的问题                                         |
| ---- | ---------------------- | --------------------------------------- | -------------------------------------------------- |
| t1   | 更新数据库中的值...... |                                         |                                                    |
| t2   |                        | 缓存中立刻命中，此时B读取的是缓存旧值。 | A还没有来得及删除缓存的值，导致B缓存命中读到旧值。 |
| t3   | 更新缓存的数据，over   |                                         |                                                    |

 假如缓存删除失败或者来不及，导致请求再次访问redis时缓存命中，读取到的是缓存旧值。

### 4.5. 双检加锁解决

多个线程同时去查询数据库的这条数据，那么我们可以在第一个查询数据的请求上使用一个 互斥锁来锁住它。其他的线程走到这一步拿不到锁就等着，等第一个线程查询到了数据，然后做缓存。后面的线程进来发现已经有缓存了，就直接走缓存。 

```go
func get(key string)string{
    value,err:=redis.get(ctx,key)
    if err==nil{
        return value
    }
   
    if err==redis.Nil{
        //说明没查到 加锁
        lock.Lock()
        //在检查一边
        value,err:=redis.get(ctx,key)
   		if err==nil{
             lock.Unlock()
        return value
        }else{
            //在数据库查找
            Query()
            redis.set(ctx,value,expireTime)
            lock.Unlock()
            return
        }
    }
   
    }
}
```

为什么要检查两遍呢

对于从缓存中获取数据的操作，存在两次检查的原因是为了避免在高并发情况下出现竞态条件。

首次检查是为了判断缓存中是否存在所需的数据。如果缓存中存在数据，则直接返回，避免不必要的数据库查询和加锁操作。

如果首次检查发现缓存中不存在数据（即返回了redis.Nil错误），则表示需要进行数据库查询。为了避免多个并发请求同时进入数据库查询的情况，这里使用了互斥锁（即`lock.Lock()`）来确保只有一个请求进入数据库查询操作。

在获取到锁之后，需要再次进行检查（即第二次检查），这是为了避免在等待锁的过程中其他请求已经进行了数据库查询并更新了缓存，避免重复的数据库查询和缓存更新操作。

如果第二次检查发现缓存中已经存在数据（即其他请求已经进行了数据库查询并更新了缓存），则可以直接释放锁并返回获取到的数据。

如果第二次检查仍然发现缓存中不存在数据，那么进行数据库查询并将查询到的数据更新到缓存中，然后释放锁，并返回获取到的数据。

通过这样的双重检查，可以减少对数据库的频繁查询操作，同时确保在高并发情况下只有一个请求进行数据库查询和缓存更新，提高了性能和一致性。