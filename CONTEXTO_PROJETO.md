# Contexto do Projeto: Mini Macro

## Objetivo

Aplicativo desktop simples para automatizar acoes repetitivas de teclado e mouse com interface grafica.

O usuario pode cadastrar varias macros, cada uma com:

- tipo de acao (`key` ou `mouse`)
- valor da acao (tecla ou botao do mouse)
- intervalo em segundos

Todas as macros sao executadas em paralelo logico dentro de uma unica thread de trabalho, com um delay inicial opcional.

Atualmente o projeto tambem possui persistencia em arquivos JSON e suporte a distribuicao como executavel Windows.

## Stack e Dependencias

- Python 3.10+
- Tkinter (GUI nativa)
- `pynput==1.7.7` (controle de teclado e mouse)

## Estrutura Atual

- `app.py`: aplicacao completa (UI, validacao, modelo de dados e runtime de execucao).
- `README.md`: instrucoes de instalacao e uso.
- `requirements.txt`: dependencias Python.
- `saves/`: pasta de configuracoes salvas em JSON.
- `dist/`: saida do executavel (`mini-macro.exe`) quando gerado via PyInstaller.

## Arquitetura (app.py)

### Modelo

- `MacroItem` (`dataclass`)
  - `item_id`: identificador da macro
  - `action_type`: `"key"` ou `"mouse"`
  - `value`: texto da tecla ou botao (`left/right/middle`)
  - `interval`: intervalo em segundos

### Controlador/UI

- `MacroApp`
  - Monta a interface com `ttk`.
  - Gerencia lista de macros em memoria (`self.macros`).
  - Faz validacoes de entrada (tecla, intervalo, delay inicial).
  - Permite salvar e carregar macros pela secao de saves.
  - Controla estado de execucao (`start/stop`) e estados dos botoes/campos.

### Execucao de macros

- `start_macro()` cria agenda (`schedule`) com `next_run` para cada macro.
- `_run_macro(schedule)` roda em thread daemon e:
  - verifica macros vencidas pelo relogio monotonic (`time.monotonic()`)
  - executa acao
  - recalcula proxima execucao por `interval`
  - aguarda ate o proximo disparo (ou parada)
- `stop_macro()` sinaliza `stop_event` para interromper loop.

### Persistencia (saves)

- `save_macros()` salva em JSON na pasta `saves/`:
  - `version`
  - `start_delay`
  - lista `macros` com `action_type`, `value` e `interval`
- `load_selected_save()` carrega arquivo selecionado, valida dados e reconstrui `self.macros`.
- `_refresh_saves_list()` atualiza a listagem de arquivos `.json` para carregamento.
- Nome de save e sanitizado para aceitar apenas letras, numeros, `_` e `-`.

## Fluxo Funcional

1. Usuario seleciona tipo (tecla/mouse).
2. Informa valor e intervalo.
3. Adiciona/atualiza/remove itens na lista.
4. Informa delay inicial.
5. Opcionalmente salva a configuracao na secao de saves.
6. Opcionalmente carrega uma configuracao salva da pasta `saves/`.
7. Inicia execucao.
8. App dispara todas as macros em seus respectivos intervalos ate parar.

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
python -m PyInstaller --noconfirm --clean --onefile --windowed --name mini-macro app.py
```

Saida do executavel:

```text
dist/mini-macro.exe
```
