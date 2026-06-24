import gettext
import os
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.requests import Request
from starlette.responses import Response
from starlette.datastructures import MutableHeaders

LOCALE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "locales"
)


class I18nMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        default_locale="en",
        supported_locales=["en", "fa"],
        locale_dir=LOCALE_DIR,
    ):
        super().__init__(app)
        self.default_locale = default_locale
        self.locale_dir = locale_dir
        self.supported_locales = supported_locales
        self.translations = {}

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        locale = self.get_locale(request)

        translation = self.load_translation(locale)
        request.state.translation = translation
        request.state.locale = locale

        response = await call_next(request)

        headers = MutableHeaders(response.headers)
        headers["X-Locale"] = locale

        return response

    def get_locale(self, request: Request):
        accept_language = request.headers.get("Accept-Language")
        if accept_language:
            if accept_language in self.supported_locales:
                return accept_language
        return self.default_locale

    def load_translation(self, locale: str):
        if locale in self.translations:
            return self.translations[locale]

        try:
            translation = gettext.translation(
                domain="messages",
                localedir=self.locale_dir,
                languages=[locale],
                fallback=True,
            )
            self.translations[locale] = translation
            return translation
        except FileNotFoundError:
            print(
                "Warning: Locale directory or .mo file not found for "
                f"'{locale}'. Falling back."
            )
            return gettext.NullTranslations()
