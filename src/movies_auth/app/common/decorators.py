from functools import wraps
from typing import Any

from flask import current_app, jsonify, request
from flask_jwt_extended import get_jwt
from flask_sqlalchemy.pagination import Pagination
from opentelemetry import trace as telemetry_trace
from opentelemetry.trace import Tracer

from movies_auth.app.common.exceptions import Forbidden
from movies_auth.app.common.module_loading import import_string
from movies_auth.app.common.pagination import PaginatedPage, get_pagination_params, paginate_list


def superuser_required(request_methods: list[str] | None = None) -> Any:
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            if not request_methods or request.method in request_methods:
                claims = get_jwt()
                is_superuser = claims.get("is_superuser")
                if not is_superuser:
                    raise Forbidden("Permission denied")
            return current_app.ensure_sync(fn)(*args, **kwargs)

        return decorator

    return wrapper


def paginate(page_size: int | None = None, ma_schema=None) -> Any:
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            fn_result = current_app.ensure_sync(fn)(*args, **kwargs)
            if isinstance(fn_result, Pagination):
                paginated_page = PaginatedPage(
                    total_count=fn_result.total,
                    total_pages=fn_result.pages,
                    next_page=fn_result.next_num,
                    prev_page=fn_result.prev_num,
                    results=fn_result.items,
                )
                if ma_schema:
                    paginated_page.results = ma_schema.dump(paginated_page.results, many=True)
                else:
                    paginated_page.serialize_results()
                return jsonify(paginated_page.dict())

            if isinstance(fn_result, list):
                _page_number, _page_size = get_pagination_params(page_size)
                paginated_page = paginate_list(
                    page_size=int(_page_size),
                    page_number=int(_page_number),
                    results=fn_result,
                )
                return jsonify(paginated_page.dict())

            return fn_result

        return decorator

    return wrapper


def trace(tracer: Tracer | None = None, span_name: str | None = None) -> Any:
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            _tracer = tracer
            if not _tracer:
                module_name = fn.__module__
                module_object = import_string(module_name)
                _tracer = getattr(module_object, "tracer", None)
                if not _tracer:
                    _tracer = telemetry_trace.get_tracer(module_name)

            with _tracer.start_as_current_span(span_name or fn.__name__):
                return current_app.ensure_sync(fn)(*args, **kwargs)

        return decorator

    return wrapper
