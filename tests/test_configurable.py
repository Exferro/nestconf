import pytest
from nestconf import Configurable

class Person(Configurable):
    name: str = None
    age: int = None

    def __init__(self, *, config=None, people_root_path: str = None, **kwargs):
        super().__init__(config=config, **kwargs)
        self.people_root_path = people_root_path


def test_config_class_creation():
    """Test that PersonConfig class is automatically created."""
    assert hasattr(Person, 'BOUND_CONFIG_CLASS')
    assert Person.BOUND_CONFIG_CLASS.__name__ == 'PersonConfig'


def test_create_without_config():
    """Test creating Person instance without config."""
    person = Person(name="John", age=30, people_root_path="/data")
    assert person.name == "John"
    assert person.age == 30
    assert person.people_root_path == "/data"


def test_create_with_config():
    """Test creating Person instance with config only."""
    config = Person.BOUND_CONFIG_CLASS(name="John", age=30)
    person = Person(config=config, people_root_path="/data")
    assert person.name == "John"
    assert person.age == 30
    assert person.people_root_path == "/data"


def test_config_kwargs_conflict():
    """Test that conflicting values between config and kwargs raise error."""
    config = Person.BOUND_CONFIG_CLASS(name="John", age=30)
    with pytest.raises(ValueError) as exc_info:
        Person(config=config, name="Jane", people_root_path="/data")
    assert "Conflicting values" in str(exc_info.value)


def test_config_kwargs_no_conflict():
    """Test that non-conflicting values between config and kwargs work."""
    config = Person.BOUND_CONFIG_CLASS(name="John")
    person = Person(config=config, age=30, people_root_path="/data")
    assert person.name == "John"
    assert person.age == 30
    assert person.people_root_path == "/data"


def test_config_property():
    """Test that config property returns correct configuration."""
    person = Person(name="John", age=30, people_root_path="/data")
    config = person.config
    assert config.name == "John"
    assert config.age == 30
    assert not hasattr(config, 'people_root_path')  # Non-annotated field should not be in config 


def test_path_suffix_stop_at_none():
    """Test that to_path_suffix stops at None when stop_at_none is True."""
    class TestPerson(Configurable):
        name: str = None
        age: int = None
        city: str = None
        country: str = None

    # Case 1: All values set
    person1 = TestPerson(name="John", age=30, city="London", country="UK")
    assert person1.config.to_path_suffix() == "name=John/age=30/city=London/country=UK"

    # Case 2: With None in the middle and stop_at_none=True
    person2 = TestPerson(name="John", age=None, city="London", country="UK")
    assert person2.config.to_path_suffix(stop_at_none=True) == "name=John"

    # Case 3: With None in the middle and stop_at_none=False (default behavior)
    assert person2.config.to_path_suffix() == "name=John/age=None/city=London/country=UK" 