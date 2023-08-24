import json


class Settings:
    """Global settings to be imported by all modules in the architecture simulator."""

    _settings = {
        # change steps_per_interval if you want to change the amount of times evaluatePython_step_sim() is called per interval (10ms)
        # the higher this number the less responsive the ui gets, at 200 it starts to get a bit too unresponsive. 100 feels acceptable
        "steps_per_interval": 100,
        "autoparse_delay": 500,
        "default_no_error_output": "Ready!\n",
        "default_isa": "riscv",
        "default_register_representation": 3,
        "default_memory_representation": 3,
        "default_pipeline_mode": "single_stage_pipeline",
        "hazard_detection": True,
        "instruction_memory_min_bytes": 0,
        "instruction_memory_max_bytes": 2**14,
        "memory_address_length": 32,
        "memory_address_min_bytes": 2**14,
        "abi_names": {
            "zero": 0,
            "ra": 1,
            "sp": 2,
            "gp": 3,
            "tp": 4,
            "t0": 5,
            "t1": 6,
            "t2": 7,
            "s0": 8,
            "fp": 8,  # this is intentional, s0 and fp are the same register
            "s1": 9,
            "a0": 10,
            "a1": 11,
            "a2": 12,
            "a3": 13,
            "a4": 14,
            "a5": 15,
            "a6": 16,
            "a7": 17,
            "s2": 18,
            "s3": 19,
            "s4": 20,
            "s5": 21,
            "s6": 22,
            "s7": 23,
            "s8": 24,
            "s9": 25,
            "s10": 26,
            "s11": 27,
            "t3": 28,
            "t4": 29,
            "t5": 30,
            "t6": 31,
        },
        "toy_instruction_memory_min_bytes": 0,
        "toy_instruction_memory_max_bytes": 1024,
        "toy_memory_min_bytes": 1024,
        "toy_memory_max_bytes": 4096,
    }

    def get_JSON(self) -> str:
        """Returns a JSON string of the settings."""
        return json.dumps(self._settings)

    def get(self) -> dict:
        """Returns the settings as a dict."""
        return self._settings
