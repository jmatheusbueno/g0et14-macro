# Contexto do Projeto: G0et1a Macro

## Objetivo

Aplicativo desktop simples para automatizar acoes repetitivas de teclado e mouse com interface grafica.

O usuario pode cadastrar varias macros, cada uma com:

- tipo de acao (`key` ou `mouse`)
- valor da acao (tecla ou botao do mouse)
- intervalo em segundos
- delay individual em segundos (padrao `0`)

Todas as macros sao executadas em paralelo logico dentro de uma unica thread de trabalho, com um delay inicial opcional.

Atualmente o projeto tambem possui persistencia em arquivos JSON e suporte a distribuicao como executavel Windows.

## Stack e Dependencias

- Python 3.10+
- Tkinter (GUI nativa)
- `pynput==1.7.7` (controle de teclado e mouse)

## Estrutura Atual

- `app.py`: ponto de entrada da aplicacao.
- `macro_app.py`: camada de interface (Tkinter) e orquestracao de fluxo.
- `macro_models.py`: modelos de dominio (`MacroItem`).
- `macro_constants.py`: mapeamentos de teclas e botoes de mouse.
- `macro_validator.py`: validacoes e normalizacao de entradas.
- `macro_storage.py`: persistencia de saves em JSON.
- `macro_runner.py`: execucao agendada das macros em thread.
- `README.md`: instrucoes de instalacao e uso.
- `requirements.txt`: dependencias Python.
- `saves/`: pasta de configuracoes salvas em JSON.
- `dist/`: saida do executavel (`g0et1a-macro.exe`) quando gerado via PyInstaller.

## Arquitetura (app.py)

`app.py` agora somente chama `main()` de `macro_app.py`.

## Arquitetura (modular)

### Modelo

- `MacroItem` (`dataclass`)
  - `item_id`: identificador da macro
  - `action_type`: `"key"` ou `"mouse"`
  - `value`: texto da tecla ou botao (`left/right/middle`)
  - `interval`: intervalo em segundos

### Controlador/UI

- `MacroApp` (em `macro_app.py`)
  - monta interface com `ttk`
  - gerencia estado de tela e lista de macros em memoria
  - delega validacoes para `MacroValidator`
  - delega persistencia para `SaveRepository`
  - delega agendamento/execucao para `MacroRunner`

### Execucao de macros

- `MacroRunner` (em `macro_runner.py`)
  - cria agenda (`schedule`) com `next_run` por macro
  - roda loop em thread daemon usando `time.monotonic()`
  - aplica delay global antes dos delays individuais
  - recalcula execucoes por `interval` ate parada

### Persistencia (saves)

- `SaveRepository` (em `macro_storage.py`) salva em JSON na pasta `saves/`:
  - `version`
  - `start_delay`
  - lista `macros` com `action_type`, `value`, `interval` e `start_delay`
- carrega arquivo selecionado, valida dados e reconstrui lista de macros
- lista arquivos `.json` para o combobox de carregamento
- Nome de save e sanitizado para aceitar apenas letras, numeros, `_` e `-`.

## Fluxo Funcional

1. Usuario seleciona tipo (tecla/mouse).
2. Informa valor e intervalo.
3. Adiciona/atualiza/remove itens na lista.
4. Informa delay inicial.
5. Informa delay individual em cada macro (opcional, padrao 0).
6. Opcionalmente salva a configuracao na secao de saves.
7. Opcionalmente carrega uma configuracao salva da pasta `saves/`.
8. Inicia execucao.
9. App aplica primeiro o delay global, depois o delay individual de cada macro, e entao segue com os intervalos.

## Regras de Validacao Importantes

- Intervalo deve ser numero e maior que zero.
- Delay inicial deve ser numero e nao negativo.
- Tecla deve ser:
  - 1 caractere (`a`, `r`, etc.) ou
  - chave especial mapeada (`space`, `enter`, `tab`, `esc`, setas, etc.)
- O campo de tecla converte entradas especiais:
  - pressionar TAB no campo define `tab`
  - pressionar ESPACO no campo define `space`
- Mouse aceita apenas `left`, `right` ou `middle`.
- Save precisa conter dados validos (`action_type`, `value`, `interval > 0`, `start_delay >= 0`).

## Comportamentos de Interface

- Campo de tecla e combobox de mouse alternam habilitacao conforme tipo selecionado.
- Durante execucao:
  - botoes de CRUD e campos de formulario ficam bloqueados
  - controles de save/load tambem ficam bloqueados
  - apenas `Parar` permanece habilitado
- Selecionar item da lista preenche formulario para edicao.
- Lista de saves pode ser atualizada pelo botao "Atualizar lista".

## Limitacoes Atuais

- Nao ha hotkey global para iniciar/parar.
- Nao ha logs de execucao, retries ou tratamento detalhado de falhas de automacao.
- Precisao depende de timer e agendamento do sistema operacional.

## Pontos de Evolucao Natural

- Adicionar hotkeys globais de start/stop/pause.
- Incluir coluna de "proxima execucao" e contador por macro.
- Permitir ordenar macros e duplicar item.
- Criar suporte a sequencias (mais de uma acao por macro).
- Exportar/importar saves por arquivo externo escolhido pelo usuario.
- Adicionar confirmacao para sobrescrita de save com mesmo nome.

## Comandos Rapidos

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Executar app:

```bash
python app.py
```

Gerar executavel Windows:

```bash
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --clean --onefile --windowed --name g0et1a-macro app.py
```

Saida do executavel:

```text
dist/g0et1a-macro.exe
```
