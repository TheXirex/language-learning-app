from dataclasses import dataclass, field
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
ARTIFACTS_DIR = ROOT_DIR / "artifacts"


@dataclass(frozen=True)
class ModuleTestConfig:
    name: str
    module_path: Path
    test_inputs: tuple[str, ...] = field(default_factory=tuple)

    @property
    def artifacts_dir(self) -> Path:
        return ARTIFACTS_DIR / self.name


SCRAPPER = ModuleTestConfig(
    name="scrapper",
    module_path=ROOT_DIR / "src" / "modules" / "scrapper",
    test_inputs=("hard",),
)

DB = ModuleTestConfig(
    name="db",
    module_path=ROOT_DIR / "src" / "modules" / "db",
)

