# go-redis

> 安装：go get github.com/redis/go-redis/v9
>
> 

## 1. 第一次连接

```go
package main

import (
	"fmt"
	"github.com/go-redis/redis"
	"log"
)

func main() {
	rdb := redis.NewClient(&redis.Options{
		Addr:     "192.168.187.131:6379",
		Password: "",
		DB:       0,
	})
	res, err := rdb.Ping().Result()
	if err != nil {
		log.Fatal(err)
		return
	}
	defer func(rdb *redis.Client) {
		err := rdb.Close()
		if err != nil {
			log.Fatal(err)
		}
	}(rdb)
	fmt.Println(res)
}

```

```shell
wangyufan@wangcomputerair MINGW64 /d/goworkplace/src/github.com/goRedis (master)
$ go run redis/redis.go
PONG
```

## 2. set、get操作

```go
```

