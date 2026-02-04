"""Safe default execution policy profile.

Conservative defaults that fail closed. Used when:
- No config exists
- Requested profile not found
- Config parsing errors occur
"""

from profiles.builtins import SAFE

__all__ = ["SAFE"]
