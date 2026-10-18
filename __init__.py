import types
import sys
from pathlib import Path
_cur_dir = Path(__file__).resolve().parent
if str(_cur_dir) not in sys.path:
    sys.path.insert(0, str(_cur_dir))
if "flyfly_oncology" not in sys.modules:
    _pkg = types.ModuleType("flyfly_oncology")
    _pkg.__path__ = [str(_cur_dir)]
    _pkg.__file__ = str(_cur_dir / "__init__.py")
    sys.modules["flyfly_oncology"] = _pkg
