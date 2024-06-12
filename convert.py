import re


def parse(input_text):
    in_paragraph = False
    in_code_block = False
    buffer = []
    output = []
    code_language = ""

    def flush_paragraph():
        nonlocal in_paragraph
        if in_paragraph:
            output.append(f"<p>{''.join(buffer).rstrip()}</p>")
            buffer.clear()
            in_paragraph = False

    def flush_code_block():
        nonlocal in_code_block, code_language
        if in_code_block:
            language = code_language if code_language else "plaintext"
            output.append(f'<pre><code class="language-{language}">{"".join(buffer)}</code></pre>')

            buffer.clear()
            in_code_block = False
            code_language = ""

    lines = input_text.split("\n")
    for line in lines:
        line = line.rstrip()

        # horizontal line
        if line == "---":
            flush_paragraph()
            output.append("<hr>")
            continue

        # code block start or end
        code_block_match = re.match(r'^```(\w+)?', line)
        if line.startswith("```"):
            if in_code_block:
                flush_code_block()
            else:
                flush_paragraph()
                code_language = code_block_match.group(1) if code_block_match.group(1) else ""
                in_code_block = True
            continue

        # stuff in code block
        if in_code_block:
            buffer.append(escape_text(line) + "\n")
            continue

        # header
        header_match = re.match(r'^(#+)\s*(.*)', line)
        if header_match:
            flush_paragraph()
            level = len(header_match.group(1))
            content = header_match.group(2)
            output.append(f"<h{level}>{content}</h{level}>")
            continue

        # paragraphs and inline code
        if line:
            if not in_paragraph:
                in_paragraph = True
            processed_line = re.sub(r'`([^`]+)`', lambda m: f"<code>{escape_text(m.group(1))}</code>", line)
            buffer.append(processed_line + " ")
        else:
            flush_paragraph()

    # flush remaining buffer
    flush_paragraph()
    flush_code_block()

    return "\n".join(output)


def escape_text(content):
    replacements = [
        ("&", "&amp;"),
        ("<", "&lt;"),
        (">", "&gt;"),
        ("'", "&#39;"),
        ('"', "&quot;")
    ]
    for chr, replacement in replacements:
        content = content.replace(chr, replacement)
    return content


def generate_html(content):
    with open("template.html", "r", encoding="utf-8") as file:
        html_template = file.read()
    return html_template.format(content=parse(content))


if __name__ == "__main__":
    source_path = "source.txt"
    output_path = "output.html"

    with open(source_path, "r", encoding="utf-8") as file:
        content = file.read()

    converted_html = generate_html(content)

    with open(output_path, "w", encoding='utf-8') as file:
        file.write(converted_html)

    print(converted_html)
