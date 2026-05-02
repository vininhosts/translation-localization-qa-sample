"""Generate a compact PDF case study using only the Python standard library."""

from __future__ import annotations

from pathlib import Path
from textwrap import wrap


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "deliverables" / "case_study.pdf"
PAGE_WIDTH = 612
PAGE_HEIGHT = 792
MARGIN = 54
LINE_HEIGHT = 14


def pdf_text(value: str) -> str:
    encoded = value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    return encoded


def add_line(lines: list[tuple[str, int, bool]], text: str = "", size: int = 10, bold: bool = False) -> None:
    lines.append((text, size, bold))


def build_lines() -> list[tuple[str, int, bool]]:
    lines: list[tuple[str, int, bool]] = []
    add_line(lines, "English to Brazilian Portuguese Localization QA Sample", 18, True)
    add_line(lines, "Self-initiated portfolio case study for translation, localization QA, and AI/software content review.", 10)
    add_line(lines)
    add_line(lines, "Project Summary", 14, True)
    add_line(lines, "Language pair: English to Brazilian Portuguese")
    add_line(lines, "Content type: SaaS app copy, onboarding text, UI strings, and help-center copy")
    add_line(lines, "Sample status: portfolio demonstration, not client work")
    add_line(lines)
    add_line(lines, "English Source Sample", 14, True)
    add_line(lines, "Stay focused without losing track of the details. TaskPilot AI captures your notes, highlights decisions, and suggests action items so your team can move faster after every meeting.")
    add_line(lines, "Review the suggested action items before sharing them. You stay in control of what gets sent.")
    add_line(lines)
    add_line(lines, "Brazilian Portuguese Translation", 14, True)
    add_line(lines, "Mantenha o foco sem perder os detalhes importantes. O TaskPilot AI captura suas anotações, destaca decisões e sugere itens de ação para que sua equipe avance com mais rapidez depois de cada reunião.")
    add_line(lines, "Revise os itens de ação sugeridos antes de compartilhá-los. Você mantém o controle sobre o que será enviado.")
    add_line(lines)
    add_line(lines, "UI String Samples", 14, True)
    add_line(lines, "New summary -> Novo resumo")
    add_line(lines, "Upload transcript -> Enviar transcrição")
    add_line(lines, "Generate action items -> Gerar itens de ação")
    add_line(lines, "Assign owner -> Atribuir responsável")
    add_line(lines, "Review before sending -> Revisar antes de enviar")
    add_line(lines)
    add_line(lines, "Terminology Decisions", 14, True)
    add_line(lines, "action items -> itens de ação: common in business/productivity contexts.")
    add_line(lines, "owners -> responsáveis: natural task-management wording; avoids literal 'donos'.")
    add_line(lines, "follow-up messages -> mensagens de acompanhamento: preserves meaning without unnecessary English borrowing.")
    add_line(lines, "Settings -> Configurações: standard software UI term.")
    add_line(lines, "workspace -> espaço de trabalho: common SaaS localization term.")
    add_line(lines)
    add_line(lines, "Quality Checks", 14, True)
    add_line(lines, "- Meaning preserved from source to target.")
    add_line(lines, "- Brazilian Portuguese reads naturally, not literally translated.")
    add_line(lines, "- Product name remains unchanged.")
    add_line(lines, "- UI strings are concise enough for buttons and menus.")
    add_line(lines, "- Terminology is consistent across app-store copy, onboarding, UI, and help center text.")
    add_line(lines, "- Safety/help-center warning remains clear and direct.")
    add_line(lines)
    add_line(lines, "Created by Vini Siqueira as a self-initiated portfolio sample.", 9)
    return lines


def paginate(lines: list[tuple[str, int, bool]]) -> list[list[tuple[str, int, bool]]]:
    pages: list[list[tuple[str, int, bool]]] = [[]]
    current_y = PAGE_HEIGHT - MARGIN
    usable_width_chars = 88
    for text, size, bold in lines:
        wrapped = [""] if not text else wrap(text, width=usable_width_chars)
        for part in wrapped:
            if current_y < MARGIN:
                pages.append([])
                current_y = PAGE_HEIGHT - MARGIN
            pages[-1].append((part, size, bold))
            current_y -= LINE_HEIGHT if size <= 10 else LINE_HEIGHT + 6
    return pages


def page_stream(page: list[tuple[str, int, bool]]) -> bytes:
    y = PAGE_HEIGHT - MARGIN
    commands = ["BT"]
    for text, size, bold in page:
        font = "F2" if bold else "F1"
        commands.append(f"/{font} {size} Tf")
        commands.append(f"{MARGIN} {y} Td")
        commands.append(f"({pdf_text(text)}) Tj")
        commands.append(f"{-MARGIN} 0 Td")
        y -= LINE_HEIGHT if size <= 10 else LINE_HEIGHT + 6
    commands.append("ET")
    return "\n".join(commands).encode("latin-1", errors="replace")


def write_pdf(pages: list[list[tuple[str, int, bool]]]) -> None:
    objects: list[bytes] = []
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")

    page_object_numbers = []
    content_object_numbers = []
    next_obj = 4
    for _page in pages:
        page_object_numbers.append(next_obj)
        content_object_numbers.append(next_obj + 1)
        next_obj += 2

    kids = " ".join(f"{num} 0 R" for num in page_object_numbers)
    objects.append(f"<< /Type /Pages /Kids [{kids}] /Count {len(pages)} >>".encode("latin-1"))
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>")

    for page_num, content_num, page in zip(page_object_numbers, content_object_numbers, pages):
        page_obj = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] "
            f"/Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> /Contents {content_num} 0 R >>"
        ).encode("latin-1")
        stream = page_stream(page)
        content_obj = b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream"
        objects.append(page_obj)
        objects.append(content_obj)

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{index} 0 obj\n".encode("ascii"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")
    xref_pos = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode("ascii")
    )
    OUT.write_bytes(pdf)


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    write_pdf(paginate(build_lines()))


if __name__ == "__main__":
    main()
