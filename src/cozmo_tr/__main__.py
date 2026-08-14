"""Allow `python -m cozmo_tr` to invoke the CLI.

Responsible for: process entry only.
Not responsible for: argument parsing or application behavior.
"""

from cozmo_tr.cli import main

raise SystemExit(main())
