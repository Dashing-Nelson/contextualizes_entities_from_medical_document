import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, TypeVar, Union

from app.util.log import logger


class EnvVarType(Enum):
    """Enum for supported environment variable types."""

    STRING = "string"
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    ENUM = "enum"
    BYTES = "bytes"


# Common deployment stages
class Stage(Enum):
    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"


@dataclass
class EnvVarConfig:
    """Configuration for an environment variable."""

    name: str
    required: bool = True
    default: Any = None
    var_type: EnvVarType = EnvVarType.STRING
    description: str = ""
    # For enum validation
    enum_class: Optional[type] = None
    allowed_values: Set[Any] = field(default_factory=set)


T = TypeVar("T")


class EnvConfig:
    """Environment configuration manager."""

    def __init__(self, configs: List[EnvVarConfig]):
        """
        Initialize with a list of environment variable configurations.

        Args:
            configs: List of EnvVarConfig objects defining the environment variables.
        """
        self.configs = configs
        self.values: Dict[str, Any] = {}
        self._load_env_vars()

    def _load_env_vars(self) -> None:
        """Load all environment variables based on their configurations."""
        for config in self.configs:
            value = os.getenv(config.name)

            # Check if required variable is missing
            if value is None and config.required and config.default is None:
                raise ValueError(
                    f"Required environment variable '{config.name}' is not set."
                )

            # Use default if value is not present
            if value is None:
                value = config.default
                if config.required:
                    logger.info(
                        f"Using default value for required environment variable: {config.name}"
                    )

            # Skip processing if value is None (will remain None in self.values)
            if value is None:
                self.values[config.name] = None
                continue

            # Convert value to specified type
            try:
                if config.var_type == EnvVarType.INT:
                    self.values[config.name] = int(value)
                elif config.var_type == EnvVarType.FLOAT:
                    self.values[config.name] = float(value)
                elif config.var_type == EnvVarType.BOOL:
                    self.values[config.name] = value.lower() in (
                        "true",
                        "yes",
                        "1",
                        "y",
                    )
                elif config.var_type == EnvVarType.BYTES:
                    self.values[config.name] = value.encode("utf-8")
                elif config.var_type == EnvVarType.ENUM:
                    # Handle enum validation
                    if config.enum_class is not None:
                        try:
                            # Try to convert string to enum value
                            self.values[config.name] = config.enum_class(value)
                        except ValueError:
                            enum_values = [e.value for e in config.enum_class]
                            raise ValueError(
                                f"Invalid value '{value}' for '{config.name}'. "
                                f"Must be one of: {', '.join(str(v) for v in enum_values)}"
                            )
                    elif config.allowed_values:
                        # Check against allowed values set
                        if value not in config.allowed_values:
                            raise ValueError(
                                f"Invalid value '{value}' for '{config.name}'. "
                                f"Must be one of: {', '.join(str(v) for v in config.allowed_values)}"
                            )
                        self.values[config.name] = value
                    else:
                        # No validation rules provided, treat as string
                        self.values[config.name] = value
                else:  # Default is string
                    self.values[config.name] = value
            except (ValueError, TypeError) as e:
                raise ValueError(
                    f"Could not convert '{config.name}' value to {config.var_type.value}: {e}"
                )

    def get(self, name: str, default: Optional[T] = None) -> Union[Any, T]:
        """
        Get an environment variable value.

        Args:
            name: Name of the environment variable.
            default: Default value if the variable is not found.

        Returns:
            The value of the environment variable or the default.
        """
        return self.values.get(name, default)

    def __getitem__(self, name: str) -> Any:
        """Get an environment variable value using dictionary syntax."""
        if name not in self.values:
            raise KeyError(f"Environment variable '{name}' not found.")
        return self.values[name]

    def __contains__(self, name: str) -> bool:
        """Check if an environment variable exists."""
        return name in self.values


# Example usage
def configure_environment():
    """Configure and return the application environment."""
    env_configs = [
        EnvVarConfig(
            name="HTTP_BASIC_AUTH_USERNAME",
            var_type=EnvVarType.BYTES,
            description="Username for HTTP basic authentication",
        ),
        EnvVarConfig(
            name="HTTP_BASIC_AUTH_PASSWORD",
            var_type=EnvVarType.BYTES,
            description="Password for HTTP basic authentication",
        ),
        EnvVarConfig(
            name="STAGE",
            var_type=EnvVarType.ENUM,
            enum_class=Stage,
            description="Deployment stage (dev, staging, prod)",
        ),
        EnvVarConfig(
            name="HUGGING_FACE_MODEL_PATH", description="Path to Hugging Face model"
        ),
        EnvVarConfig(
            name="HUGGING_FACE_TASK",
            required=False,
            default="ner",
            var_type=EnvVarType.ENUM,
            allowed_values={
                "ner",
                "text-classification",
                "question-answering",
                "summarization",
            },
            description="Hugging Face task type",
        ),
        EnvVarConfig(
            name="HUGGING_FACE_AGGREGATION_STRATEGY",
            required=False,
            default="average",
            var_type=EnvVarType.ENUM,
            allowed_values={"simple", "first", "average", "max"},
            description="Aggregation strategy for Hugging Face models",
        ),
        EnvVarConfig(
            name="HUGGING_FACE_DEVICE",
            required=False,
            default="cpu",
            var_type=EnvVarType.ENUM,
            allowed_values={"cpu", "cuda", "mps"},
            description="Device to run Hugging Face models on",
        ),
        EnvVarConfig(
            name="HTTP_PORT",
            required=True,
            var_type=EnvVarType.INT,
            description="PORT to run on HTTP server",
        ),
    ]

    return EnvConfig(env_configs)


env = configure_environment()

# Access variables - stage will be an actual Stage enum instance
correct_username_bytes = env["HTTP_BASIC_AUTH_USERNAME"]
correct_password_bytes = env["HTTP_BASIC_AUTH_PASSWORD"]
stage = env["STAGE"]  # This will be a Stage enum value
huggingface_model = env["HUGGING_FACE_MODEL_PATH"]
huggingface_task = env.get("HUGGING_FACE_TASK")
huggingface_aggregation_strategy = env.get("HUGGING_FACE_AGGREGATION_STRATEGY")
huggingface_device = env.get("HUGGING_FACE_DEVICE")
http_port = env.get("HTTP_PORT")

# Model labels to show and exclude remaining.
KEEP_LABELS = {
    "Disease_disorder",
    "Sign_symptom",
    "Medication",
    "Diagnostic_procedure",
}

MIN_MODEL_ACCURACY = 0.6  # 60%
