# 真的是TCP黏包吗

在一次网络实验中我遇到了这样的一个问题，当我的客户端向服务器连续调用`send`函数时，在服务端的`read`函数读取时，两次数据重叠到了一起，代码如下面所示：

服务端

```c
package main

import (
	"fmt"
	"net"
)

func main() {
	ln, err := net.Listen("tcp", ":8888")
	if err != nil {
		fmt.Println("Failed to listen:", err)
		return
	}
	defer ln.Close()

	conn, err := ln.Accept()
	if err != nil {
		fmt.Println("Failed to accept connection:", err)
		return
	}
	fmt.Println("[conn]", conn.RemoteAddr().String())
	message := make([]byte, 1024)
	n, err := conn.Read(message)
	fmt.Println("[READ]", string(message[:n]))
}

```

客户端

```go
package main

import (
	"fmt"
	"net"
)

func main() {
	conn, err := net.Dial("tcp", "localhost:8888")
	if err != nil {
		fmt.Println("Failed to connect:", err)
		return
	}
	fmt.Println("[连接成功]")
	defer conn.Close()

	// 发送黏包数据
	message := "Hello!"
	writen, err := conn.Write([]byte(message))
	if err != nil {
		fmt.Println("[write ]", err.Error())
		return
	}
	fmt.Println("[write successfully]", writen)

	// 发送正常数据
	message = "How are you?"
	conn.Write([]byte(message))
	fmt.Println("[write successfully]", writen)
}

```

服务端运行结果：

```shell
$ go  run test/tcp/client.go
[conn] [::1]:53337
[READ] Hello!How are you?
```

客户端运行结果:

```shell
$ go run test/tcp/server.go
[连接成功]
[write successfully] 6
[write successfully] 6
```

我们预期的结果应该是

```shell
$ go  run test/tcp/client.go
[conn] [::1]:53337
[READ] Hello!
[READ] How are you?
```

那么出现这样现象的原因是什么呢，为什么和我们预期的现象不相同呢？我们接着往下看

## 1. 回顾一下TCP

**传输控制协议**（英语：**T**ransmission **C**ontrol **P**rotocol，缩写：**TCP**）是一种面向连接的、可靠的、基于[字节流](https://zh.wikipedia.org/wiki/字節流)的[传输层](https://zh.wikipedia.org/wiki/传输层)通信协议，由[IETF](https://zh.wikipedia.org/wiki/IETF)的[RFC](https://zh.wikipedia.org/wiki/RFC) [793](https://tools.ietf.org/html/rfc793)定义。在简化的计算机网络[OSI模型](https://zh.wikipedia.org/wiki/OSI模型)中，它完成第四层传输层所指定的功能。

下面是一些关于TCP的主要特点和工作原理的介绍：

1. **面向连接**：TCP在通信前需要先建立连接，即通过三次握手协议进行连接的建立。连接的建立过程确保了通信双方的可达性和可靠性。
2. **可靠性**：TCP通过序列号、确认应答、重传机制和拥塞控制等技术保证了数据的可靠传输。它使用确认应答机制来确认接收到的数据，并进行必要的重传以应对丢失或损坏的数据。
3. **流控制**：TCP利用滑动窗口机制进行流控制，确保发送方和接收方之间的数据传输速率匹配。接收方可以通过窗口大小通知发送方自己的接收能力，从而实现动态调节发送速率。
4. **拥塞控制**：TCP使用拥塞控制算法来避免网络拥塞的发生。通过动态调整发送速率和窗口大小，TCP可以在网络拥塞时减少发送数据，从而维持网络的稳定性和公平性。
5. **字节流传输**：TCP是一种字节流协议，将应用层的数据流切分成合适的大小的数据段（segment）进行传输。TCP屏蔽了底层网络的细节，向上层应用提供了一个可靠的、抽象的字节流接口。
6. **全双工通信**：TCP支持全双工通信，即发送方和接收方可以同时进行数据的发送和接收。这使得通信双方可以独立地进行数据的传输和处理。
7. **面向字节流**：TCP对发送的数据不做消息边界的限制，它将应用层交给它的数据视为一个连续的字节流，而不是独立的消息或数据包。应用层需要自行定义消息的边界或使用其他协议进行消息的切分和解析。

## 2. 面向字节流


面向字节流是TCP的一个重要特性，它指的是TCP协议在传输数据时将数据视为一连串的字节流，而==不关心数据的消息边界或数据包的划分==。

具体来说，面向字节流的特性意味着以下几点：

1. **无消息边界限制**：TCP协议不会对应用层的数据做任何切分或分割，也不会在传输过程中将数据划分成独立的消息或数据包。它仅负责将应用层交给它的字节流按顺序可靠地传输。
2. **连续的字节流**：发送方将数据不间断地写入TCP连接，而接收方将数据按照发送方发送的顺序连续地读取。无论数据的大小或长度如何，TCP会按顺序将字节流逐个传输，并在接收方重新组装为完整的字节流。
3. **保持数据完整性**：TCP通过序列号、确认应答和校验和等机制来保证数据的完整性。发送方对每个发送的数据段都会分配一个唯一的序列号，接收方会对接收到的数据段进行校验和验证和确认应答，以确保数据的准确性和完整性。
4. **数据传输的粒度可变**：TCP协议没有固定的数据传输粒度。发送方可以选择以任意大小的数据块进行发送，这取决于应用层的需求和实际情况。TCP协议会根据网络状况和接收方的接收能力来动态调整发送的数据块的大小。

面向字节流的特性使得TCP协议非常灵活，可以适应不同类型的应用需求。然而，对于应用层来说，这也带来了一些挑战。**由于TCP无法自动划分数据包或识别消息边界，应用层需要自行定义和解析消息的边界。**

在实际应用中，为了实现消息的边界划分，通常会使用特定的消息格式，例如在消息中添加特殊的分隔符（如换行符或特定字符序列）或在消息头中包含消息的长度信息。这样，接收方可以根据这些信息正确地切分和解析接收到的字节流。

**总结起来，TCP的面向字节流的特性使其成为一种可靠的、通用的传输协议。它通过保持数据完整性和按顺序传输字节流的方式，实现了可靠的数据传输。然而，在使用TCP进行应用层通信时，开发人员需要自行处理消息的边界问题，以确保数据的正确解析和处理。**

看到这里大家估计就知道为什么出现这种现象了。

## 3. 不是TCP黏包而是应用层协议的问题

黏包问题通常是由应用层协议设计不合理造成的，而不是TCP协议本身引起的。

在应用层协议中，黏包问题可能出现的原因包括：

1. **消息边界模糊**：应用层协议没有明确定义消息的边界，导致接收方无法准确切分和解析消息。
2. **数据的粘连**：发送方连续发送多个消息，但这些消息在传输过程中被合并为一个或部分粘连在一起，导致接收方无法正确判断消息的边界。
3. **消息长度不固定**：应用层协议中的消息长度不固定，导致发送方和接收方在切分和解析消息时出现不一致。
4. **处理延迟**：接收方在处理接收到的消息时存在延迟，而发送方持续发送消息，导致已接收和待接收的消息粘连在一起。

为了解决应用层协议的黏包问题，可以采取以下一些常见的解决方案：

1. **消息长度字段**：在应用层协议中，引入消息长度字段，使接收方能够根据长度字段准确切分消息。
2. **消息分隔符**：定义特定的消息分隔符，在消息中插入分隔符以标识消息的边界。
3. **消息头标识**：在消息头中添加特定的标识符，用于标识消息的开始和结束。
4. **消息序号**：在每个消息中添加序号，接收方可以根据序号判断消息的完整性。
5. **应用层缓冲区**：接收方使用应用层缓冲区，将接收到的数据存储起来，然后根据应用层协议的定义进行消息的切分和处理。

下面，我会提供一种协议方法去解决这个问题。

## 4. 上层协议

这一块为了演示比较方便，我在这块定义一个十分简单的协议。

```go
type MessageProtocol struct {
	// Len 数据长度，注意此处必须为无符号类型
	Len  uint32
	// Data 真实数据
	Data []byte
}
```

```go
// 定义解包和拆包函数
func pack(msg MessageProtocol) ([]byte, error) {
	dataBuff := bytes.NewBuffer([]byte{})
	if err := binary.Write(dataBuff, binary.LittleEndian, msg.Len); err != nil {
		return nil, err
	}
	if err := binary.Write(dataBuff, binary.LittleEndian, msg.Data); err != nil {
		return nil, err
	}
	return dataBuff.Bytes(), nil
}

func unPack(data []byte) (*MessageProtocol, error) {
	dataBuffer := bytes.NewBuffer(data)
	msg := new(MessageProtocol)
	if err := binary.Read(dataBuffer, binary.LittleEndian, &msg.Len); err != nil {
		return nil, err
	}
	return msg, nil
}
```

这段代码定义了两个函数：`pack` 和 `unPack`，用于消息的打包和解包操作。

### 4.1. **`pack` 函数**：

```go
func pack(msg MessageProtocol) ([]byte, error)
```

- 该函数接受一个 `MessageProtocol` 类型的参数 `msg`，表示要打包的消息。
- 在函数内部，首先创建了一个 `bytes.Buffer` 类型的变量 `dataBuff`，用于存储打包后的字节流。
- 使用 `binary.Write` 函数将消息的长度字段 `msg.Len` 和消息的数据字段 `msg.Data` 按照小端字节序写入 `dataBuff`。
- 如果在写入过程中出现错误，函数将返回 `nil` 和该错误。
- 最后，通过调用 `dataBuff.Bytes()` 将 `dataBuff` 转换为字节切片并返回。

### 4.2. **`unPack` 函数**：

```go
func unPack(data []byte) (*MessageProtocol, error)
```

- 该函数接受一个字节切片类型的参数 `data`，表示要解包的字节流。
- 在函数内部，首先创建了一个 `bytes.Buffer` 类型的变量 `dataBuffer`，并将 `data` 作为输入数据初始化 `dataBuffer`。
- 使用 `binary.Read` 函数从 `dataBuffer` 中按照小端字节序读取消息的长度字段 `msg.Len`，并将其存储在新创建的 `MessageProtocol` 类型的变量 `msg` 中。
- 如果在读取过程中出现错误，函数将返回 `nil` 和该错误。
- 最后，返回解包后的消息 `msg`。

这两个函数配合使用，可以将消息按照指定的协议格式打包为字节流，或者从字节流中解析出消息。在打包过程中，使用 `binary.Write` 函数将消息的长度和数据字段按照小端字节序写入到缓冲区中；而在解包过程中，使用 `binary.Read` 函数从字节流中按照小端字节序读取长度字段，并将其存储在消息对象中。

修改客户端向服务端发送代码:

```go
	// 发送黏包数据
	message := "Hello!"
	msgOne := MessageProtocol{
		Len:  uint32(len(message)),
		Data: []byte(message),
	}
	fmt.Println("[msgOne]", msgOne)
	byteBuffer, err := pack(msgOne)
	if err != nil {
		fmt.Println("[pack]", err)
	}
	writen, err := conn.Write(byteBuffer)
	if err != nil {
		fmt.Println("[write ]", err.Error())
		return
	}
	fmt.Println("[write successfully]", writen)
	message = "How are you?"
	msgOne = MessageProtocol{
		Len:  uint32(len(message)),
		Data: []byte(message),
	}
	byteBuffer, _ = pack(msgOne)
	fmt.Println("[msgOne]", msgOne)
	writen,_=conn.Write(byteBuffer)
	fmt.Println("[write successfully]", write
```

这段代码的作用是模拟发送黏包数据的情况。它构造了两个消息，每个消息都被打包为字节流后发送到 TCP 连接中。

我们先稍微修改一下服务端代码观察一下现象：

```go
// 模仿网络延迟
	time.Sleep(time.Second * 3)
	message := make([]byte, 1024)
	n, err := conn.Read(message)
	fmt.Println("[READ]", message[:n], "[count]", n, "[String]", string(message[:n]))
```



```shell
$ go run test/tcp/server.go test/tcp/protocol.go 
[连接成功]
[byteBuffer] [6 0 0 0 72 101 108 108 111 33]
[write successfully] 10
[byteBuffer] [12 0 0 0 72 111 119 32 97 114 101 32 121 111 117 63]
[write successfully] 16
```

```shell
$ go  run test/tcp/client.go
[conn] [::1]:64806
[READ] [6 0 0 0 72 101 108 108 111 33 12 0 0 0 72 111 119 32 97 114 101 32 121 111 117 63] [count] 26 [String] Hello!
How are you?
```

很显然出现了黏包现象这两个包黏在一起，但是好处是，根据`len`字段的数据，我们可以很容易的取出真实的数据。下面我们就来试一试：

改一改服务端代码

```go
for {
	
		// 首先从字节流中读取4 字节的内容，为什么读取4 字节当然是我们协议的规定啦
		var headLen = make([]byte, 4)
		if _, err := io.ReadFull(conn, headLen); err != nil {
			fmt.Println("[ReadFull]", err)
			return
		}
		msg, err := unPack(headLen)
		if err != nil {
			fmt.Println("[unPack]", err)
			return
		}
		var data []byte
		if msg.Len > 0 {
			data = make([]byte, msg.Len)
			if _, err := io.ReadFull(conn, data); err != nil {
				fmt.Println("[ReadFull]", err)
				return
			}
		}
		fmt.Println("[READDATA]", string(data), "[BYTE]:", data)
		time.Sleep(time.Second)
	}
```

于是我们就发现了这样:

```shell
$ go  run test/tcp/client.go  test/tcp/protocol.go
[conn] [::1]:64976
[READDATA] Hello! [BYTE]: [72 101 108 108 111 33]
[READDATA] How are you? [BYTE]: [72 111 119 32 97 114 101 32 121 111 117 63]
[ReadFull] EOF
```

非常正确的展现出来了。

代码说明：

1. `for` 循环将会一直执行，不断接收消息。
2. 首先，从连接 `conn` 中读取 4 个字节的内容，这是根据协议规定的消息长度字段的长度。
3. 使用 `io.ReadFull` 函数从连接中读取指定长度的数据，将其存储在 `headLen` 字节切片中。
4. 调用 `unPack` 函数对读取到的 `headLen` 进行解包，得到消息的长度和数据字段。
5. 如果消息的长度 `msg.Len` 大于 0，说明存在数据字段，创建一个长度为 `msg.Len` 的字节切片 `data`。
6. 使用 `io.ReadFull` 函数再次从连接中读取指定长度的数据，将其存储在 `data` 字节切片中。
7. 打印输出接收到的数据内容和字节。
8. 使用 `time.Sleep` 函数暂停 1 秒钟，以便在下次循环中继续接收消息。

## 5. 总结

当今天的交流中，我们提出了关于TCP黏包问题和应用层协议设计的一些问题。我们一起探讨了黏包问题的原因、面向字节流的TCP协议、黏包问题在应用层协议中的出现原因以及解决方法。以下是对今天讨论内容的总结：

1. **黏包问题的原因**：黏包问题是由底层传输协议将数据切分成数据块进行传输，而接收方无法准确判断数据块边界所导致的。黏包问题的出现主要与传输速率不匹配、缓冲区大小限制、应用层协议设计等因素有关。
2. **面向字节流的TCP协议**：TCP是一种可靠的面向连接的传输协议，它提供了面向字节流的通信方式。TCP协议将应用层的数据流分割成合适大小的数据块，并通过序号、确认应答、重传等机制来保证数据的可靠性和有序性。
3. **应用层协议的黏包问题**：应用层协议的黏包问题是由协议设计不合理引起的，如消息边界模糊、数据粘连、消息长度不固定、处理延迟等。这些问题使接收方无法准确判断消息的边界，从而导致数据解析错误或丢失。
4. **解决黏包问题的方法**：为了解决应用层协议的黏包问题，可以采取以下方法：
   - 消息长度字段：引入消息长度字段，使接收方能够准确切分消息。
   - 消息分隔符：定义特定的消息分隔符，在消息中插入分隔符以标识消息的边界。
   - 消息头标识：在消息头中添加特定的标识符，用于标识消息的开始和结束。
   - 消息序号：在每个消息中添加序号，接收方可以根据序号判断消息的完整性。
   - 应用层缓冲区：接收方使用应用层缓冲区，将接收到的数据存储起来，然后根据应用层协议的定义进行消息的切分和处理。

总的来说，黏包问题是在应用层协议设计中常见的挑战之一。通过合理的协议设计和消息处理策略，结合TCP协议的特性，可以有效地解决黏包问题，确保数据的可靠传输和正确解析。

附`c语言黏包代码`

客户端：

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

#define SERVER_IP "127.0.0.1"
#define SERVER_PORT 8080

int main() {
    int sockfd;
    struct sockaddr_in server_addr;
    char *message;

    // 创建socket
    if ((sockfd = socket(AF_INET, SOCK_STREAM, 0)) == -1) {
        perror("socket");
        exit(EXIT_FAILURE);
    }

    // 设置服务器地址信息
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERVER_PORT);
    if (inet_pton(AF_INET, SERVER_IP, &(server_addr.sin_addr)) <= 0) {
        perror("inet_pton");
        exit(EXIT_FAILURE);
    }

    // 连接服务器
    if (connect(sockfd, (struct sockaddr*)&server_addr, sizeof(server_addr)) == -1) {
        perror("connect");
        exit(EXIT_FAILURE);
    }

    // 发送黏包数据
    message = "Hello!";
    if (send(sockfd, message, strlen(message), 0) == -1) {
        perror("send");
        exit(EXIT_FAILURE);
    }

    // 发送正常数据
    message = "How are you?";
    if (send(sockfd, message, strlen(message), 0) == -1) {
        perror("send");
        exit(EXIT_FAILURE);
    }

    // 关闭socket
    close(sockfd);

    return 0;
}

```

服务端：

```c

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

#define SERVER_PORT 8080

int main() {
    int sockfd, newsockfd;
    struct sockaddr_in server_addr, client_addr;
    socklen_t client_len;
    char buffer[1024];

    // 创建socket
    if ((sockfd = socket(AF_INET, SOCK_STREAM, 0)) == -1) {
        perror("socket");
        exit(EXIT_FAILURE);
    }

    // 设置服务器地址信息
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERVER_PORT);
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY);

    // 绑定socket到服务器地址
    if (bind(sockfd, (struct sockaddr*)&server_addr, sizeof(server_addr)) == -1) {
        perror("bind");
        exit(EXIT_FAILURE);
    }

    // 监听连接
    if (listen(sockfd, 5) == -1) {
        perror("listen");
        exit(EXIT_FAILURE);
    }

    printf("Server listening on port %d...\n", SERVER_PORT);

    while (1) {
        // 接收新的连接
        client_len = sizeof(client_addr);
        if ((newsockfd = accept(sockfd, (struct sockaddr*)&client_addr, &client_len)) == -1) {
            perror("accept");
            exit(EXIT_FAILURE);
        }

        printf("New client connected: %s:%d\n", inet_ntoa(client_addr.sin_addr), ntohs(client_addr.sin_port));

        // 读取客户端发送的数据
        int bytes_read;
        while ((bytes_read = read(newsockfd, buffer, sizeof(buffer) - 1)) > 0) {
            buffer[bytes_read] = '\0';
            printf("Received message from client: %s\n", buffer);
        }

        if (bytes_read == -1) {
            perror("read");
            exit(EXIT_FAILURE);
        }

        // 关闭客户端连接
        close(newsockfd);
        printf("Client disconnected.\n");
    }

    // 关闭socket
    close(sockfd);

    return 0;
}

```

