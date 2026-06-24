from fastapi import Request


def _get_text(key: str, request: Request) -> str:
    translation = getattr(request.state, "translation", None)
    if translation:
        return translation.gettext(key)
    return key


def get_translation_function(request: Request):

    return lambda key: _get_text(key, request)
