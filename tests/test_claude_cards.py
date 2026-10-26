from llm_history_converter.adapters.claude_cards import render_card


def _card(name: str, data: dict) -> dict:
    return {"type": "tool_use", "name": name, "input": data}


def test_step_card():
    block = _card("step_card_display_v0", {
        "summary": "Como publicar o site",
        "steps": [
            {"title": "Gerar o build", "description": "Rode npm run build."},
            {"title": "Enviar", "description": "Suba a pasta dist."},
        ],
    })
    assert render_card(block) == (
        "**Passo a passo:** Como publicar o site\n"
        "\n"
        "1. **Gerar o build**\n"
        "   Rode npm run build.\n"
        "2. **Enviar**\n"
        "   Suba a pasta dist."
    )


def test_step_card_indents_multiline_description():
    block = _card("step_card_display_v0", {
        "summary": "",
        "steps": [{"title": "Instalar", "description": "Primeira linha\nSegunda linha"}],
    })
    assert render_card(block) == (
        "**Passo a passo:**\n"
        "\n"
        "1. **Instalar**\n"
        "   Primeira linha\n"
        "   Segunda linha"
    )


def test_question_card_with_type():
    block = _card("ask_user_input_v0", {
        "questions": [
            {"question": "Qual banco você prefere?", "options": ["PostgreSQL", "SQLite"], "type": "single_select"},
            {"question": "Quais extras?", "options": ["Docker"], "type": "multi_select"},
        ],
    })
    assert render_card(block) == (
        "**Pergunta:** Qual banco você prefere? (escolha uma)\n"
        "- PostgreSQL\n"
        "- SQLite\n"
        "\n"
        "**Pergunta:** Quais extras? (escolha várias)\n"
        "- Docker"
    )


def test_question_card_without_type():
    block = _card("ask_user_input_v0", {"questions": [{"question": "Seguimos?", "options": ["Sim", "Não"]}]})
    assert render_card(block) == "**Pergunta:** Seguimos?\n- Sim\n- Não"


def test_message_card_with_variants():
    block = _card("message_compose_v1", {
        "kind": "email",
        "summary_title": "Pedido de prazo",
        "variants": [
            {"label": "Formal", "subject": "Prazo do trabalho", "body": "Prezado professor, ..."},
            {"label": "Direta", "body": "Oi, professor, ..."},
        ],
    })
    assert render_card(block) == (
        "**Rascunho de mensagem (e-mail):** Pedido de prazo\n"
        "\n"
        "**Formal**\n"
        "Assunto: Prazo do trabalho\n"
        "\n"
        "Prezado professor, ...\n"
        "\n"
        "**Direta**\n"
        "\n"
        "Oi, professor, ..."
    )


def test_message_card_single_variant_has_no_label():
    block = _card("message_compose_v1", {
        "kind": "other",
        "summary_title": "Aviso",
        "variants": [{"label": "Única", "body": "Chego às 10h."}],
    })
    assert render_card(block) == "**Rascunho de mensagem:** Aviso\n\nChego às 10h."


def test_message_card_unlabeled_variants_are_numbered():
    block = _card("message_compose_v1", {
        "kind": "textMessage",
        "summary_title": "Convite",
        "variants": [{"body": "Bora?"}, {"body": "Vamos?"}],
    })
    assert render_card(block) == (
        "**Rascunho de mensagem (mensagem de texto):** Convite\n"
        "\n"
        "**Versão 1**\n"
        "\n"
        "Bora?\n"
        "\n"
        "**Versão 2**\n"
        "\n"
        "Vamos?"
    )


def test_options_card():
    block = _card("options_card_display_v0", {
        "summary": "Onde hospedar",
        "options": [
            {"title": "Vercel", "description": "Grátis para projetos pessoais.",
             "bullets": ["Deploy pelo GitHub", "Sem servidor"]},
        ],
    })
    assert render_card(block) == (
        "**Opções:** Onde hospedar\n"
        "\n"
        "- **Vercel:** Grátis para projetos pessoais.\n"
        "  - Deploy pelo GitHub\n"
        "  - Sem servidor"
    )


def test_comparison_card():
    block = _card("comparison_card_display_v0", {
        "summary": "Fones até R$ 300",
        "products": [
            {"name": "Fone A", "price": "R$ 250", "attributes": [{"label": "Bateria", "value": "20 h"}]},
            {"name": "Fone B", "attributes": [{"label": "Bateria", "value": "30 h"}]},
        ],
    })
    assert render_card(block) == (
        "**Comparação:** Fones até R$ 300\n"
        "\n"
        "- **Fone A** (R$ 250)\n"
        "  - Bateria: 20 h\n"
        "- **Fone B**\n"
        "  - Bateria: 30 h"
    )


def test_link_card():
    block = _card("link_preview_display_v0", {
        "summary": "Documentação",
        "links": [{"title": "Guia do pytest", "url": "https://docs.pytest.org",
                   "domain": "docs.pytest.org", "snippet": "Como escrever testes."}],
    })
    assert render_card(block) == (
        "**Links:** Documentação\n"
        "\n"
        "- [Guia do pytest](https://docs.pytest.org) (docs.pytest.org)\n"
        "  Como escrever testes."
    )


def test_quiz_card_marks_correct_option():
    block = _card("quiz_display_v0", {
        "title": "Revisão de Python",
        "description": "Três perguntas rápidas",
        "summary": "Quiz",
        "questions": [{
            "id": "q1", "prompt": "Qual tipo é imutável?", "question_type": "multiple_choice",
            "options": [{"id": "a", "text": "list"}, {"id": "b", "text": "tuple"}],
            "correct_option_id": "b", "hint": "Pense em parênteses.",
            "explanation": "tuplas não podem ser alteradas depois de criadas.",
            "correct_feedback": "Isso!", "incorrect_feedback": "Quase.",
        }],
    })
    assert render_card(block) == (
        "**Quiz: Revisão de Python** - Três perguntas rápidas\n"
        "\n"
        "1. Qual tipo é imutável?\n"
        "   - list\n"
        "   - tuple ✅\n"
        "   Explicação: tuplas não podem ser alteradas depois de criadas."
    )


def test_chart_card():
    block = _card("chart_display_v0", {
        "title": "Horas de estudo", "style": "bar",
        "x_axis": {"data": ["Seg", "Ter"]}, "y_axis": {"title": "Horas"},
        "series": [{"name": "Semana 1", "values": [2, 3]}],
    })
    assert render_card(block) == (
        "**Gráfico:** Horas de estudo (eixo Y: Horas)\n"
        "\n"
        "| | Semana 1 |\n"
        "|---|---|\n"
        "| Seg | 2 |\n"
        "| Ter | 3 |"
    )


def test_regular_tool_is_ignored():
    assert render_card(_card("bash_tool", {"command": "ls"})) == ""
