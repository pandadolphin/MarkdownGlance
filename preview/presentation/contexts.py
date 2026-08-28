import sublime


def context_result(actual, operator, operand):
    expected = bool(operand)
    if operator == sublime.OP_NOT_EQUAL:
        return actual != expected
    return actual == expected


def preview_focused(window, backend):
    sheet = window.active_sheet() if window else None
    return bool(sheet and backend.owner_of(sheet))


def markdown_source(view):
    return bool(view and view.match_selector(0, "text.html.markdown"))
