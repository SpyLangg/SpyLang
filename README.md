# SpyLang Programming Language Documentation

## Overview
SpyLang is a programming language designed with a thrilling blend of espionage and geopolitics. It is tailored for developers who seek a unique thematic experience while coding. This documentation provides an in-depth understanding of SpyLang, its syntax, features, and usage. SpyLang programs can be converted into executable files, making them versatile and deployable.

![SpyLang Logo](asset/logo.png)

---

## Table of Contents

1. [Introduction](#introduction)
2. [Features](#features)
3. [Installation](#installation)
4. [Syntax and Structure](#syntax-and-structure)
    - [Errors](#errors)
    - [Tokens](#tokens)
    - [Control Structures](#control-structures)
5. [Running a SpyLang Program](#running-a-spylang-program)
6. [Examples](#examples)
7. [Built-in Functions](#built-in-functions)
8. [Glossary of Keywords](#glossary-of-keywords)
9. [Contributing](#contributing)

---

## Introduction
SpyLang is built to simulate the high-stakes world of international espionage while providing a robust and expressive programming environment. With a syntax inspired by clandestine operations and mission planning, it encourages developers to think like spies and strategists. 

---

## Features

- **Unique Thematic Syntax**: Keywords and operations are designed to resemble espionage terminology.
- **Dynamic Error Handling**: Errors are presented as mission failures with detailed reports.
- **Readable Token System**: Tokens such as `Agent Status` and `Mission Log` enhance code clarity.
- **Control Structures**: Includes espionage-themed constructs like `check` (if), `followup` (else if), and `otherwise` (else).
- **Loop Mechanics**: Use `each` for loops and `chase` for while loops.
- **Functional Programming**: Define functions as `missions` with parameters and return values.

---

## Installation

To get started with SpyLang, follow these steps:

1. **Download the Compiler**:
    Download the SpyLang compiler from the [github](#).

2. **Set Environment Variables**:
    Add the SpyLang directory to your system's PATH for easy access.

---

## Syntax and Structure

### Errors
SpyLang provides a unique error reporting mechanism:

- **Illegal Character**:
  > *Agent Error: Unauthorized character detected in the operation. Mission compromised!*

- **Expected Character**:
  > *Agent Error: Expected character not found in the operation. Mission compromised!*

- **Runtime Error**:
  > *Agent Error: Runtime breach! Unauthorized behavior detected in the system.*

### Tokens
SpyLang's token system includes:

- **Data Types**: `INT`, `FLOAT`, `STRING`
- **Operators**: `PLUS (+)`, `MINUS (-)`, `DIV (/)`, `MUL (*)`
- **Control Structures**: `KEYWORD`
- **Special Tokens**: `MISSION`, `AGENT REPORT`

### Control Structures

#### Conditional Statements

```spylang
check (condition) {
    # Actions if condition is true
}
followup (condition) {
    # Actions if followup condition is true
}
otherwise {
    # Actions if no conditions are true
}
```

#### Loops

**For Loop:**
```spylang
each var in (1..10) {
    # Loop body
}
```

**While Loop:**
```spylang
chase (condition) {
    # Loop body
}
```

---

## Running a SpyLang Program

1. Write your SpyLang code in a `.spy` file.

2. Use the SpyLang interpreter to execute the script:

    ```bash
    spylang.exe your_file.spy
    ```

---

## Examples

**Hello, Spy World:**
```spylang
mission main() {
    assign message = "Hello, Spy World!"
    extract message
}
```

**Fibonacci Sequence:**
```spylang
mission fibonacci(n) {
    check (n <= 1) {
        extract n;
    } otherwise {
        extract fibonacci(n - 1) + fibonacci(n - 2)
    }
}
```

**Prime Checker:**
```spylang
mission is_prime(number) {
    each i in (2..number - 1) {
        check (number % i == 0) {
            extract false;
        }
    }
    extract true
}
```

---

## Built-in Functions

SpyLang comes equipped with several built-in functions to assist in various operations:

- **`math_pi`**:
  A constant representing the value of π.

  ```spylang
  print(math_pi)
  ```

- **`transmit(value)`**:
  Prints the provided value to the console.

  ```spylang
  transmit("Agent reporting for duty!")
  ```

- **`transmit_ret(value)`**:
  Prints the value and returns it.

  ```spylang
  assign response = transmit_ret("Mission complete.")
  ```

- **`intel(prompt)`**:
  Reads input from the user as a string.

  ```spylang
  assign name = intel("Enter your codename: ")
  transmit("Welcome, " + name)
  ```

- **`intel_int(prompt)`**:
  Reads input from the user and converts it to an integer.

  ```spylang
  assign age = intel_int("Enter your age: ")
  transmit("Your age is " + age)
  ```

- **`erase()`**:
  Clears the console screen.

  ```spylang
  erase()
  ```

- **`is_code(value)`**:
  Checks if the value is a number.

  ```spylang
  transmit(is_code(42))
  ```

- **`is_msg(value)`**:
  Checks if the value is a string.

  ```spylang
  transmit(is_msg("Agent"))
  ```

- **`is_list(value)`**:
  Checks if the value is a list.

  ```spylang
  transmit(is_list([1, 2, 3]))
  ```

- **`is_mission(value)`**:
  Checks if the value is a function.

  ```spylang
  transmit(is_mission(main))
  ```

- **`add_agent(list, value)`**:
  Appends a value to a list.

  ```spylang
  assign agents = []
  add_agent(agents, "Agent 007")
  ```

- **`withdraw(list)`**:
  Removes the last element from a list and returns it.

  ```spylang
  assign last_agent = withdraw(agents)
  ```

- **`expand(list1, list2)`**:
  Extends the first list with elements from the second list.

  ```spylang
  expand(agents, ["Agent 008", "Agent 009"])
  ```

- **`length(collection)`**:
  Returns the length of a collection.

  ```spylang
  transmit(length(agents))
  ```

- **`launch(mission)`**:
  Executes a file.

  ```spylang
  launch("test.spy")
  ```

---

## Glossary of Keywords

- `assign`: Variable assignment.
- `check`: Start of a conditional block.
- `followup`: An else-if condition.
- `otherwise`: Default else block.
- `each`: Looping construct.
- `chase`: While loop construct.
- `mission`: Function definition.
- `extract`: Return statement.
- `abort`: Break statement.
- `proceed`: Continue statement.

---

## Contributing
Contributions to SpyLang are welcome. To contribute:

1. Fork the repository.
2. Create a new branch for your feature or fix.
3. Submit a pull request with detailed explanations of your changes.

---

**Enjoy coding with SpyLang! Let your imagination run wild in the thrilling world of espionage and geopolitics!**
