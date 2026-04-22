import json
from pathlib import Path

from macro_constants import MOUSE_BUTTONS
from macro_models import MacroItem
from macro_validator import MacroValidator


class SaveRepository:
    def __init__(self, base_dir: Path, validator: MacroValidator) -> None:
        self.validator = validator
        self.saves_dir = base_dir / "saves"
        self.saves_dir.mkdir(exist_ok=True)

    def list_save_names(self) -> list[str]:
        return sorted(path.stem for path in self.saves_dir.glob("*.json"))

    def save(self, save_name: str, start_delay: float, macros: list[MacroItem]) -> Path:
        payload = {
            "version": 1,
            "start_delay": start_delay,
            "macros": [
                {
                    "action_type": item.action_type,
                    "value": item.value,
                    "interval": item.interval,
                    "start_delay": item.start_delay,
                }
                for item in macros
            ],
        }

        save_path = self._save_file_path(save_name)
        with save_path.open("w", encoding="utf-8") as save_file:
            json.dump(payload, save_file, ensure_ascii=True, indent=2)

        return save_path

    def load(self, save_name: str) -> tuple[float, list[MacroItem]]:
        save_path = self._save_file_path(save_name)
        if not save_path.exists():
            raise ValueError("Arquivo de save nao encontrado.")

        try:
            with save_path.open("r", encoding="utf-8") as save_file:
                payload = json.load(save_file)
        except (OSError, json.JSONDecodeError) as err:
            raise ValueError(f"Falha ao ler save: {err}") from err

        try:
            loaded_macros: list[MacroItem] = []
            for index, raw_item in enumerate(payload.get("macros", []), start=1):
                action_type = str(raw_item.get("action_type", "")).strip().lower()
                value = str(raw_item.get("value", ""))
                interval = self.validator.parse_positive_number(
                    raw_item.get("interval", 0),
                    "Intervalo invalido no save.",
                )
                item_start_delay = self.validator.parse_non_negative_number(
                    raw_item.get("start_delay", 0),
                    "Delay do input invalido no save.",
                )

                if action_type not in {"key", "mouse"}:
                    raise ValueError("Tipo de acao invalido no save.")

                if action_type == "key":
                    value = self.validator.normalize_key_input(value)
                    self.validator.parse_key(value)
                elif value not in MOUSE_BUTTONS:
                    raise ValueError("Botao de mouse invalido no save.")

                loaded_macros.append(
                    MacroItem(
                        item_id=index,
                        action_type=action_type,
                        value=value,
                        interval=interval,
                        start_delay=item_start_delay,
                    )
                )

            start_delay = self.validator.parse_non_negative_number(
                payload.get("start_delay", 0),
                "Delay inicial invalido no save.",
            )
        except (TypeError, ValueError) as err:
            raise ValueError(f"Save invalido: {err}") from err

        return start_delay, loaded_macros

    def _save_file_path(self, save_name: str) -> Path:
        return self.saves_dir / f"{save_name}.json"
