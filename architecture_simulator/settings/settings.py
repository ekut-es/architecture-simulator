import json


class Settings:
    """Global settings to be imported by all modules in the architecture simulator."""

    _settings = {
        # change steps_per_interval if you want to change the amount of times evaluatePython_step_sim() is called per interval (10ms)
        # the higher this number the less responsive the ui gets, at 200 it starts to get a bit too unresponsive. 100 feels acceptable
        "steps_per_interval": 100,
        "autoparse_delay": 500,
        "default_isa": "riscv",
        "default_register_representation": 3,
        "default_memory_representation": 3,
        "default_pipeline_mode": "single_stage_pipeline",
        "hazard_detection": True,
        "BINARY_REPRESENTATION": 0,
        "DECIMAL_REPRESENTATION": 1,
        "HEXADECIMAL_REPRESENTATION": 2,
        "SIGNED_DECIMAL_REPRESENTATION": 3,
    }

    def get_JSON(self) -> str:
        """Returns a JSON string of the settings."""
        return json.dumps(self._settings)

    def get(self) -> dict:
        """Returns the settings as a dict."""
        return self._settings
