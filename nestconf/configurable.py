import sys

from dataclasses import make_dataclass, field, Field, MISSING

from .config import Config


class ConfigurableMeta(type):
    def __new__(cls, name, bases, dct):
        # Create a copy of dct for the class creation
        class_dct = dct.copy()
        
        # If there are annotations, handle the fields
        if '__annotations__' in class_dct:
            for field_name, field_type in class_dct['__annotations__'].items():
                if isinstance(class_dct.get(field_name), Field):
                    # If it's a Field, evaluate its default_factory or default
                    field_obj = class_dct[field_name]
                    if field_obj.default_factory is not MISSING:
                        class_dct[field_name] = field_obj.default_factory()
                    elif field_obj.default is not MISSING:
                        class_dct[field_name] = field_obj.default
                    else:
                        class_dct[field_name] = None

        # Create the Configurable class
        configurable_cls = super().__new__(cls, name, bases, class_dct)

        config_fields = []
        if '__annotations__' in dct:
            for field_name, field_type in dct['__annotations__'].items():
                if isinstance(dct.get(field_name), Field):
                    config_fields.append((field_name, 
                                       field_type,
                                       dct[field_name]))
                elif field_name in dct:
                    config_fields.append((field_name,
                                       field_type,
                                       field(default=dct[field_name])))
                else:
                    config_fields.append((field_name,
                                       field_type,
                                       field(default=None)))
                    
            # Define the dynamically created Config class
            config_name = f"{name}Config"
            config_class = make_dataclass(
                config_name,
                fields=config_fields,
                bases=(Config,),
                frozen=True,
                eq=False,
            )

            # Set the module of the config class to be the same as the original class
            config_class.__module__ = configurable_cls.__module__

            # Attach the dynamically created Config class to the Configurable
            setattr(configurable_cls, "BOUND_CONFIG_CLASS", config_class)

            # Add the config class to the correct module's namespace
            module = sys.modules[configurable_cls.__module__]
            setattr(module, config_name, config_class)
            
        return configurable_cls
    

class Configurable(metaclass=ConfigurableMeta):
    def __init__(self, *, config: Config = None, **kwargs):
        if config is not None:
            if not isinstance(config, self.BOUND_CONFIG_CLASS):
                raise TypeError(f"Expected {self.BOUND_CONFIG_CLASS}, got {type(config)}.")
            
            # Check for value conflicts between config and kwargs
            for field_name in set(kwargs.keys()) & set(config.__dict__.keys()):
                if kwargs[field_name] != config.__dict__[field_name]:
                    if (not (kwargs[field_name] is None)) and (not (config.__dict__[field_name] is None)):
                        raise ValueError(
                        f"Conflicting values provided for {field_name}. "
                        f"Config and direct arguments have different values for these attributes. "
                        f"Config value: {config.__dict__[field_name]}. "
                        f"Direct argument value: {kwargs[field_name]}.")                
            
            # Set values from config
            for field_name, value in config.__dict__.items():
                setattr(self, field_name, value)

        # Set values from kwargs
        for field_name, value in kwargs.items():
            if field_name in self.__annotations__:
                setattr(self, field_name, value)
            else:
                raise AttributeError(f"'{self.__class__.__name__}' has no annotated field '{field_name}'")

        # Set remaining annotated fields to None if not set
        for field_name in self.__annotations__:
            if not hasattr(self, field_name):
                setattr(self, field_name, None)

    @property
    def config(self) -> Config:
        """Dynamically create a config object based on current attribute values."""
        config_values = {
            field_name: getattr(self, field_name)
            for field_name in self.__annotations__
        }
        return self.BOUND_CONFIG_CLASS(**config_values)
