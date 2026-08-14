"""Shared adapter failures for direct robot I/O.

Responsible for: stable user-facing exception types.
Not responsible for: recovery, logging, or hardware calls.
"""


class RobotUnavailable(RuntimeError):
    """Report a missing connection, dependency, or failed robot operation."""
