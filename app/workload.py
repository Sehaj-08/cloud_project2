"""Bounded deterministic CPU workload used for scaling experiments."""


def run_cpu_workload(iterations: int) -> int:
    """Perform deterministic integer work and return a stable result.

    This deliberately consumes CPU. The API layer enforces a configurable
    upper bound so callers cannot request unbounded work.
    """
    accumulator = 0
    modulus = 1_000_000_007
    for value in range(1, iterations + 1):
        mixed_value = (value * 2_654_435_761) ^ (value >> 3)
        accumulator = (accumulator + mixed_value) % modulus
    return accumulator
