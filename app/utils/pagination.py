from typing import Generic, List, TypeVar
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import Query

T = TypeVar("T")  # Generic type for the items in the list


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic Pydantic model for paginated responses.
    """
    total: int = Field(..., description="Total number of items available.")
    offset: int = Field(...,
                        description="The starting offset for the current page.")
    limit: int = Field(...,
                       description="The maximum number of items per page.")
    items: List[T] = Field(...,
                           description="List of items for the current page.")


async def paginate(
    db: AsyncSession,
    query: Query,  
    skip: int = 0,
    limit: int = 100
) -> PaginatedResponse[T]:
    """
    Applies pagination to a SQLAlchemy query and returns a PaginatedResponse.
    """
    # Create a count query from the original query without limit/offset.
    # Using .subquery() ensures that any joins or filters in the original query
    # are correctly considered when calculating the total count.
    total_count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(total_count_query)
    total_items = total_result.scalar_one()

    paginated_items_query = query.offset(skip).limit(limit)
    items_result = await db.execute(paginated_items_query)
    items = items_result.scalars().unique().all()

    return PaginatedResponse(
        total=total_items,
        offset=skip,
        limit=limit,
        items=items
    )
