# Mini Macro

Projeto simples de macro com interface grafica para criar varias macros, cada uma com seu proprio intervalo.

Cada macro pode ser:

- digitar uma tecla automaticamente a cada X segundos;
- clicar o mouse automaticamente a cada X segundos.

## Requisitos

- Python 3.10+
- Windows/macOS/Linux

## Instalacao

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
```

## Executar

```bash
python app.py
```

## Como usar

1. Escolha o tipo de acao: **Tecla** ou **Clique do mouse**.
2. Preencha o input da acao:
	- Tecla: `a`, `s`, `r`, `space`, `enter`, `tab`, etc.
	- Mouse: `left`, `right` ou `middle`.
3. Informe o intervalo em segundos (por exemplo, `30`).
4. Clique em **Adicionar** para incluir a macro na lista.
5. Repita para adicionar quantas macros quiser.
6. Use **Atualizar** para editar uma macro selecionada na lista.
7. Use **Remover** para excluir uma macro selecionada.
8. Informe o campo **Delay inicial (s)** (ex.: `10`) para esperar esse tempo antes da primeira execucao.
9. Clique em **Iniciar** para executar todas as macros da lista e em **Parar** para interromper.

### Atalhos no campo Tecla

- Pressionar **TAB** no campo Tecla grava automaticamente `tab` como valor da macro.
- Pressionar **ESPACO** no campo Tecla grava automaticamente `space` como valor da macro.

## Saves (salvar e carregar configuracoes)

- O projeto possui a pasta `saves/` para armazenar configuracoes em arquivos `.json`.
- Para salvar:
	1. Preencha as macros que deseja manter.
	2. Informe um nome no campo **Nome** da secao **Saves**.
	3. Clique em **Salvar**.
- Para carregar:
	1. Selecione um item na lista **Carregar**.
	2. Clique em **Carregar**.

Ao carregar um save, a lista atual de macros e o delay inicial sao substituidos pelos dados do arquivo selecionado.

### Formato do save

Cada arquivo em `saves/` usa JSON no formato:

```json
{
	"version": 1,
	"start_delay": 0,
	"macros": [
		{
			"action_type": "key",
			"value": "space",
			"interval": 30
		},
		{
			"action_type": "mouse",
			"value": "left",
			"interval": 40
		}
	]
}
```

## Executavel (Windows)

Para gerar um `.exe` com PyInstaller:

```bash
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --clean --onefile --windowed --name mini-macro app.py
```

Saida esperada:

- `dist/mini-macro.exe`

Ao rodar o executavel, a pasta `saves/` e criada/usada ao lado do `.exe`.

## Exemplo

Para ter esse conjunto:

- `R` a cada `30` segundos
- `Click esquerdo` a cada `40` segundos
- `S` a cada `5` segundos
- `A` a cada `15` segundos

adicione 4 macros com esses valores e depois clique em **Iniciar**.

## Observacoes

- Em alguns sistemas, o app pode precisar de permissao de acessibilidade para controlar teclado/mouse.
- Use com cuidado para nao interferir em outras atividades no computador.
