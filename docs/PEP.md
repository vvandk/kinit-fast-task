# PEP

PEP 是 Python Enhancement Proposal（Python 增强提案）的缩写。它是一种为 Python 社区提供新功能或改进现有功能建议的正式文档。PEP 的目的是为 Python 的开发和进化提供信息给广大的 Python 社区，或定义一个新的特性以及它的过程或环境。每个 PEP 都包含了一个提案的技术规格和理由，以及讨论该提案所必须的背景信息。

PEP 分为三种类型：

1. **标准跟踪 PEP**：描述了对 Python 语言的新功能或实现的更改，需要广泛的社区共识。
2. **信息性 PEP**：提供一般的指导或信息给 Python 社区，但不包含新功能。
3. **流程 PEP**：描述了 Python 社区的流程或改进，包括决策过程以及环境或程序的变更。

每个 PEP 都有一个唯一的编号，通常以 "PEP" 后跟一个编号来表示（例如，PEP 8）。PEP 通过 Python 社区的讨论和反馈逐步完善，最终可能会被接受并实现在 Python 语言中，或者被拒绝或撤回。

PEP 的流程通常包括草案的撰写、提交、讨论、可能的修改、以及最终的接受或拒绝。这个流程确保了 Python 社区的每个成员都有机会对 Python 的发展提供意见和反馈。



## PEP 585

Type Hinting Generics In Standard Collections

**PEP 585** 提出了一种改进，允许在标准集合和其他部分的 Python 类型提示中直接使用泛型类型，而不需要从 `typing` 模块导入特殊的类。这个改动使得类型提示更加自然和简洁。

**主要特点**

- **内置集合作为泛型**：在 Python 3.9 之前，要对内置集合（如 `list`、`dict`、`set` 等）使用泛型，需要从 `typing` 模块导入对应的泛型版本，例如 `List[T]`、`Dict[K, V]`。PEP 585 允许直接在这些内置集合上使用泛型注解，比如 `list[int]`、`dict[str, float]`。
- **减少 `from typing import ...` 的需要**：这个改动减少了在使用类型提示时需要从 `typing` 模块导入的类型数量。
- **类型提示和运行时行为的统一**：通过这种方式，类型提示更接近 Python 代码的实际运行时行为。

**示例**

在 Python 3.9 以及更早的版本中，你可能需要这样写代码：

```
pythonCopy codefrom typing import List, Dict

def process(items: List[int]) -> Dict[str, int]:
    ...
```

在 Python 3.10 及以后的版本中，你可以这样写：

```
pythonCopy codedef process(items: list[int]) -> dict[str, int]:
    ...
```

## PEP 604

Allow writing union types as X | Y

**PEP 604** 引入了一个新的语法，允许用 `X | Y` 来表示联合类型，这是对先前需要使用 `typing.Union[X, Y]` 的简化。

**主要特点**

- **简化联合类型的表示**：使用 `|` 操作符可以更简单直观地表示一个值可以是多个类型之一。
- **减少 `from typing import Union` 的需要**：与 PEP 585 类似，这个改动也减少了对 `typing` 模块的依赖。
- **与类型提示的其他部分保持一致性**：这种表示方法与其他类型提示特性（如泛型）更为一致。

**示例**

在 Python 3.9 以及更早的版本中，表示一个变量可以是 `int` 或 `str` 类型，你需要这样写：

```
pythonCopy codefrom typing import Union

def foo(bar: Union[int, str]):
    ...
```

在 Python 3.10 及以后的版本中，你可以简单地写成：

```
pythonCopy codedef foo(bar: int | str):
    ...
```

这两个 PEP 的实施极大地简化了 Python 的类型提示系统，使其更加易于使用和理解。