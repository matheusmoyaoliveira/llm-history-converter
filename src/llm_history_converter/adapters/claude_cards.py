KIND_LABELS = {"email": "e-mail", "textMessage": "mensagem de texto"}
SELECT_LABELS = {"single_select": "escolha uma", "multi_select": "escolha várias"}


def _heading(label: str, summary: str = "") -> str:
    return f"**{label}:** {summary}" if summary else f"**{label}:**"


def _indent(text: str, prefix: str) -> str:
    return "\n".join(prefix + line for line in text.splitlines())


def _steps(data: dict) -> str:
    lines = [_heading("Passo a passo", data.get("summary", "")), ""]
    for number, step in enumerate(data.get("steps", []), start=1):
        lines.append(f"{number}. **{step.get('title', '')}**")
        if step.get("description"):
            lines.append(_indent(step["description"], "   "))
    return "\n".join(lines)


def _questions(data: dict) -> str:
    parts = []
    for question in data.get("questions", []):
        label = SELECT_LABELS.get(question.get("type"))
        suffix = f" ({label})" if label else ""
        lines = [f"**Pergunta:** {question.get('question', '')}{suffix}"]
        lines += [f"- {option}" for option in question.get("options", [])]
        parts.append("\n".join(lines))
    return "\n\n".join(parts)


def _message(data: dict) -> str:
    kind = KIND_LABELS.get(data.get("kind"))
    label = f"Rascunho de mensagem ({kind})" if kind else "Rascunho de mensagem"
    parts = [_heading(label, data.get("summary_title", ""))]
    variants = data.get("variants", [])
    for number, variant in enumerate(variants, start=1):
        header = []
        if len(variants) > 1:
            header.append(f"**{variant.get('label') or f'Versão {number}'}**")
        if variant.get("subject"):
            header.append(f"Assunto: {variant['subject']}")
        body = variant.get("body", "")
        parts.append("\n".join(header) + "\n\n" + body if header else body)
    return "\n\n".join(parts)


def _options(data: dict) -> str:
    lines = [_heading("Opções", data.get("summary", "")), ""]
    for option in data.get("options", []):
        name = option.get("title", "")
        description = option.get("description")
        lines.append(f"- **{name}:** {description}" if description else f"- **{name}**")
        lines += [f"  - {bullet}" for bullet in option.get("bullets", [])]
    return "\n".join(lines)


def _comparison(data: dict) -> str:
    lines = [_heading("Comparação", data.get("summary", "")), ""]
    for product in data.get("products", []):
        price = f" ({product['price']})" if product.get("price") else ""
        lines.append(f"- **{product.get('name', '')}**{price}")
        lines += [
            f"  - {attribute.get('label', '')}: {attribute.get('value', '')}"
            for attribute in product.get("attributes", [])
        ]
    return "\n".join(lines)


def _links(data: dict) -> str:
    lines = [_heading("Links", data.get("summary", "")), ""]
    for link in data.get("links", []):
        domain = f" ({link['domain']})" if link.get("domain") else ""
        lines.append(f"- [{link.get('title', '')}]({link.get('url', '')}){domain}")
        if link.get("snippet"):
            lines.append(_indent(link["snippet"], "  "))
    return "\n".join(lines)


def _quiz(data: dict) -> str:
    title = f"**Quiz: {data.get('title', '')}**"
    if data.get("description"):
        title += f" - {data['description']}"
    lines = [title, ""]
    for number, question in enumerate(data.get("questions", []), start=1):
        lines.append(f"{number}. {question.get('prompt', '')}")
        for option in question.get("options", []):
            mark = " ✅" if option.get("id") == question.get("correct_option_id") else ""
            lines.append(f"   - {option.get('text', '')}{mark}")
        if question.get("explanation"):
            lines.append(f"   Explicação: {question['explanation']}")
    return "\n".join(lines)


def _chart(data: dict) -> str:
    title = data.get("title", "")
    axis = (data.get("y_axis") or {}).get("title")
    if axis:
        title += f" (eixo Y: {axis})"
    series = data.get("series", [])
    lines = [
        _heading("Gráfico", title),
        "",
        "| | " + " | ".join(s.get("name", "") for s in series) + " |",
        "|---|" + "---|" * len(series),
    ]
    for index, label in enumerate((data.get("x_axis") or {}).get("data", [])):
        values = [s.get("values", []) for s in series]
        cells = [str(v[index]) if index < len(v) else "" for v in values]
        lines.append(f"| {label} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


CARDS = {
    "step_card_display_v0": _steps,
    "ask_user_input_v0": _questions,
    "message_compose_v1": _message,
    "options_card_display_v0": _options,
    "comparison_card_display_v0": _comparison,
    "link_preview_display_v0": _links,
    "quiz_display_v0": _quiz,
    "chart_display_v0": _chart,
}


def render_card(block: dict) -> str:
    render = CARDS.get(block.get("name"))
    return render(block.get("input") or {}) if render else ""
