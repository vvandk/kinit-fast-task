## 使用 TypeVar 和实体类型的区别

使用 `TypeVar` 创建的类型变量，如 `SchemaUserModel = TypeVar("SchemaUserModel", bound=UserModel)`，和直接使用 `UserModel` 类型标注确实在许多情况下有类似的效果，但它们在使用上和意图上存在一些细微的差异。下面我将解释两者之间的区别和适用场景。

### 直接使用 `UserModel`

在你的示例中，当函数 `user_put` 参数的类型直接指定为 `UserModel` 时，这表明该函数接受 `UserModel` 或其任何子类的实例。这是多态的一种直接体现，允许任何继承自 `UserModel` 的类的实例作为参数。这种方式简单明了，对于大多数需要多态性的情况已经足够。

### 使用 `TypeVar` 绑定到 `UserModel`

当你使用 `TypeVar` 并将其绑定到 `UserModel`：

```python
SchemaUserModel = TypeVar("SchemaUserModel", bound=UserModel)
```

这种方式定义了一个类型变量，这个变量被限制为 `UserModel` 或其子类的实例。在表面上，这似乎与直接使用 `UserModel` 相同。然而，使用 `TypeVar` 的主要优势在于它提供了更高的灵活性和表达能力，尤其是在定义泛型类或函数时更为重要。例如：

- **泛型函数或类**：如果你正在定义一个泛型函数或泛型类，其中涉及多个参数或返回类型与该类型变量相关，使用 `TypeVar` 可以确保这些相关类型之间保持一致。例如，你可能想要保证某个函数的输入和输出类型相同，或者确保两个不同参数是相同的类型。
- **更复杂的类型关系**：`TypeVar` 允许定义涉及多个约束的复杂类型关系，这在直接使用基类作为类型时无法实现。

### 示例

考虑下面的泛型函数示例，它使用了 `TypeVar`：

```python
codeT = TypeVar('T', bound=UserModel)

def process_user(user: T) -> T:
    print(user.name)
    return user
```

在这个例子中，`process_user` 保证输入类型和返回类型是相同的。这意味着如果你传入一个 `SonUserModel` 实例，返回的也会是 `SonUserModel` 类型的实例。这种类型保持是直接使用 `UserModel` 无法确保的。

### 结论

尽管在很多简单场景中直接使用 `UserModel` 和使用绑定到 `UserModel` 的 `TypeVar` 效果相似，但 `TypeVar` 提供了更高级的类型操作，特别是在需要维护类型一致性的复杂泛型编程中。直接使用 `UserModel` 更简单直接，适合大多数情况。选择使用哪种方式取决于你的具体需求和预期的代码复用级别。



## 真实案例

```python
from typing import TypeVar


class UserModel:

    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age


class SonUserModel(UserModel):

    def __init__(self, name: str, age: int, gender: str = 'male'):
        super().__init__(name, age)
        self.gender = gender


def user_1(data: UserModel) -> UserModel:
    print(data.name)
    print(data.age)
    return data

    
# 定义类型变量，这个变量被限制为 UserModel 或其子类的实例
UserModelSchema = TypeVar("UserModelSchema", bound=UserModel)


def user_2(data: UserModelSchema) -> UserModelSchema:
    print(data.name)
    print(data.age)
    return data


if __name__ == '__main__':
    _user_1 = SonUserModel(name="John", age=18)
    user_1(_user_1)

    _user_2 = SonUserModel(name="John", age=18, gender='male')
    user_2(_user_2)
```



### 实体类型

在以上代码示例中，`user_1` 函数的参数 `data` 类型被指定为 `UserModel` 类。

**在Python中，这意味着 `user_1` 函数可以接受任何类型为 `UserModel` 或其任何子类的实例。**

这是因为Python的类型系统支持多态，其中子类的实例可以被视为其父类的实例。

**这是面向对象编程中的一个基本原则，称为“里氏替换原则”（Liskov Substitution Principle），即子类对象应该能够替换其父类对象被使用，而不影响程序的正确性。**

返回类型同样为为 `UserModel` 或其任何子类的实例。

**可接受的类型**

由于 `SonUserModel` 是 `UserModel` 的子类，因此以下类型的实例都可以作为参数传递给 `user_put` 函数：

- `UserModel` 的实例。
- `SonUserModel` 的实例，或任何其他从 `UserModel` 继承的子类的实例。

这表明你可以用 `UserModel` 以及任何继承自 `UserModel` 的类的实例来调用 `user_1` 函数。由于 `SonUserModel` 扩展了 `UserModel`（增加了 `gender` 属性并保留了从 `UserModel` 继承的属性和方法），`SonUserModel` 的实例在被用作 `UserModel` 的实例时，仍然保持了接口的一致性，即它至少具有 `UserModel` 的所有属性和方法。

**适用场景**：

- 当函数或方法预期只与一个具体类及其子类交互时。
- 代码中没有需要泛型或多个类型保持一致性的需求。

**优点**：

- 简单直接，易于理解。
- 代码更加直观，易于维护和阅读。

### 使用 `TypeVar` 绑定到实体类型

在以上代码示例中，在入参情况下 `TypeVar` 与直接使用实体类型是一致的，但是在返回时， `TypeVar`  可以确保当你传入的是什么类型，就会标记返回什么类型，比如你传入的是 `UserModel` 的子类 `SonUserModel` ，则返回的也是  `SonUserModel`  的实例

**适用场景**：

- 在实现泛型编程时，尤其是当需要确保多个参数或返回值之间的类型一致性时。
- 当需要将类型参数限定于某个特定的基类或接口时，但又希望保持一定的类型灵活性。

**优点**：

- 提高了代码的灵活性和可重用性。
- 可以在多个函数或类之间保持类型一致性，提高代码的安全性。

