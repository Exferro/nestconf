# nestconf

A lightweight Python library for nested configuration management with zero dependencies. nestconf makes it easy to create configurable classes with type-safe configuration parameters.

## Motivation

When writing code for numerical experiments, you often need to manage multiple configuration parameters (knobs) across different modules, which can be nested within each other. This package was born from the need to:

1. Easily store experiment results based on the values of these configuration knobs
2. Generate human-readable descriptions of experiments alongside their results
3. Separate experiment-defining parameters from situationally dynamic parameters (like file paths)

For example, in a machine learning experiment, you might have:
- Model architecture parameters (number of layers, hidden sizes)
- Training parameters (learning rate, batch size)
- Dataset parameters (number of samples, preprocessing steps)
- Runtime parameters (output directory, GPU device)

With nestconf, you can easily make any class Configurable and abstract the relevant knobs there, while keeping other parameters separate. This makes it simple to:
- Generate unique paths for experiment results based on configuration values
- Save and load experiment configurations
- Compare different experimental setups
- Document the exact parameters used in each experiment

## Installation

```bash
pip install nestconf
```

## Features

- Automatic Config class generation for each Configurable class
- Support for nested configurations
- Flexible initialization with either kwargs or Config objects
- Conflict detection between config and kwargs
- Path suffix generation for configuration values
- JSON serialization support
- Hash-based configuration comparison

## Usage

### Basic Example

Let's say you have a class with some configurable parameters. To make it work with nestconf, you just need to:

1. Inherit from `Configurable`
2. Add type annotations to the fields you want to be part of the configuration

Here's a simple example:

```python
from nestconf import Configurable

class Person(Configurable):
    # These fields will be part of the configuration
    name: str = None
    age: int = None

    def __init__(self, *, config=None, people_root_path: str = None, **kwargs):
        super().__init__(config=config, **kwargs)
        # This field won't be part of the configuration
        self.people_root_path = people_root_path
```

Thanks to Python's metaclass magic, a corresponding `PersonConfig` class is automatically created with the same fields as the type-annotated fields in `Person`. This is similar to how dataclasses work, but with additional configuration management features. The Config class will always be named by appending "Config" to the original class name (e.g., `PersonConfig` for `Person`).

### Initialization Methods

You can initialize a Configurable class in two ways:

1. Using keyword arguments:
```python
person = Person(name="John", age=30, people_root_path="/data")
```

2. Using a Config object:
```python
config = PersonConfig(name="John", age=30)
person = Person(config=config, people_root_path="/data")
```

### Conflict Detection

nestconf prevents conflicts between config and kwargs:
```python
config = PersonConfig(name="John", age=30)
# This will raise a ValueError due to conflicting name values
person = Person(config=config, name="Jane", people_root_path="/data")
```

### Extracting Configuration

You can extract the current configuration from any Configurable instance using the `config` property:
```python
person = Person(name="John", age=30, people_root_path="/data")
config = person.config
print(config.name)  # "John"
print(config.age)   # 30
# Note: people_root_path is not in config as it's not an annotated field
```

### Path Suffix Generation

The Config class provides a `to_path_suffix()` method that generates a path-like string representation of the configuration:

```python
class TestPerson(Configurable):
    name: str = None
    age: int = None
    city: str = None
    country: str = None

# All values set
person1 = TestPerson(name="John", age=30, city="London", country="UK")
print(person1.config.to_path_suffix())
# Output: "name=John/age=30/city=London/country=UK"

# With None values
person2 = TestPerson(name="John", age=None, city="London", country="UK")
print(person2.config.to_path_suffix(stop_at_none=True))
# Output: "name=John"
print(person2.config.to_path_suffix())
# Output: "name=John/age=None/city=London/country=UK"
```

### JSON Serialization

Config objects can be serialized to JSON:
```python
person = Person(name="John", age=30)
config = person.config
json_str = config.to_json_dict()
config.to_json("person_config.json")
```

### Configuration Comparison

Config objects can be compared using hash-based equality:
```python
config1 = PersonConfig(name="John", age=30)
config2 = PersonConfig(name="John", age=30)
assert config1 == config2  # True
```

## Advanced Features

### Nested Configurations

nestconf supports nested configurations through Configurable objects:

```python
class Address(Configurable):
    street: str = None
    city: str = None

class Person(Configurable):
    name: str = None
    address: Address = None

person = Person(
    name="John",
    address=Address(street="123 Main St", city="London")
)
print(person.config.to_path_suffix())
# Output: "name=John/address=street=123 Main St/city=London"
```

## Requirements

- Python >= 3.7 (for dataclasses support)
- No external dependencies 
