from macro_constants import MOUSE_BUTTONS, SPECIAL_KEYS


class MacroValidator:
    def normalize_key_input(self, key_text: str) -> str:
        if key_text == "\t":
            return "tab"
        if key_text == " ":
            return "space"

        normalized = key_text.strip().lower()
        if normalized == "\\t":
            return "tab"

        return normalized

    def parse_key(self, key_text: str):
        normalized = self.normalize_key_input(key_text)
        if not normalized:
            raise ValueError("Informe uma tecla.")

        if normalized in SPECIAL_KEYS:
            return SPECIAL_KEYS[normalized]

        if len(normalized) == 1:
            return normalized

        raise ValueError("Tecla invalida. Use um caractere ou tecla especial.")

    def parse_positive_number(self, raw_value, error_message: str) -> float:
        try:
            value = float(raw_value)
        except (TypeError, ValueError) as exc:
            raise ValueError(error_message) from exc

        if value <= 0:
            raise ValueError(error_message)

        return value

    def parse_non_negative_number(self, raw_value, error_message: str) -> float:
        try:
            value = float(raw_value)
        except (TypeError, ValueError) as exc:
            raise ValueError(error_message) from exc

        if value < 0:
            raise ValueError(error_message)

        return value

    def sanitize_save_name(self, raw_name: str) -> str:
        cleaned = "".join(ch for ch in raw_name.strip() if ch.isalnum() or ch in ("-", "_"))
        if not cleaned:
            raise ValueError("Informe um nome de save valido (letras, numeros, _ ou -).")
        return cleaned

    def validate_mouse_button(self, button_name: str) -> str:
        normalized = button_name.strip().lower()
        if normalized not in MOUSE_BUTTONS:
            raise ValueError("Botao de mouse invalido.")
        return normalized
