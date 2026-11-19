"""Install lightweight Home Assistant stubs when the package is not present.

The integration package __init__.py pulls in coordinators and platforms, so
tests load config_flow via the package path without executing that file.
"""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _pkg(name: str, path: str | None = None) -> types.ModuleType:
    mod = types.ModuleType(name)
    if path is not None:
        mod.__path__ = [path]  # type: ignore[attr-defined]
    else:
        mod.__path__ = []  # type: ignore[attr-defined]
    sys.modules[name] = mod
    return mod


def _ensure_ha_stubs() -> None:
    try:
        import homeassistant  # noqa: F401
        return
    except ImportError:
        pass

    _pkg("homeassistant")
    config_entries = _pkg("homeassistant.config_entries")
    core = _pkg("homeassistant.core")
    exceptions = _pkg("homeassistant.exceptions")
    _pkg("homeassistant.helpers")
    aiohttp_client = _pkg("homeassistant.helpers.aiohttp_client")

    class HomeAssistantError(Exception):
        """Stub of homeassistant.exceptions.HomeAssistantError."""

    class HomeAssistant:
        """Minimal hass stand-in used by unit tests."""

    class ConfigFlowResult(dict):
        """Minimal mapping returned by stubbed flow methods."""

    class ConfigFlow:
        def __init_subclass__(cls, domain: str | None = None, **kwargs: Any) -> None:
            super().__init_subclass__(**kwargs)
            cls.domain = domain

        def __init__(self) -> None:
            self.hass = HomeAssistant()
            self.unique_id: str | None = None
            self._abort_unique = False

        async def async_set_unique_id(self, unique_id: str) -> None:
            self.unique_id = unique_id

        def _abort_if_unique_id_configured(self) -> None:
            if self._abort_unique:
                raise RuntimeError("already_configured")

        def async_create_entry(self, title: str, data: dict[str, Any]) -> ConfigFlowResult:
            return ConfigFlowResult({"type": "create_entry", "title": title, "data": data})

        def async_show_form(
            self, step_id: str, data_schema: Any = None, errors: dict[str, str] | None = None
        ) -> ConfigFlowResult:
            return ConfigFlowResult(
                {
                    "type": "form",
                    "step_id": step_id,
                    "data_schema": data_schema,
                    "errors": errors or {},
                }
            )

    config_entries.ConfigFlow = ConfigFlow
    config_entries.ConfigFlowResult = ConfigFlowResult
    core.HomeAssistant = HomeAssistant
    exceptions.HomeAssistantError = HomeAssistantError

    def async_get_clientsession(hass: Any) -> Any:
        return getattr(hass, "session")

    aiohttp_client.async_get_clientsession = async_get_clientsession


def _load_config_flow_module() -> None:
    """Register custom_components.isg without running integration __init__.py."""
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    if "custom_components" not in sys.modules:
        _pkg("custom_components", str(ROOT / "custom_components"))
    if "custom_components.isg" not in sys.modules:
        _pkg("custom_components.isg", str(ROOT / "custom_components" / "isg"))

    def _load(modname: str, rel: str) -> None:
        if modname in sys.modules and getattr(sys.modules[modname], "__file__", None):
            return
        path = ROOT / rel
        spec = importlib.util.spec_from_file_location(modname, path)
        if spec is None or spec.loader is None:
            raise ImportError(f"cannot load {modname} from {path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[modname] = module
        spec.loader.exec_module(module)

    _load("custom_components.isg.const", "custom_components/isg/const.py")
    _load("custom_components.isg.config_flow", "custom_components/isg/config_flow.py")


_ensure_ha_stubs()
_load_config_flow_module()
