# Context上下文

在Go语言中，Context（上下文）是一个类型，用于在程序中传递请求范围的值、截止时间、取消信号和其他与请求相关的上下文信息。它在多个goroutine之间传递这些值，使得并发编程更加可靠和简单。

Context的出现是为了解决在大型应用程序中的并发环境下，协调和管理多个goroutine之间的通信、超时和取消操作的问题。它提供了一种标准化的机制，以便在程序的不同部分之间传递请求相关的值，并且可以在整个调用链中传播和取消这些值。

Context的主要目的是：

1. 传递请求范围的值：通过Context，可以在不同的函数调用中传递请求相关的值，例如请求ID、用户认证信息、日志记录器等。这样可以避免在函数之间显式传递这些值，使代码更加清晰简洁。
2. 控制并发操作：通过Context的取消信号，可以通知相关的goroutine停止运行并返回，从而实现对并发操作的控制。这对于处理长时间运行的操作或避免资源泄漏非常有用。
3. 设置截止时间：Context允许为操作设置截止时间，超过该时间则自动取消相关的操作。这对于避免长时间等待或超时的情况非常有用，可以提高系统的可靠性和性能。
4. 传播和继承：通过Context，可以在整个调用链中传播和继承请求范围的值和取消信号，而无需显式地传递它们。这样可以减少代码中的重复操作，并确保所有相关的goroutine都能收到相同的上下文信息。

总而言之，Context的出现是为了提供一种统一的机制，用于管理并发操作、传递请求相关的值和控制操作的超时和取消。它简化了并发编程模型，提高了代码的可读性、可维护性和可测试性。

## 1. Context接口定义

```go
type Context interface {
  Deadline() (deadline time.Time, ok bool)
  Done <-chan struct{}
  Err() error
  Value(key interface{}) interface{}
}
```

1. `Deadline() (deadline time.Time, ok bool)`：

   方法功能： Deadline方法返回代表此上下文中的工作应该被取消的时间。当没有设置截止时间时，Deadline方法返回ok==false。连续调用Deadline方法将返回相同的结果：

   - `deadline`：表示Context的截止时间，如果没有设置截止时间或截止时间已过，则返回零值Deadline方法返回ok==false。
   - `ok`：布尔值，指示截止时间是否存在。如果存在截止时间，则为`true`；否则为`false`。

2. `Done() <-chan struct{}`：

   方法功能：返回一个只读的通道（`<-chan struct{}`），该通道在Context被取消或过期时关闭。

   返回值：返回一个只读的通道，可以通过该通道接收到Context的取消或过期信号。

3. `Err() error`：

   方法功能：返回Context被取消的原因（错误信息）。

   返回值：

   - 如果Context已被取消，返回一个非空的错误对象，描述取消的原因。
   - 如果Context尚未被取消，或者取消原因未知，则返回`nil`。

4. `Value(key interface{}) interface{}`：

   方法功能：根据给定的键（key），返回与Context相关联的值。

   参数：`key`表示要检索的值的键。

   返回值：

   - 如果Context关联的值存在，则返回与给定键关联的值（类型为`interface{}`）。
   - 如果不存在与给定键关联的值，则返回`nil`。

## 2. 错误设置

```go
// Canceled is the error returned by Context.Err when the context is canceled.
var Canceled = errors.New("context canceled")

// DeadlineExceeded is the error returned by Context.Err when the context's
// deadline passes.
var DeadlineExceeded error = deadlineExceededError{}

type deadlineExceededError struct{}

func (deadlineExceededError) Error() string   { return "context deadline exceeded" }
func (deadlineExceededError) Timeout() bool   { return true }
func (deadlineExceededError) Temporary() bool { return true }

```

在上述代码中，定义了两个预定义的错误变量：Canceled和DeadlineExceeded，用于表示上下文取消和超时。

`Canceled`是在上下文被取消时由`Context.Err`返回的错误。它是一个`errors.New`创建的错误，表示上下文已被取消。

`DeadlineExceeded`是在上下文的截止时间过去时由`Context.Err`返回的错误。它是一个自定义的错误类型`deadlineExceededError`的实例。该类型实现了`error`接口的方法。

- `Error()`方法返回表示上下文截止时间已过的错误字符串，即"context deadline exceeded"。
- `Timeout()`方法返回`true`，指示该错误是由于超时引起的。
- `Temporary()`方法返回`true`，指示该错误是临时性的。

## 3. emptyCtx

```go
type emptyCtx int

func (*emptyCtx) Deadline() (deadline time.Time, ok bool) {
	return
}

func (*emptyCtx) Done() <-chan struct{} {
	return nil
}

func (*emptyCtx) Err() error {
	return nil
}

func (*emptyCtx) Value(key any) any {
	return nil
}

func (e *emptyCtx) String() string {
	switch e {
	case background:
		return "context.Background"
	case todo:
		return "context.TODO"
	}
	return "unknown empty Context"
}
```

`emptyCtx`是一个空的上下文类型。它具有以下特点：

- 永远不会被取消：`emptyCtx`是一个不可取消的上下文，即没有任何操作会导致它被取消。
- 没有值：`emptyCtx`不存储任何与其关联的值。
- 没有截止时间：`emptyCtx`没有设置任何截止时间，即没有截止时间的限制。

`emptyCtx`的类型不是`struct{}`，因为这样的变量必须具有不同的地址。实际上，`emptyCtx`是一个内部类型，用于表示一个特殊的空上下文。

该空上下文在一些特殊情况下使用，例如作为根上下文或默认上下文，在没有显式提供上下文的情况下，可以使用它来代替。由于其不可取消、没有值和截止时间的特性，它在某些场景下提供了一个空的占位符上下文实例。

## 4. 两个emptyCtx

```go

var (
	background = new(emptyCtx)
	todo       = new(emptyCtx)
)

func Background() Context {
	return background
}

func TODO() Context {
	return todo
}

```

### 4.1. Background

`Background`函数返回一个非空的空上下文。它具有以下特点：

- 永远不会被取消：`Background`上下文是一个不可取消的上下文，即没有任何操作会导致它被取消。
- 没有值：`Background`上下文不存储任何与其关联的值。
- 没有截止时间：`Background`上下文没有设置任何截止时间，即没有截止时间的限制。

`Background`上下文是一个常用的上下文实例，通常用于主函数、初始化过程、测试以及作为传入请求的顶级上下文。它提供了一个空的占位符上下文，适用于不需要具体上下文的场景。由于其不可取消、没有值和截止时间的特性，`Background`上下文在启动程序、进行初始化操作以及处理入站请求时经常被使用。

### 4.2. TODO

`TODO`函数返回一个非空的空上下文。在代码中，当不清楚使用哪个上下文或者上下文尚不可用（因为周围的函数尚未被扩展为接受上下文参数）时，应使用`context.TODO`。

`TODO`上下文是一个临时的占位符上下文，用于表示上下文尚未确定或不可用的情况。它可以作为编码过程中的一种暂时解决方案，在代码进一步完善之前使用。当需要传递上下文但还没有明确选择使用哪个上下文时，可以使用`TODO`来占位，以后根据具体情况进行替换。

## 5. CancleFun

```go
// A CancelFunc tells an operation to abandon its work.
// A CancelFunc does not wait for the work to stop.
// A CancelFunc may be called by multiple goroutines simultaneously.
// After the first call, subsequent calls to a CancelFunc do nothing.
type CancelFunc func()
```

`CancelFunc`是一个函数类型，用于通知某个操作放弃其工作。`CancelFunc`不会等待工作停止，它仅仅是发送一个取消信号。`CancelFunc`可以被多个 goroutine 同时调用。第一次调用之后，对 `CancelFunc` 的后续调用不会产生任何效果。

当需要取消某个操作时，可以调用 `CancelFunc` 函数，以通知相关的操作停止工作。这个函数类型可以与 `context.WithCancel`、`context.WithDeadline`、`context.WithTimeout` 等函数一起使用，这些函数在创建派生的上下文时会返回一个 `CancelFunc`。

需要注意的是，调用 `CancelFunc` 只是向操作发送一个取消信号，具体的操作是否真正停止取决于操作本身的实现。`CancelFunc` 的调用不会阻塞，它会立即返回。

在使用 `CancelFunc` 时，应注意并发调用的情况，因为它可以被多个 goroutine 同时调用。确保在并发情况下正确处理取消操作，以避免潜在的竞态条件和问题。

## 6. cancleCtx

```go
type cancelCtx struct {
	Context

	mu       sync.Mutex            // protects following fields
	done     atomic.Value          // of chan struct{}, created lazily, closed by first cancel call
	children map[canceler]struct{} // set to nil by the first cancel call
	err      error                 // set to non-nil by the first cancel call
	cause    error                 // set to non-nil by the first cancel call
}
```

`cancelCtx` 是 `context` 包中定义的一个结构体类型，实现了 `Context` 接口。它是基于取消机制的上下文类型，用于表示可以被取消的上下文。

下面是 `cancelCtx` 结构体的详细介绍：

- `Context`：嵌入字段，表示 `cancelCtx` 结构体实现了 `Context` 接口，可以被用作上下文对象。
- `mu`：`sync.Mutex` 类型的互斥锁，用于保护以下字段的并发访问。
- `done`：`atomic.Value` 类型的原子值，用于存储一个 `chan struct{}`，该通道在首次取消调用时被关闭。该字段是惰性创建的，即在首次取消调用之前为 `nil`。它用于通知相关的 goroutine 上下文已被取消。
- `children`：`map[canceler]struct{}` 类型的字段，用于存储与该上下文关联的子上下文（通过 `WithCancel`、`WithDeadline` 或 `WithTimeout` 创建）。子上下文被存储在该映射中作为键，对应的值为空结构。在首次取消调用后，该字段会被设置为 `nil`。
- `err`：`error` 类型的字段，用于存储上下文的取消错误。在首次取消调用后，该字段会被设置为非 `nil` 的错误值。
- `cause`：`error` 类型的字段，用于存储上下文的取消原因。在首次取消调用后，该字段会被设置为非 `nil` 的错误值。

`cancelCtx` 结构体用于实现上下文的取消机制。当调用 `cancel` 方法时，会通过关闭 `done` 通道来通知相关的 goroutine 上下文已被取消。同时，会设置 `err` 字段为取消错误，并记录取消原因（如果提供了）。子上下文也会被取消，即它们的 `cancel` 方法会被调用，并将自身从 `children` 映射中删除。

这种基于取消机制的上下文类型可以用于在多个 goroutine 之间传递取消信号，使得相关的操作可以在需要时及时终止。

## 7. WithCancel

```go
func WithCancel(parent Context) (ctx Context, cancel CancelFunc) {
	c := withCancel(parent)
	return c, func() { c.cancel(true, Canceled, nil) }
}
```

`WithCancel` 函数的主要特点和步骤：

- 返回一个基于父上下文的副本，并创建一个新的 `Done` 通道。
- 当调用返回的 `cancel` 函数或者父上下文的 `Done` 通道关闭时，返回的上下文的 `Done` 通道也会被关闭。
- 调用 `cancel` 函数会释放与上下文相关的资源，因此在操作完成后应尽快调用。
- 使用 `WithCancel` 创建的上下文可以手动取消操作，并确保及时释放资源。\

```go
func Cancel() {
	// 创建一个带有取消功能的上下文
	ctx, cancel := context.WithCancel(context.Background())

	// 启动一个 goroutine 来执行定时任务
	go func() {
		for {
			select {
			case <-ctx.Done():
				fmt.Println("定时任务被取消")
				return
			default:
				// 模拟定时任务的工作
				fmt.Println("执行定时任务...")
				time.Sleep(1 * time.Second)
			}
		}
	}()

	// 模拟等待一段时间后取消定时任务
	time.Sleep(5 * time.Second)
	cancel()

	// 等待一段时间以观察任务的状态
	time.Sleep(2 * time.Second)
}

```

```shell
wangyufan@wangcomputerair MINGW64 /d/goworkplace/src/github.com/context (master)
$ go run .
执行定时任务...
执行定时任务...
执行定时任务...
执行定时任务...
执行定时任务...
定时任务被取消

```

在这个例子中，我们创建了一个带有取消功能的上下文(`ctx`)和对应的取消函数(`cancel`)。然后，我们启动了一个 goroutine 来执行定时任务，每隔一秒钟输出一次"执行定时任务..."。在主函数中，我们等待了5秒钟后调用`cancel`函数，发送取消信号。最后，我们等待2秒钟以观察任务的状态。

通过运行这个示例，你可以观察到在取消信号发送后，定时任务会立即停止执行，输出"定时任务被取消"，而不会继续执行剩余的定时任务。这展示了使用`context.WithCancel()`取消任务的现象明显的例子

## 8. WithDeadline

```go
func WithDeadline(parent Context, d time.Time) (Context, CancelFunc){}
```

`WithDeadline` 函数返回一个基于父上下文 `parent` 的副本，并设置一个截止时间 `d`。返回的上下文对象具有一个新的 `Done` 通道，当截止时间到达或者父上下文的 `Done` 通道关闭时（以先发生者为准），该 `Done` 通道将被关闭。

取消该上下文会释放与其相关联的资源，因此，在使用该上下文执行的操作完成后，代码应尽快调用 `cancel` 函数。

`WithDeadline` 函数的作用是创建一个带有截止时间的上下文。可以使用该上下文来控制操作的执行时间，一旦截止时间到达，相关操作可以被取消或中止。

需要注意的是，截止时间是一个绝对时间，可以使用 `time.Now()` 结合 `time.Duration` 来指定一个相对于当前时间的截止时间。

`WithDeadline` 函数的主要特点和步骤如下：

- 返回一个基于父上下文的副本，并设置截止时间为 `d`。
- 创建一个新的 `Done` 通道，当截止时间到达或者父上下文的 `Done` 通道关闭时，该 `Done` 通道将被关闭。
- 调用 `cancel` 函数会释放与上下文相关的资源，因此在操作完成后应尽快调用。
- 使用 `WithDeadline` 创建的上下文可以控制操作的执行时间，并在截止时间到达时取消或中止相关操作。

```go
func Dead() {
	ctx, cancel := context.WithDeadline(context.Background(), time.Now().Add(5*time.Second))

	// 启动一个 goroutine 来执行任务
	go func() {
		for {
			select {
			case <-ctx.Done():
				fmt.Println("任务被取消：", ctx.Err())
				return
			default:
				// 模拟任务的工作
				fmt.Println("执行任务...")
				time.Sleep(1 * time.Second)
			}
		}
	}()

	// 等待一段时间以观察任务的状态
	time.Sleep(8 * time.Second)

	// 取消任务
	cancel()

	// 等待一段时间以观察任务的状态
	time.Sleep(2 * time.Second)
}
```

```shell
wangyufan@wangcomputerair MINGW64 /d/goworkplace/src/github.com/context (master)
$ go run .
执行任务...
执行任务...
执行任务...
执行任务...
执行任务...
任务被取消： context deadline exceeded

```

在这个示例中，我们使用`context.WithDeadline()`创建了一个具有截止时间的上下文(`ctx`)和对应的取消函数(`cancel`)。通过调用`time.Now().Add(5*time.Second)`，我们设置了截止时间为当前时间5秒后。然后，我们启动了一个 goroutine 来执行任务，每隔一秒钟输出一次"执行任务..."。在主函数中，我们等待了8秒钟，超过了截止时间，然后调用`cancel`函数取消任务。最后，我们等待2秒钟以观察任务的状态。

通过运行这个示例，你可以观察到在截止时间到达后，任务会立即停止执行，并输出"任务被取消"。这展示了使用`context.WithDeadline()`设置截止时间并取消任务的示例。

## 9. WithTimeOut

```go
func WithTimeout(parent Context, timeout time.Duration) (Context, CancelFunc) {
	return WithDeadline(parent, time.Now().Add(timeout))
}
```

`WithTimeout` 函数是 `context` 包中的一个辅助函数，它基于父上下文 `parent` 和超时时间 `timeout` 创建一个新的上下文，并返回该上下文以及对应的取消函数。

函数的内部实现是调用了 `WithDeadline` 函数，将当前时间加上超时时间得到截止时间，然后将截止时间作为参数调用 `WithDeadline`，返回相应的上下文和取消函数。

简而言之，`WithTimeout` 函数是使用相对于当前时间的超时时间来创建一个带有截止时间的上下文。超时时间可以是一个持续时间（`time.Duration`）对象，表示从当前时间开始的一段时间。

使用 `WithTimeout` 函数可以方便地创建一个具有超时控制的上下文，以确保在超时时间到达后相关操作可以被取消或中止。

需要注意的是，超时时间应该是一个非负值。如果超时时间为零或负值，表示立即超时，即操作将立即取消。

```go
// TimeOut the function that will be testing the context.WithTimeout
func TimeOut() {
	// 设置一个超时时间为5秒的上下文
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)

	// 启动一个 goroutine 来执行任务
	go func() {
		for {
			select {
			case <-ctx.Done():
				fmt.Println("任务被取消：", ctx.Err())
				return
			default:
				// 模拟任务的工作
				fmt.Println("执行任务...")
				time.Sleep(1 * time.Second)
			}
		}
	}()

	// 等待一段时间以观察任务的状态
	time.Sleep(8 * time.Second)

	// 取消任务
	cancel()

	// 等待一段时间以观察任务的状态
	time.Sleep(2 * time.Second)
}

```

```shell
wangyufan@wangcomputerair MINGW64 /d/goworkplace/src/github.com/context (master)
$ go run .
执行任务...
执行任务...
执行任务...
执行任务...
执行任务...
任务被取消： context deadline exceeded

```

在这个示例中，我们使用`context.WithTimeout()`创建了一个具有超时时间的上下文(`ctx`)和对应的取消函数(`cancel`)。通过设置超时时间为5秒(`5*time.Second`)，我们限定了任务的执行时间。然后，我们启动了一个 goroutine 来执行任务，每隔一秒钟输出一次"执行任务..."。在主函数中，我们等待了8秒钟，超过了超时时间，然后调用`cancel`函数取消任务。最后，我们等待2秒钟以观察任务的状态。

通过运行这个示例，你可以观察到在超时时间到达后，任务会立即停止执行，并输出"任务被取消"。这展示了使用`context.WithTimeout()`设置超时时间并取消任务的示例。

## 10. WithValue

```go
func WithValue(parent Context, key, val any) Context {
	if parent == nil {
		panic("cannot create context from nil parent")
	}
	if key == nil {
		panic("nil key")
	}
	if !reflectlite.TypeOf(key).Comparable() {
		panic("key is not comparable")
	}
	return &valueCtx{parent, key, val}
}
```

`WithValue` 函数是 `context` 包中的一个辅助函数，用于基于父上下文 `parent` 创建一个新的上下文，并将键值对 `(key, val)` 存储在新上下文中。函数返回新的上下文对象。

函数首先进行了一些参数校验，确保 `parent` 不为空，`key` 不为 `nil`，且 `key` 是可比较的（comparable）。在 Go 语言中，可比较的类型是指可以使用 `==` 运算符进行比较的类型。

然后，函数创建了一个 `valueCtx` 结构体，并将父上下文、`key` 和 `val` 存储在该结构体中。`valueCtx` 是 `context` 包中定义的一个内部类型，用于存储上下文的键值对信息。

最后，函数返回新创建的 `valueCtx` 对象，它实现了 `Context` 接口。

通过使用 `WithValue` 函数，可以在上下文中存储和传递与请求相关的数据，这些数据可以被跨 API 边界和进程边界传递。需要注意的是，`WithValue` 函数适用于传递请求范围的数据，而不应该被用于传递可选的函数参数。

```go
func Test() {
	// 创建一个父级上下文
	parent := context.Background()

	// 使用 WithValue 创建一个带有用户身份信息的子级上下文
	user := User{ID: 123, Name: "Alice"}
	ctx := context.WithValue(parent, "user", user)

	// 在不同的函数中获取用户身份信息
	processRequest(ctx)
}

// processRequest a function that get information from ctx
func processRequest(ctx context.Context) {
	// 从上下文中获取用户身份信息
	user, ok := ctx.Value("user").(User)
	if !ok {
		fmt.Println("无法获取用户身份信息")
		return
	}

	// 使用用户身份信息执行请求处理
	fmt.Printf("处理请求，用户ID: %d, 用户名: %s\n", user.ID, user.Name)

	// 调用其他函数传递上下文
	otherFunction(ctx)
}

// otherFunction another function that get information form ctx
func otherFunction(ctx context.Context) {
	// 从上下文中获取用户身份信息
	user, ok := ctx.Value("user").(User)
	if !ok {
		fmt.Println("无法获取用户身份信息")
		return
	}

	// 使用用户身份信息执行其他操作
	fmt.Printf("执行其他操作，用户ID: %d, 用户名: %s\n", user.ID, user.Name)
}

```

```shell
wangyufan@wangcomputerair MINGW64 /d/goworkplace/src/github.com/context (master)
$ go run .
处理请求，用户ID: 123, 用户名: Alice
执行其他操作，用户ID: 123, 用户名: Alice
```

在这个例子中，我们首先创建了一个父级上下文`parent`。然后，我们使用`context.WithValue()`将用户身份信息`User{ID: 123, Name: "Alice"}`与上下文关联，创建了一个带有用户身份信息的子级上下文`ctx`。接下来，我们通过调用`processRequest(ctx)`将子级上下文传递给处理请求的函数。

在`processRequest`函数中，我们从上下文中获取用户身份信息，并使用该信息执行请求处理。然后，我们调用`otherFunction(ctx)`将上下文传递给另一个函数。

在`otherFunction`函数中，我们同样从上下文中获取用户身份信息，并使用该信息执行其他操作。

通过运行这个例子，你可以观察到在不同的函数中成功获取到了用户身份信息，并使用该信息进行相应的处理和操作。这展示了如何使用`context.WithValue()`将用户身份信息与上下文关联，并在不同的函数中传递和获取这些信息。

[本文的源代码](https://github.com/byteYuFan/Go/blob/master/context/context.go)