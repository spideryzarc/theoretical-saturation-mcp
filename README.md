# Theoretical Saturation MCP

Um servidor MCP (Model Context Protocol) escrito em Python, focado em gerenciar a saturação teórica para o seu processo de revisão bibliográfica. 

Este projeto foi estruturado com as melhores práticas para ser facilmente executável via `uvx`, permitindo que seja usado como uma ferramenta independente e de fácil integração.

## 🚀 Como usar com `uvx`

A estrutura de pacote do Python deste projeto permite que o servidor seja baixado, instalado e executado diretamente via GitHub usando a ferramenta `uv` (especificamente o comando `uvx`). 

Para rodá-lo, você pode usar um dos comandos abaixo em qualquer terminal (não requer clonagem do repositório):

```bash
# Se o repositório for público (substitua 'seu-usuario' pelo seu username do GitHub)
uvx --from git+https://github.com/seu-usuario/theoretical-saturation-mcp theoretical-saturation-mcp
```

### 🔌 Integração com o Claude Desktop

Você pode configurar este MCP no seu arquivo `claude_desktop_config.json` para que o Claude o carregue automaticamente sem que você precise instalar dependências de forma global:

```json
{
  "mcpServers": {
    "theoretical-saturation": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/seu-usuario/theoretical-saturation-mcp",
        "theoretical-saturation-mcp"
      ]
    }
  }
}
```

## 🛠️ Desenvolvimento Local

Caso você queira editar e testar o código do MCP, siga os passos abaixo:

1. **Instale o `uv`** (se ainda não o tiver)
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Clone este repositório** e entre na pasta:
   ```bash
   git clone https://github.com/seu-usuario/theoretical-saturation-mcp.git
   cd theoretical-saturation-mcp
   ```

3. **Rode o servidor localmente**:
   O comando `uv run` cuidará automaticamente de criar um ambiente virtual (se necessário) e baixar as dependências.
   ```bash
   uv run theoretical-saturation-mcp
   ```

## 📁 Estrutura do Projeto

* `pyproject.toml`: Configuração do pacote e dependências. Define também o comando `[project.scripts]` que possibilita rodar o MCP pelo nome via terminal ou `uvx`.
* `src/theoretical_saturation_mcp/main.py`: O "entry point" configurado que chama e inicia o MCP.
* `src/theoretical_saturation_mcp/server.py`: Onde as ferramentas (tools), recursos e a lógica do `FastMCP` estão implementados.
