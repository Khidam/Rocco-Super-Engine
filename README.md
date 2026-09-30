# Estante de Webnovels

Plugin local para Codex/ChatGPT que pesquisa referencias acessiveis, registra leitura, constroi perfis narrativos auditaveis e cria ou reescreve ficcao original em portugues brasileiro.

## Instalacao

Requisitos: Python 3.10+ e um host Codex com suporte a plugins e MCP por `stdio`.

1. Adicione este repositorio como marketplace local:
   ```bash
   codex plugin marketplace add /caminho/para/Rocco-Super-Engine
   ```
2. Instale o plugin:
   ```bash
   codex plugin install estante-de-webnovels@estante-de-webnovels
   ```
3. Reinicie/abra uma nova conversa e invoque a skill `estante-de-webnovels`.

Os dados ficam em `~/.local/share/estante-de-webnovels`. Para escolher outro armazenamento controlado por voce, defina `ESTANTE_DATA_DIR` antes de iniciar o host. Nao ha sincronizacao nem memoria remota implicita.

## Uso

- `Crie uma cena com esta ideia e sugira referencias entre Heavenly Jewel Change, The Legendary Moonlight Sculptor e Shadow Slave.`
- `Use esta traducao como referencia. Quero principalmente a organizacao das falas, os pensamentos e o espacamento dos paragrafos.`
- `Guarde o original e mostre outra versao com o perfil de Shadow Slave.`
- `Registre que parei no capitulo 18 e anote este link.`

O plugin so confirma um perfil depois de ler amostras textuais identificadas. A pesquisa web depende das ferramentas e da conectividade oferecidas pelo host; fontes com login, pagamento ou bloqueio nao sao contornadas. Nesses casos, ele registra a falha e solicita um trecho fornecido legalmente pelo usuario. O plugin armazena analises e referencias, nao bibliotecas de capitulos de terceiros.

## Desenvolvimento e validacao

```bash
python3 /opt/codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/estante-de-webnovels
PYTHONPATH=plugins/estante-de-webnovels/scripts python3 -m unittest discover -s plugins/estante-de-webnovels/scripts -p 'test_*.py'
```
