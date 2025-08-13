from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db

__all__ = [
    "RecordNotFound",
    "CommitError",
    "get_or_404",
    "commit_or_500",
    "paginate_query",
]

class RecordNotFound(Exception):
    pass

class CommitError(Exception):
    pass

def get_or_404(model, object_id):
    try:
        stmt = select(model).where(model.id == object_id)
        obj = db.session.execute(stmt).scalar_one_or_none()
        if obj is None:
            raise RecordNotFound(f"{model.__name__} with id {object_id} not found")
        return obj
    except SQLAlchemyError as e:
        raise CommitError(f"Database error: {e}")

def commit_or_500(obj=None, session=None):
    sess = session  
    try:
        if sess is None:
            sess = db.session
        if obj is not None:
            sess.add(obj)
        sess.commit()
        return obj
    except SQLAlchemyError as e:
        try:
            if sess is not None:
                sess.rollback()
        except Exception:
            pass
        raise CommitError(f"Database commit failed: {e}")

def paginate_query(query, page: int, per_page: int):
    try:
        items = db.session.execute(query.offset((page - 1) * per_page).limit(per_page)).scalars().all()
        total_query = select(func.count()).select_from(query.subquery())
        total = db.session.execute(total_query).scalar() or 0
        pages = (total + per_page - 1) // per_page if per_page else 1
        return {
            "items": items,
            "meta": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": pages,
            },
        }
    except SQLAlchemyError as e:
        raise CommitError(f"Database error: {e}")
