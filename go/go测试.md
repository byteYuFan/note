# go testing

Go 测试主要包括以下几个方面的内容：

1. 单元测试：对于程序中的每个小模块进行测试，以保证其能够正常工作。
2. 性能测试：对于程序的关键模块进行测试，以保证其能够在合理的时间内完成。
3. 集成测试：对于程序中的各个组件进行测试，以保证它们能够协同工作。
4. 功能测试：对于程序中的各项功能进行测试，以保证其满足用户需求。
5. 冒烟测试：对于程序的主要功能进行测试，以保证其基本可用。
6. 回归测试：对于程序的修改进行测试，以保证其没有破坏已有的功能。

在 Go 中，单元测试和性能测试都是通过编写测试函数来实现的。同时，Go 还提供了一些辅助函数和工具，如 `testing.T` 结构体、`testing.B` 结构体、`go test` 命令等，以方便开发者进行测试工作。

## 1. test包介绍

Go语言中的testing包是用于编写单元测试的标准库。该包提供了一组用于编写测试函数的函数和类型，能够让开发人员轻松地编写单元测试并获取测试结果。testing包的核心是Test结构体，用于表示一个单元测试的元数据，包括测试名称、测试函数和测试状态等。下面是testing包中常用的函数和类型：

```go
1. testing.T：代表一个测试实例，提供了用于测试的方法和断言函数，例如Errorf、Fatal、Log等等。
2. testing.B：代表一个基准测试实例，提供了用于基准测试的方法和断言函数，例如N、ResetTimer、StopTimer等等。
3. testing.M：代表一个测试主程序，通常用于测试初始化和结束操作。
4. testing.Coverage：代表一份代码覆盖率报告，包括代码行数、覆盖率百分比等。
```



testing包提供了以下函数和方法来编写单元测试：

```go
1. func TestXxx(*testing.T)：编写单元测试函数。
2. func BenchmarkXxx(*testing.B)：编写基准测试函数。
3. func TestMain(m *testing.M)：编写测试主程序，可以在测试开始前执行一些初始化操作，例如打开数据库连接等等。
```

除了上述函数和方法，testing包还提供了一些用于比较和判断的函数，例如：

```go
1. func (t *T) Error(args ...interface{})：标记测试函数为失败，并输出错误信息。
2. func (t *T) Errorf(format string, args ...interface{})：格式化输出错误信息。
3. func (t *T) Fail()：标记测试函数为失败。
4. func (t *T) FailNow()：标记测试函数为失败，并中止测试。
5. func (t *T) Fatal(args ...interface{})：标记测试函数为失败，并退出程序。
6. func (t *T) Log(args ...interface{})：输出一条日志信息。
7. func (t *T) Name() string：返回当前测试的名称。
8. func (t *T) Skip(args ...interface{})：跳过当前测试。
```

`go test` 命令是 Go 语言自带的测试工具，用于执行测试文件或者包，并输出测试结果。

以下是 `go test` 命令的一些常用参数：

- `-v`：显示测试执行的详细信息，包括每个测试函数的执行结果和运行时间等。
- `-run regexp`：只运行名称与正则表达式 regexp 匹配的测试函数。
- `-cover`：显示测试代码覆盖率的百分比。
- `-coverprofile cover.out`：将测试覆盖率结果输出到指定文件 cover.out 中。
- `-count n`：指定测试的运行次数。
- `-parallel n`：指定同时运行的测试的数量。
- `-timeout duration`：指定测试运行的最大时长，超过此时长的测试将被中断。

一般情况下，我们可以使用以下命令来执行测试：

```go
go test [-v] [-cover] [-coverprofile cover.out] [packages] [-run regexp]
```

其中 `packages` 为测试目录或文件路径，可以使用相对路径或绝对路径，也可以是 Go 模块的包名，例如 `./pkg` 或 `github.com/myuser/mymodule/pkg`.

如果没有指定测试目录或文件，`go test` 会自动在当前目录下搜索所有以 `_test.go` 结尾的文件并执行测试。

## 2. 单元测试

测试斐波那契函数的可行性

```go
// 斐波那契数列函数
func Fibonacci(n int) int {
	if n <= 1 {
		return n
	}
	return Fibonacci(n-1) + Fibonacci(n-2)
}
```

```go
package util

import "testing"

// 单元测试函数
func TestFibonacci(t *testing.T) {
	// 测试用例
	testCases := []struct {
		n        int // 输入值
		expected int // 期望值
	}{
		{0, 0},
		{1, 1},
		{2, 1},
		{3, 2},
		{4, 3},
		{5, 5},
		{6, 8},
	}

	// 遍历测试用例进行测试
	for _, tc := range testCases {
		output := Fibonacci(tc.n)
		if output != tc.expected {
			t.Errorf("Fibonacci(%d) = %d; expected %d", tc.n, output, tc.expected)
		}
	}
}

```

```shell
$ go test -run TestFibonacci
PASS
ok      github.com/rabbitmq/util        0.846s
```

## 3. 基准测试

```go
func BenchmarkFibonacci(b *testing.B) {
	for i := 0; i < b.N; i++ {
		Fibonacci(30)
	}
}
```

```shell
$ go test -bench=BenchmarkFibonacci
goos: windows
goarch: amd64
pkg: github.com/rabbitmq/util
cpu: AMD Ryzen 7 4800U with Radeon Graphics         
BenchmarkFibonacci-16                178           6698897 ns/op
PASS
ok      github.com/rabbitmq/util        2.734s
```

在这个执行结果中，我们可以看到 `BenchmarkFibonacci` 的执行次数为 ` 178`，每次执行的平均时间为 `7.86 6698897 ns/op`。这个结果告诉我们，在当前环境下，执行斐波那契函数的平均时间约为6698897 纳秒。

```GO
func BenchmarkF(b *testing.B) {
	for i := 0; i < b.N; i++ {
		F(30)
	}
}
```

```shell
$ go test -bench=BenchmarkF
goos: windows
goarch: amd64
pkg: github.com/rabbitmq/util
cpu: AMD Ryzen 7 4800U with Radeon Graphics         
BenchmarkF-16                   45572446                26.01 ns/op
PASS
ok      github.com/rabbitmq/util        3.974s

```

在这个执行结果中，我们可以看到 `BenchmarkFibonacci` 的执行次数为 `  45572446 `，每次执行的平均时间为 `  26.01ns/op`。这个结果告诉我们，在当前环境下，执行斐波那契函数的平均时间约为  26.01 纳秒。

需要注意的是，基准测试的结果可能受到多种因素的影响，包括硬件性能、操作系统调度和 GC 等。因此，我们应该在相同的环境下多次执行基准测试，并取多次执行的平均值作为参考。