from dataclasses import make_dataclass, field, Field

from .config import Config


class ConfigurableMeta(type):
    def __new__(cls, name, bases, dct):
        # Create the Configurable class
        configurable_cls = super().__new__(cls, name, bases, dct)

        config_fields = []
        if '__annotations__' in dct:
            for field_name, field_type in dct['__annotations__'].items():
                if isinstance(dct[field_name], Field):
                    config_fields.append((field_name, 
                                        field_type,
                                        dct[field_name]))
                else:
                    config_fields.append((field_name,
                                        field_type,
                                        field(default=dct[field_name])))
                    
            # # Define the dynamically created Config class
            config_name = f"{name}Config"
            config_class = make_dataclass(
                config_name,  # Name of the dynamically created class
                fields=config_fields,  # Dynamically extracted fields
                bases=(Config,),  # Inherit from the base Config class
            )

            # Attach the dynamically created Config class to the Configurable
            setattr(configurable_cls, "BOUND_CONFIG_CLASS", config_class)

            for field_name, _, _ in config_fields:
                def make_property(field_name):
                    # Define a property dynamically
                    return property(lambda self: getattr(self.config, field_name))
                setattr(configurable_cls, field_name, make_property(field_name))

        return configurable_cls
    

class Configurable(metaclass=ConfigurableMeta):
    def __init__(self, 
                 *,
                 config: Config = None,
                 **kwargs):
        # Use the dynamically created Config class
        if config is None:
            self.config = self.BOUND_CONFIG_CLASS()
        else:
            if not isinstance(config, self.BOUND_CONFIG_CLASS):
                raise TypeError(f"Expected {self.BOUND_CONFIG_CLASS}, got {type(config)}.")
            else:
                self.config = config
        for arg_name, arg_val in kwargs.items():
            if hasattr(self.config, arg_name):
                setattr(self.config, arg_name, arg_val)
