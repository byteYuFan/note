## 1. std::function

std::function 是 C++ 标准库中的一个模板类，用于包装和管理可调用对象（callable objects），包括函数、函数指针、成员函数指针、函数对象、Lambda 表达式等。它提供了一种通用的方式来表示和调用各种不同类型的可调用对象，从而增加了代码的灵活性和可复用性。

### 1. 绑定全局函数

```cpp
#include <iostream>
#include <functional>

int add(int a, int b) {
    return a + b;
}

int main() {
    std::function<int(int, int)> operation = add;
    int result = operation(3, 4);
    std::cout << "Result: " << result << std::endl;
    return 0;
}

```

### 2. 绑定成员函数

```cpp
#include <iostream>
#include <functional>

class MyClass {
public:
    void greet(const std::string& name) {
        std::cout << "Hello, " << name << "!" << std::endl;
    }
};

int main() {
    MyClass obj;
    auto member_func = std::bind(&MyClass::greet, &obj, "Bob");
    member_func(); // 调用 obj.greet("Bob")
    return 0;
}


```

### 3. 使用Lambda表达式

```cpp
#include <iostream>
#include <functional>

int main() {
    std::function<int(int, int)> operation = [](int a, int b) { return a * b; };
    int result = operation(3, 4);
    std::cout << "Result: " << result << std::endl;
    return 0;
}


```

### 4. 部分函数应用

```cpp
#include <iostream>
#include <functional>

int main() {
    std::function<int(int, int)> operation = [](int a, int b) { return a * b; };
    int result = operation(3, 4);
    std::cout << "Result: " << result << std::endl;
    return 0;
}

```

### 5. 函数适配器

```cpp
void test05() {
    std::vector<int> numbers = {3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5};
    int target = 5;

    // 使用 std::count_if 和函数适配器，计算大于 target 的元素个数
    std::function<bool(int)> isGreaterThanTarget = [target](auto &&PH1) {
        return std::less<int>()(std::forward<decltype(PH1)>(PH1), target);
    };
    int count = std::count_if(numbers.begin(), numbers.end(), isGreaterThanTarget);

    std::cout << "Count: " << count << std::endl;
}
```

### 6. 多态行为

```cpp
#include <iostream>
#include <functional>

class Animal {
public:
    virtual void speak() const = 0;
};

class Dog : public Animal {
public:
    void speak() const override {
        std::cout << "Woof!" << std::endl;
    }
};

class Cat : public Animal {
public:
    void speak() const override {
        std::cout << "Meow!" << std::endl;
    }
};

int main() {
    std::function<void(const Animal&)> talk = [](const Animal& animal) {
        animal.speak();
    };

    Dog dog;
    Cat cat;

    talk(dog); // 输出 "Woof!"
    talk(cat); // 输出 "Meow!"

    return 0;
}

```

### 7. 事件处理

```cpp
#include <iostream>
#include <functional>
#include <vector>

class Event {
public:
    using EventHandler = std::function<void()>;

    void addHandler(const EventHandler& handler) {
        handlers.push_back(handler);
    }

    void fire() {
        for (const auto& handler : handlers) {
            handler();
        }
    }

private:
    std::vector<EventHandler> handlers;
};

int main() {
    Event event;
    event.addHandler([]() { std::cout << "Event handler 1" << std::endl; });
    event.addHandler([]() { std::cout << "Event handler 2" << std::endl; });

    event.fire(); // 触发事件，调用注册的事件处理器

    return 0;
}
```

### 8. 回调函数

```cpp
#include <iostream>
#include <functional>
#include <thread>

void asyncOperation(std::function<void()> callback) {
    // 模拟异步操作
    std::this_thread::sleep_for(std::chrono::seconds(2));
    // 完成后调用回调函数
    callback();
}

int main() {
    asyncOperation([]() {
        std::cout << "Async operation completed." << std::endl;
    });

    // 在异步操作完成之前继续执行其他任务

    return 0;
}
```

### 9. 函数组合

```cpp
#include <iostream>
#include <functional>

int add(int a, int b) {
    return a + b;
}

int subtract(int a, int b) {
    return a - b;
}

int main() {
    std::function<int(int, int)> add_func = add;
    std::function<int(int, int)> subtract_func = subtract;

    std::function<int(int, int)> combined_func = [&](int x, int y) {
        return subtract_func(add_func(x, y), y);
    };

    int result = combined_func(5, 3);
    std::cout << "Result: " << result << std::endl; // 输出 "Result: 5"
    return 0;
}
```

### 10. 函数参数化

```cpp
#include <iostream>
#include <functional>

void performOperation(int a, int b, std::function<int(int, int)> operation) {
    int result = operation(a, b);
    std::cout << "Result: " << result << std::endl;
}

int main() {
    std::function<int(int, int)> add_func = [](int x, int y) { return x + y; };
    std::function<int(int, int)> multiply_func = [](int x, int y) { return x * y; };

    performOperation(5, 3, add_func); // 输出 "Result: 8"
    performOperation(5, 3, multiply_func); // 输出 "Result: 15"
    return 0;
}

```

### 11. 函数重载

```cpp
#include <iostream>
#include <functional>

int add(int a, int b) {
    return a + b;
}

double add(double a, double b) {
    return a + b;
}

int main() {
    std::function<int(int, int)> int_add_func = add;
    std::function<double(double, double)> double_add_func = add;

    int result1 = int_add_func(5, 3);
    double result2 = double_add_func(2.5, 3.7);

    std::cout << "Result 1: " << result1 << std::endl; // 输出 "Result 1: 8"
    std::cout << "Result 2: " << result2 << std::endl; // 输出 "Result 2: 6.2"
    return 0;
}
```

### 4. 函数动态调用

```cpp
#include <iostream>
#include <functional>

int add(int a, int b) {
    return a + b;
}

int subtract(int a, int b) {
    return a - b;
}

int main() {
    std::function<int(int, int)> selected_func;

    bool use_addition = true;
    if (use_addition) {
        selected_func = add;
    } else {
        selected_func = subtract;
    }

    int result = selected_func(5, 3); // 动态选择要调用的函数
    std::cout << "Result: " << result << std::endl; // 输出 "Result: 8"
    return 0;
}
```

## 2. Lambda表达式

Lambda 表达式是 C++11 引入的一项重要特性，允许你在代码中定义匿名函数，这些函数可以像普通函数一样使用。Lambda 表达式通常用于创建临时的、局部的函数对象，以便更灵活地处理一些任务，例如函数传递、算法操作等。

### Lambda 表达式的基本语法

Lambda 表达式的基本语法如下：

```cpp
[capture_clause] (parameter_list) -> return_type {
    // Lambda 函数体
}
```

- `capture_clause`：捕获列表，用于指定在 Lambda 函数中可以访问的外部变量。捕获列表可以为空，也可以包含变量名，如 `[x, y]`，表示捕获变量 `x` 和 `y`。捕获列表还可以使用引用捕获（`[&x, y]`）或按值捕获（`[=]`）的方式。
- `parameter_list`：参数列表，与普通函数的参数列表类似，用于指定 Lambda 函数的参数。
- `return_type`：返回类型，用于指定 Lambda 函数的返回类型。如果省略，编译器会根据函数体的返回语句自动推断返回类型。
- Lambda 函数体：包含实际执行的代码。

### **Lambda 表达式作为函数对象**：

```cpp
#include <iostream>
#include <vector>
#include <algorithm>

int main() {
    std::vector<int> numbers = {3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5};

    // 使用 Lambda 表达式作为排序函数
    std::sort(numbers.begin(), numbers.end(), [](int a, int b) {
        return a < b;
    });

    // 使用 Lambda 表达式作为输出函数
    std::for_each(numbers.begin(), numbers.end(), [](int num) {
        std::cout << num << " ";
    });

    return 0;
}
```

在这个示例中，Lambda 表达式被用作排序函数和输出函数，用于对整数向量进行排序和输出。

### **Lambda 表达式与标准库算法**：

```cpp
#include <iostream>
#include <vector>
#include <algorithm>

int main() {
    std::vector<int> numbers = {3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5};

    // 使用 Lambda 表达式和 std::count_if 统计大于 4 的元素个数
    int count = std::count_if(numbers.begin(), numbers.end(), [](int num) {
        return num > 4;
    });

    std::cout << "Count: " << count << std::endl;

    return 0;
}
```

在这个示例中，Lambda 表达式与 `std::count_if` 算法一起使用，用于统计大于 4 的元素个数。

### **Lambda 表达式作为回调函数**：

```cpp
#include <iostream>
#include <functional>

void performOperation(int a, int b, std::function<void(int, int)> operation) {
    operation(a, b);
}

int main() {
    performOperation(5, 3, [](int x, int y) {
        std::cout << "Sum: " << x + y << std::endl;
    });

    return 0;
}
```

在这个示例中，Lambda 表达式被传递给 `performOperation` 函数，用作回调函数，执行两个整数的求和操作。

### **Lambda 表达式与范围 `for` 循环**：

```cpp
#include <iostream>
#include <vector>

int main() {
    std::vector<int> numbers = {3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5};

    // 使用 Lambda 表达式和范围 for 循环遍历容器元素
    for (int num : numbers) {
        std::cout << num << " ";
    }

    return 0;
}
```

这个示例展示了如何使用 Lambda 表达式和范围 `for` 循环来遍历容器中的元素并输出它们。

### Lambda 表达式捕获外部变量**：

```cpp
#include <iostream>

int main() {
    int x = 5;

    auto lambda = [x]() {
        std::cout << "Captured variable x: " << x << std::endl;
    };

    lambda();

    return 0;
}
```
