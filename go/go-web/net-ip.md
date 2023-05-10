# 一 IP

## 1 全局单播地址

全局单播地址是 IPv4 地址空间中的一种地址类型，它被用于在 Internet 上单播数据包。全局单播地址是指能够被路由器转发到全球任何地方的 IP 地址，因此也称为全球单播地址。

全局单播地址的范围是从 1.0.0.0 到 223.255.255.255，其中 224.0.0.0 到 239.255.255.255 是多播地址，240.0.0.0 到 255.255.255.254 是保留地址，255.255.255.255 是广播地址。

全局单播地址的分配和管理是由互联网号码分配机构（IANA）负责的。IANA 将全局单播地址划分为多个地址块，并将这些地址块分配给各个地区的互联网注册机构（RIR）进行分配。RIR 再将这些地址块分配给各个互联网服务提供商（ISP）和企业，使得它们可以分配给自己的用户和设备。

在 IPv4 地址枯竭的情况下，全局单播地址的分配变得越来越困难。因此，IPv6 已经成为了未来互联网的主要协议，它提供了更多的地址空间，可以支持更多的设备和用户。

```go
package main

import (
        "fmt"
        "log"
        "net"
        "os"
)

func main() {
        if len(os.Args) != 2 {
                log.Fatal("go run global.go <ip>")
        }

        ipStr := os.Args[1]
        ip := net.ParseIP(ipStr)
        if ip == nil {
                log.Fatalf("%v is not a valid IP address\n", ipStr)
        }

        if ip.IsGlobalUnicast() {
                fmt.Printf("%v is a global unicast IP address\n", ip)
        } else {
                fmt.Printf("%v is not a global unicast IP address\n", ip)
        }
}


```



```shell
┌──(root㉿kali)-[~/…/src/github.com/net/ip]
└─# go run global.go 127.0.0.1
127.0.0.1 is not a global unicast IP address

┌──(root㉿kali)-[~/…/src/github.com/net/ip]
└─# go run global.go 192.168.0.1
192.168.0.1 is a global unicast IP address

┌──(root㉿kali)-[~/…/src/github.com/net/ip]
└─# go run global.go 8.8.8.8
8.8.8.8 is a global unicast IP address

┌──(root㉿kali)-[~/…/src/github.com/net/ip]
└─#

```

可能是由于操作系统的实现机制不同，导致 `IP.IsGlobalUnicast()` 函数的实现存在差异。

`IP.IsGlobalUnicast()` 函数是根据 RFC 4291 中的规范实现的。根据 RFC 4291，全局单播地址必须满足以下条件：

1. 地址的第一个字节不能是 0x00、0x01、0x02、0x03、0x04、0x05、0x06、0x07、0x20、0x24、0x25、0x26、0x27、0x2a、0x2b、0x2c。
2. 地址不能是保留地址。
3. 地址不能是广播地址。
4. 地址不能是任何已知的多播地址。

根据这些规则，192.168.0.1 明显不是全局单播地址，因为它的第一个字节是 0xC0，不符合第一个规则。然而，如果操作系统的实现机制存在问题，就可能导致 `IP.IsGlobalUnicast()` 函数的实现出现差异，将其错误地判断为全局单播地址。

因此，我们建议您在编写代码时，要谨慎使用 `IP.IsGlobalUnicast()` 函数，最好结合其他 IP 地址类型的判断方法，以确保代码的准确性。

##  2 链路本地地址

链路本地地址（Link-Local Address）是指在单个链路上可用的 IPv6 地址，它只能在同一个链路内进行通信，无法跨越路由器进行通信。链路本地地址的前缀是 FE80::/10。

链路本地地址在 IPv6 网络中具有很重要的作用。它是 IPv6 自动配置机制中的一部分，用于自动分配 IPv6 地址。当一个设备连接到一个网络时，它可以使用链路本地地址进行通信，而无需进行任何配置。

链路本地地址还用于一些特殊的通信场景，例如邻居发现、路由器发现等。在这些场景中，设备可以使用链路本地地址与同一链路上的设备进行通信。

需要注意的是，链路本地地址不能够直接被路由器转发。如果需要在不同的链路上进行通信，则需要使用全局唯一地址（Global Unicast Address）。为了方便设备进行通信，IPv6 设备通常同时具有链路本地地址和全局唯一地址。

```go
func (ip IP) IsLinkLocalUnicast() bool
```

`IsLinkLocalUnicast()` 是一个 `net.IP` 类型的方法，用于判断 IPv6 地址是否为链路本地单播地址（Link-Local Unicast Address）。如果是，则返回 true，否则返回 false。

链路本地单播地址的特点是其地址的前缀是 FE80::/10。这种地址只能在本地链路内使用，不能被路由器转发。链路本地单播地址主要用于邻居发现、路由器发现和链路本地组播通信等场景。

示例代码：

```go
package main

import (
    "fmt"
    "net"
)

func main() {
    ip := net.ParseIP("fe80::a4a1:2a4f:fe78:d131")
    if ip.IsLinkLocalUnicast() {
        fmt.Printf("%s is a link-local unicast address\n", ip)
    } else {
        fmt.Printf("%s is not a link-local unicast address\n", ip)
    }
}

```

```shell
fe80::a4a1:2a4f:fe78:d131 is a link-local unicast address
```

## 3 链路组播地址

本地组播地址（Link-Local Multicast Address）是指只在一个本地链路上使用的组播地址。IPv6 的本地组播地址范围是 `FF02::/16`，这个地址范围内的地址是本地组播地址，只在同一链路上有效，不会通过路由器转发。

在 IPv6 中，本地组播地址被用于诸如邻居发现、路由器发现、DHCPv6 等协议中，以及一些本地应用程序的通信中。

本地组播地址的特点：

- 地址范围为 `FF02::/16`
- 地址的第 7 位固定为 1
- 地址的第 8 位有不同的取值，用于标识地址类型
- 地址的第 9 到 16 位是具体的组播地址

以下是几个常用的本地组播地址：

- `FF02::1`：所有节点
- `FF02::2`：所有路由器
- `FF02::9`：RIPng 协议
- `FF02::A`：EIGRP 协议
- `FF02::D`：PIMv2 协议

可以通过 `IsLinkLocalMulticast()` 方法判断一个 IPv6 地址是否为本地组播地址。例如：

```go
package main

import (
	"fmt"
	"net"
)

func main() {
	ip := net.ParseIP("ff02::1")
	if ip.IsLinkLocalMulticast() {
		fmt.Println(ip, "is a link-local multicast address")
	} else {
		fmt.Println(ip, "is not a link-local multicast address")
	}
}

```

```shell
ff02::1 is a link-local multicast address
```

## 4 本地组播地址

本地组播地址（Link-Local Multicast Address）是指只在一个本地链路上使用的组播地址。IPv6 的本地组播地址范围是 `FF02::/16`，这个地址范围内的地址是本地组播地址，只在同一链路上有效，不会通过路由器转发。

在 IPv6 中，本地组播地址被用于诸如邻居发现、路由器发现、DHCPv6 等协议中，以及一些本地应用程序的通信中。

本地组播地址的特点：

- 地址范围为 `FF02::/16`
- 地址的第 7 位固定为 1
- 地址的第 8 位有不同的取值，用于标识地址类型
- 地址的第 9 到 16 位是具体的组播地址

以下是几个常用的本地组播地址：

- `FF02::1`：所有节点
- `FF02::2`：所有路由器
- `FF02::9`：RIPng 协议
- `FF02::A`：EIGRP 协议
- `FF02::D`：PIMv2 协议

可以通过 `IsLinkLocalMulticast()` 方法判断一个 IPv6 地址是否为本地组播地址。例如：

```go
package main

import (
	"fmt"
	"net"
)

func main() {
	ip := net.ParseIP("ff02::1")
	if ip.IsLinkLocalMulticast() {
		fmt.Println(ip, "is a link-local multicast address")
	} else {
		fmt.Println(ip, "is not a link-local multicast address")
	}
}

```

## 5 组播地址

`IsMulticast()` 是一个 IP 类型的方法，用于判断一个 IP 地址是否为组播地址。

组播地址是一种特殊的 IP 地址，用于向一组主机发送数据，而不是只向一个特定的主机。IPv4 的组播地址范围是 `224.0.0.0/4`，其中 `224.0.0.0` 是预留地址，不能用于实际。

IPv6 的组播地址范围是 `ff00::/8`，其中 `ff02::1` 表示全局组播地址，`ff02::2` 表示本地链路组播地址，`ff02::5` 表示 Site-Local Scope 组播地址，`ff02::6` 表示 Link-Local Scope 组播地址。

可以通过 `IsMulticast()` 方法判断一个 IP 地址是否为组播地址。如果是组播地址，则该方法返回 `true`，否则返回 `false`。

## 6 环回地址

`IsLoopback()` 是一个 IP 类型的方法，用于判断一个 IP 地址是否为环回地址。

环回地址是一个特殊的 IP 地址，用于指代本机，常用的环回地址有：

- IPv4 的环回地址为 `127.0.0.1`
- IPv6 的环回地址为 `::1`

环回地址的特点：

- 地址范围为单个地址
- 用于本地回环测试和通信
- 不会被路由器转发

可以通过 `IsLoopback()` 方法判断一个 IP 地址是否为环回地址。如果是环回地址，则该方法返回 `true`，否则返回 `false`。

## 7 默认子网掩码

`DefaultMask()` 是一个 IP 类型的方法，用于获取默认子网掩码。

IPv4 的默认子网掩码为 `255.255.255.0`，IPv6 的默认子网掩码为 `ffff:ffff:ffff:ffff::`。如果要将一个 IP 地址分配到一个子网中，需要使用子网掩码对其进行掩码操作，以确定该地址是否属于该子网。如果该地址与子网地址进行 AND 操作后的结果等于子网地址，则该地址属于该子网。

可以通过 `DefaultMask()` 方法获取默认子网掩码。如果 IP 地址为 IPv4 类型，则返回 IPv4 默认子网掩码 `255.255.255.0` 对应的 IPMask 类型。如果 IP 地址为 IPv6 类型，则返回 IPv6 默认子网掩码 `ffff:ffff:ffff:ffff::` 对应的 IPMask 类型。

`Equal` 是 IP 类型的方法，用于判断两个 IP 是否相等。如果两个 IP 地址相等，则返回 true，否则返回 false。

IP 类型包含了 IPv4 和 IPv6 两种类型的 IP 地址。当比较两个 IP 地址时，如果两个地址类型不一致，则返回 false。如果两个地址类型相同，则根据地址值判断它们是否相等。

示例代码：

```go
package main

import (
    "fmt"
    "net"
)

func main() {
    ip1 := net.ParseIP("192.168.0.1")
    ip2 := net.ParseIP("192.168.0.1")
    ip3 := net.ParseIP("2001:db8::1")
    ip4 := net.ParseIP("2001:db8::2")

    fmt.Println(ip1.Equal(ip2)) // true
    fmt.Println(ip1.Equal(ip3)) // false
    fmt.Println(ip3.Equal(ip4)) // false
}

```

在上述示例中，我们创建了 4 个 IP 地址变量，其中 ip1 和 ip2 是相等的 IPv4 地址，ip3 和 ip4 是不相等的 IPv6 地址。通过 `Equal` 方法，我们可以比较它们是否相等。

## 8 返回子网地址

`func (ip IP) Mask(mask IPMask) IP` 方法返回将 `ip` 地址应用给定子网掩码 `mask` 后的结果地址。

示例代码：

```go
package main

import (
	"fmt"
	"net"
)

func main() {
	ip := net.ParseIP("192.168.0.1")
	mask := net.CIDRMask(24, 32)
	fmt.Println(ip.Mask(mask))
}

```

```shell
192.168.0.0
```

解释： 子网掩码为 `255.255.255.0`，对 `192.168.0.1` 进行应用，即保留其前 24 位，即 `192.168.0`，将最后 8 位设为 0，即得到 `192.168.0.0`。

# 二 掩码

```go
type IPMask []byte
```

## 1 CIRDMask

```go
func CIDRMask(ones, bits int) IPMask
```

`CIDRMask`函数根据`ones`参数返回IP地址子网掩码。

参数`ones`指定了子网掩码中1的个数，参数`bits`指定了IP地址的位数。

## 2 IPv4Mask

```go
func IPv4Mask(a, b, c, d byte) IPMask
```

`IPv4Mask(a, b, c, d byte) IPMask` 函数用于创建 IPv4 子网掩码。它将四个 `byte` 类型的参数作为参数，分别表示子网掩码中四个字节的值。例如，如果子网掩码是 `255.255.255.0`，则可以调用 `IPv4Mask(255, 255, 255, 0)` 来创建该子网掩码的 `IPMask` 值。

函数返回值是 `IPMask` 类型的子网掩码。 `IPMask` 类型是一个 `byte` 数组，其中数组的每个元素表示子网掩码中相应字节的值。在 IPv4 中，子网掩码通常为 4 个字节，因此 `IPMask` 类型具有 4 个元素。例如，子网掩码 `255.255.255.0` 的 `IPMask` 值为 `{255, 255, 255, 0}`。

## 3 位数

`func (m IPMask) Size() (ones, bits int)` 方法返回该IPMask中位的数目和总数，即它们表示的IP地址子网掩码的位数和总位数。对于IPv4，bits为32，对于IPv6，bits为128。ones是IPMask中值为1的位的数目。

具体实现中，该方法将IPMask中的每个字节拆分为位，并计算所有值为1的位的数量。

# 三 网络

```go
type IPNet struct {
    IP   IP     // 网络地址
    Mask IPMask // 子网掩码
}
```

## 1 ParseCIRD

`func ParseCIDR(s string) (IP, *IPNet, error)` 是一个函数，它解析一个 CIDR 格式的 IP 地址字符串，返回该 IP 地址、以及对应的网络。

函数的参数 `s` 是一个 CIDR 格式的 IP 地址字符串。函数会将该字符串解析为一个 IP 地址和一个 IP 网络对象。如果解析失败，函数会返回一个错误。

例如，对于以下的 IP 地址字符串和 IP 网络：

```go
ipString := "192.168.1.1/24"
```

可以使用如下代码进行解析：

```go
ip, ipNet, err := net.ParseCIDR(ipString)
if err != nil {
    fmt.Println("ParseCIDR error:", err)
} else {
    fmt.Println("IP:", ip)
    fmt.Println("IPNet:", ipNet)
}
```

该代码会输出以下内容：

```go
IP: 192.168.1.1
IPNet: 192.168.1.0/24
```

## 2 在吗

```go
func (n *IPNet) Contains(ip IP) bool
```

`Contains`方法判断给定的IP地址是否在该子网中，如果在该子网中返回true，否则返回false。

```go
func (n *IPNet) Contains(ip IP) bool {
    if len(ip) == len(n.IP) {
        for i := range ip {
            if (ip[i] & n.Mask[i]) != n.IP[i] {
                return false
            }
        }
        return true
    }
    return false
}
```

它的实现原理是将待检查的IP地址和子网掩码进行按位与操作，得到的结果应该与该子网的网络地址一致。如果一致，说明该IP地址在该子网中，否则说明不在。

# 四 Addr Conn

```go
type Addr interface {
    Network() string // 网络名
    String() string  // 字符串格式的地址
}
```

```go
type Conn interface {
    // Read从连接中读取数据
    // Read方法可能会在超过某个固定时间限制后超时返回错误，该错误的Timeout()方法返回真
    Read(b []byte) (n int, err error)
    // Write从连接中写入数据
    // Write方法可能会在超过某个固定时间限制后超时返回错误，该错误的Timeout()方法返回真
    Write(b []byte) (n int, err error)
    // Close方法关闭该连接
    // 并会导致任何阻塞中的Read或Write方法不再阻塞并返回错误
    Close() error
    // 返回本地网络地址
    LocalAddr() Addr
    // 返回远端网络地址
    RemoteAddr() Addr
    // 设定该连接的读写deadline，等价于同时调用SetReadDeadline和SetWriteDeadline
    // deadline是一个绝对时间，超过该时间后I/O操作就会直接因超时失败返回而不会阻塞
    // deadline对之后的所有I/O操作都起效，而不仅仅是下一次的读或写操作
    // 参数t为零值表示不设置期限
    SetDeadline(t time.Time) error
    // 设定该连接的读操作deadline，参数t为零值表示不设置期限
    SetReadDeadline(t time.Time) error
    // 设定该连接的写操作deadline，参数t为零值表示不设置期限
    // 即使写入超时，返回值n也可能>0，说明成功写入了部分数据
    SetWriteDeadline(t time.Time) error
}
```

## 1 Dial

```go
func Dial(network, address string) (Conn, error)
```

在网络network上连接地址address，并返回一个Conn接口。可用的网络类型有：

"tcp"、"tcp4"、"tcp6"、"udp"、"udp4"、"udp6"、"ip"、"ip4"、"ip6"、"unix"、"unixgram"、"unixpacket"

对TCP和UDP网络，地址格式是host:port或[host]:port，参见函数JoinHostPort和SplitHostPort。