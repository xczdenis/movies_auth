import math

from flask import Request
from pydantic import BaseModel

from config import settings


class PaginatedPage(BaseModel):
    total_count: int
    total_pages: int
    next_page: int | None
    prev_page: int | None
    results: list


def paginate_list(
    page_size: int, page_number: int, results: list, total_count: int | None = None
) -> PaginatedPage:
    total_count = total_count or len(results)
    total_pages = 0
    if total_count > 0:
        total_pages = math.ceil(total_count / page_size)

    next_page = page_number + 1 if page_number < total_pages else None
    prev_page = None
    if page_number and page_number > 1:
        prev_page = page_number - 1
        if prev_page > total_pages:
            prev_page = total_pages

    start = (page_number - 1) * page_size
    end = start + page_size
    portion = results[start:end]

    return PaginatedPage(
        total_count=total_count,
        total_pages=total_pages,
        next_page=next_page,
        prev_page=prev_page,
        results=portion,
    )


def get_pagination_params(request: Request, page_size: int | None = None) -> tuple[int, int]:
    page_size = request.args.get(
        settings.PAGINATOR.page_size_query_path, page_size or settings.PAGINATOR.page_size
    )
    page_number = request.args.get(settings.PAGINATOR.page_number_query_path, 1)
    return page_size, page_number
