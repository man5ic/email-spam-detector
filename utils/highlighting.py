"""Highlight the matched patterns inside the original email (HTML)."""
import html


def highlight_email(text, matches):
    # merge overlapping match intervals so <mark> tags never nest
    intervals = sorted((m.start, m.end) for m in matches)
    merged = []
    for start, end in intervals:
        if merged and start <= merged[-1][1] + 1:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])

    parts, cursor = [], 0
    for start, end in merged:
        parts.append(html.escape(text[cursor:start]))
        parts.append('<mark style="background:#ffd54f;color:#000;padding:0 2px;border-radius:3px;">'
                     + html.escape(text[start:end + 1]) + "</mark>")
        cursor = end + 1
    parts.append(html.escape(text[cursor:]))
    body = "".join(parts).replace("\n", "<br>")
    return f'<div style="line-height:1.7;padding:0.5rem 0;">{body}</div>'
