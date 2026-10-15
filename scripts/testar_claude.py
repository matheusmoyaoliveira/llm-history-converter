from pathlib import Path

from llm_history_converter.adapters.claude import load

caminho = Path.home() / ".jarvs" / "historico" / "claude" / "conversations.json"
conversas = load(caminho)

print("Conversas carregadas:", len(conversas))
print("Total de mensagens:", sum(len(c.messages) for c in conversas))
print("Autores encontrados:", {m.author for c in conversas for m in c.messages})