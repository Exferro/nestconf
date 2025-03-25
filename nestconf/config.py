import os
import json
import hashlib

from abc import ABC


class Config(ABC):
    """
    Base configuration class with utility methods.
    """
    def to_dict(self):
        """
        Convert the configuration to a dictionary.
        """
        return {
            attr_name: self._convert_value_to_dict(getattr(self, attr_name))
            for attr_name in self.__dict__.keys()
        }
    
    def _convert_value_to_dict(self, value):
        """Helper method to convert values to dictionary representation."""
        # Handle Configurable objects
        if hasattr(value, 'config'):
            return value.config.to_dict()
        # Handle Config objects
        elif hasattr(value, 'to_dict'):
            return value.to_dict()
        # Handle regular values
        return value

    @classmethod
    def custom_json_encoder(cls, obj):
        """
        Custom JSON encoder for the configuration.
        """
        try:
            return json.dumps(obj)
        except (TypeError, ValueError):
            return repr(obj)

    def to_json_dict(self):
        """
        Serialize the configuration to JSON.
        """
        return json.dumps(self.to_dict(),
                         default=Config.custom_json_encoder, 
                         indent=4)

    def to_json(self, filename: str = None):
        with open(filename, 'w') as f:
            json.dump(self.to_dict(),
                     f,
                     indent=4)
    
    def to_path_suffix(self, stop_at_none: bool = False):
        path_suffix = []
        for attr_name in self.__dict__.keys():
            attr_val = getattr(self, attr_name)
            if stop_at_none and attr_val is None:
                break
            else:
                if hasattr(attr_val, 'config'):  # Handle Configurable
                    path_suffix.append(attr_val.config.to_path_suffix())
                elif isinstance(attr_val, Config):  # Handle Config
                    path_suffix.append(attr_val.to_path_suffix())
                else:
                    path_suffix.append(f'{attr_name}={attr_val}')

        return os.path.join(*path_suffix) if len(path_suffix) > 0 else ''

    def __hash__(self):
        return hash(self.to_json_dict())
    
    def to_sha256_str(self):
        hash_factory = hashlib.sha256()
        hash_factory.update(bytes(self.__str__(), 'ascii'))
        return hash_factory.hexdigest()
    
    def __str__(self):
        return self.to_json_dict()
    
    def __eq__(self, other):
        return self.to_sha256_str() == other.to_sha256_str()
