from flask import Blueprint, request
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import class_mapper

from .models import Case, Court, Region, ScrapeLog, ScrapeSession, db

ITEMS_PER_PAGE = 50
ALLOWED_ITEMS_PER_PAGE = (10, 25, 50, 75, 100)

api = Blueprint("api", __name__, url_prefix="/api")


def cursor_encode(cursor: int) -> str:
    return str(cursor)


def cursor_decode(cursor: str) -> int:
    return int(cursor)


def pagination_args(request):
    before = request.args.get("before")
    after = request.args.get("after")
    if before is not None and after is not None:
        after = None
        before = None
    if before is not None:
        try:
            before = cursor_decode(before)
        except Exception:
            before = None
    if after is not None:
        try:
            after = cursor_decode(after)
        except Exception:
            after = None
    items_per_page = int(request.args.get("itemsPerPage", ITEMS_PER_PAGE))
    if items_per_page not in ALLOWED_ITEMS_PER_PAGE:
        items_per_page = ITEMS_PER_PAGE
    return (before, after, items_per_page)


def paginated_response(items, before, after, items_per_page, total_items):
    has_next_page = False
    has_previous_page = False
    if after is None and before is None:
        has_next_page = len(items) == items_per_page + 1
    elif after is not None:
        has_previous_page = True
        has_next_page = len(items) == items_per_page + 1
    elif before is not None:
        has_next_page = True
        has_previous_page = len(items) == items_per_page + 1
    items = items[0:items_per_page]

    return {
        "pagination": {
            "itemsPerPage": items_per_page,
            "totalItems": total_items,
            "hasNextPage": has_next_page,
            "hasPreviousPage": has_previous_page,
            # previous cursor is id of first item in this page
            "startCursor": None if len(items) == 0 else cursor_encode(items[0]["id"]),
            # next cursor is id of last item in this page
            "endCursor": None if len(items) == 0 else cursor_encode(items[-1]["id"]),
        },
        "items": items,
    }


# Convert database results to format which can be serialized to JSON
def serialize(model):
    columns = [c.key for c in class_mapper(model.__class__).columns]
    result = dict((c, getattr(model, c)) for c in columns)
    result["created_at"] = model.created_at.isoformat()
    result["updated_at"] = model.updated_at.isoformat()
    return result


def prepare_case(item):
    case_dict = serialize(item)
    if item.entry_date is not None:
        case_dict["entry_date"] = item.entry_date.isoformat()
    if item.result_date is not None:
        case_dict["result_date"] = item.result_date.isoformat()
    if item.effective_date is not None:
        case_dict["effective_date"] = item.effective_date.isoformat()
    if item.court is not None:
        case_dict["court"] = serialize(item.court)
        case_dict["region"] = serialize(item.court.region)
    else:
        case_dict["court"] = None
        case_dict["region"] = None
    return case_dict


def execute_cursor_pagination(
    before, after, items_per_page, base, id, col, query, filter
):
    # Retrieve total number of items
    count_query = query.where(*filter).subquery()
    total_items = db.session.execute(db.select(func.count(count_query.c.id))).scalar()

    # Prepare filter for cursor paginated query with multiple order by fields
    if after is not None:
        subquery = db.select(col).where(id == after).scalar_subquery()
        filter.append(
            and_(
                or_(
                    col < subquery,
                    and_(
                        col == subquery,
                        id > after,
                    ),
                ),
            )
        )
    elif before is not None:
        subquery = db.select(col).where(id == before).scalar_subquery()
        filter.append(
            and_(
                or_(
                    col > subquery,
                    and_(
                        col == subquery,
                        id < before,
                    ),
                ),
            )
        )

    # Base query for all pagination cases
    query = query.where(*filter)

    # Change ordering if we're paginating forwards or backwards
    if before is not None:
        query = query.order_by(col.asc(), id.desc())
    else:
        query = query.order_by(col.desc(), id.asc())

    # Always limit result
    query = query.limit(items_per_page + 1)

    # Wrap in a subquery and reverse ordering if we're paginating backwards
    if before is not None:
        subquery = query.subquery()
        alias = db.aliased(base, subquery)
        query = db.select(alias).order_by(
            alias.__getattr__(col.key).desc(), alias.__getattr__(id.key).asc()
        )

    # Finally process the results
    return (db.session.execute(query).scalars().all(), total_items)


# ~~~~~~~
# Regions
# ~~~~~~~


@api.route("/regions", methods=["GET"])
def regions():
    """
    List all regions
    """

    filter = []

    # Search by "name"
    name_search = request.args.get("name", None)
    if name_search is not None:
        filter.append(and_(Region.name.contains(name_search.strip())))

    # Filter by "id"
    ids = request.args.getlist("id")
    if len(ids) > 0:
        filter.append(and_(Region.id.in_(ids)))

    def prepare_results(items):
        dicts = []
        for item in items:
            item_dict = serialize(item)
            dicts.append(item_dict)
        return dicts

    query = db.select(Region)

    # Execute w. cursor-based pagination
    (before, after, items_per_page) = pagination_args(request)
    (items, total_items) = execute_cursor_pagination(
        before, after, items_per_page, Region, Region.id, Region.name, query, filter
    )
    items = prepare_results(items)
    return paginated_response(items, before, after, items_per_page, total_items)


# ~~~~~~
# Courts
# ~~~~~~


@api.route("/courts", methods=["GET"])
def courts():
    """
    List all courts
    """

    filter = []

    # Search by "name"
    name_search = request.args.get("name", None)
    if name_search is not None:
        filter.append(and_(Court.name.contains(name_search.strip())))

    # Filter by "id"
    ids = request.args.getlist("id")
    if len(ids) > 0:
        filter.append(and_(Court.id.in_(ids)))

    # Filter by region "id"
    region_ids = request.args.getlist("region")
    if len(region_ids) > 0:
        filter.append(and_(Region.id.in_(region_ids)))

    def prepare_results(items):
        dicts = []
        for item in items:
            item_dict = serialize(item)
            item_dict["region"] = serialize(item.region)
            dicts.append(item_dict)
        return dicts

    query = db.select(Court).join(Region)

    # Execute w. cursor-based pagination
    (before, after, items_per_page) = pagination_args(request)
    (items, total_items) = execute_cursor_pagination(
        before, after, items_per_page, Court, Court.id, Court.name, query, filter
    )
    items = prepare_results(items)
    return paginated_response(items, before, after, items_per_page, total_items)


@api.route("/courts/<int:id>", methods=["GET"])
def court(id):
    """
    Court details
    """
    query = db.select(Court).join(Region).where(Court.id == id)
    result = db.session.execute(query).scalars().first()
    case_dict = serialize(result)
    case_dict["region"] = serialize(result.region)
    return case_dict


@api.route("/courts/<int:id>/history", methods=["GET"])
def court_history(id):
    """
    History of all case updates for this court
    """

    def prepare_results(items):
        dicts = []
        for item in items:
            item_dict = serialize(item)
            item_dict["case"] = prepare_case(item.case)
            dicts.append(item_dict)
        return dicts

    query = db.select(ScrapeLog).join(Case)
    filter = [Case.court_id == id]

    # Execute w. cursor-based pagination
    (before, after, items_per_page) = pagination_args(request)
    (items, total_items) = execute_cursor_pagination(
        before,
        after,
        items_per_page,
        ScrapeLog,
        ScrapeLog.id,
        ScrapeLog.created_at,
        query,
        filter,
    )
    items = prepare_results(items)
    return paginated_response(items, before, after, items_per_page, total_items)


# ~~~~~~~~
# Sessions
# ~~~~~~~~


@api.route("/sessions", methods=["GET"])
def sessions():
    """
    List all scrape sessions
    """

    def prepare_results(items):
        dicts = []
        for item in items:
            item_dict = serialize(item)
            if item.court is not None:
                item_dict["court"] = serialize(item.court)
                item_dict["region"] = serialize(item.court.region)
            else:
                item_dict["court"] = None
                item_dict["region"] = None
            if item.error_type == "None":
                item_dict["error_type"] = None
            dicts.append(item_dict)
        return dicts

    query = db.select(ScrapeSession).outerjoin(Court).outerjoin(Region)
    filter = []

    # Execute w. cursor-based pagination
    (before, after, items_per_page) = pagination_args(request)
    (items, total_items) = execute_cursor_pagination(
        before,
        after,
        items_per_page,
        ScrapeSession,
        ScrapeSession.id,
        ScrapeSession.created_at,
        query,
        filter,
    )
    items = prepare_results(items)
    return paginated_response(items, before, after, items_per_page, total_items)


@api.route("/sessions/<int:id>", methods=["GET"])
def session(id):
    """
    Session details
    """
    query = (
        db.select(ScrapeSession)
        .outerjoin(Court)
        .outerjoin(Region)
        .where(ScrapeSession.id == id)
    )

    result = db.session.execute(query).scalars().first()
    session_dict = serialize(result)
    if result.court is not None:
        session_dict["court"] = serialize(result.court)
        session_dict["region"] = serialize(result.court.region)
    else:
        session_dict["court"] = None
        session_dict["region"] = None
    if result.error_type == "None":
        session_dict["error_type"] = None
    return session_dict


@api.route("/sessions/<int:id>/history", methods=["GET"])
def session_history(id):
    """
    History of all session updates
    """

    def prepare_results(items):
        dicts = []
        for item in items:
            item_dict = serialize(item)
            item_dict["case"] = prepare_case(item.case)
            dicts.append(item_dict)
        return dicts

    query = db.select(ScrapeLog).join(Case)
    filter = [ScrapeLog.scrape_session_id == id]

    # Execute w. cursor-based pagination
    (before, after, items_per_page) = pagination_args(request)
    (items, total_items) = execute_cursor_pagination(
        before,
        after,
        items_per_page,
        ScrapeLog,
        ScrapeLog.id,
        ScrapeLog.created_at,
        query,
        filter,
    )
    items = prepare_results(items)
    return paginated_response(items, before, after, items_per_page, total_items)


# ~~~~~
# Cases
# ~~~~~


@api.route("/cases", methods=["GET"])
def cases():
    """
    List all cases
    """

    filter = []

    # Search by "defendant_name"
    defendant_names = list(
        map(
            lambda i: db.column("defendant_name").contains(i.strip()),
            request.args.getlist("defendant"),
        )
    )
    if len(defendant_names) > 0:
        filter.append(and_(*defendant_names))

    # Search by "judge_name"
    judge_names = list(
        map(
            lambda i: db.column("judge_name").contains(i.strip()),
            request.args.getlist("judge"),
        )
    )
    if len(judge_names) > 0:
        filter.append(and_(*judge_names))

    # Search by "article"
    articles = list(
        map(
            lambda i: db.column("articles").contains(i.strip()),
            request.args.getlist("article"),
        )
    )
    if len(articles) > 0:
        filter.append(and_(*articles))

    # Filter by court "id"
    court_ids = request.args.getlist("court")
    if len(court_ids) > 0:
        filter.append(and_(Court.id.in_(court_ids)))

    # Filter by region "id"
    region_ids = request.args.getlist("region")
    if len(region_ids) > 0:
        filter.append(and_(Region.id.in_(region_ids)))

    # Filter by "entry_date"
    entry_date_from = request.args.get("from")
    if entry_date_from is not None:
        filter.append(and_(Case.entry_date >= entry_date_from))
    entry_date_to = request.args.get("to")
    if entry_date_to is not None:
        filter.append(and_(Case.entry_date <= entry_date_to))

    # Filter by "result_date"
    result_date_from = request.args.get("rfrom")
    if result_date_from is not None:
        filter.append(and_(Case.result_date >= result_date_from))
    result_date_to = request.args.get("rto")
    if result_date_to is not None:
        filter.append(and_(Case.result_date <= result_date_to))

    # Filter by "effective_date"
    effective_date_from = request.args.get("ecfrom")
    if effective_date_from is not None:
        filter.append(and_(Case.effective_date >= effective_date_from))
    effectiv_date_to = request.args.get("ecto")
    if effectiv_date_to is not None:
        filter.append(and_(Case.effective_date <= effectiv_date_to))

    def prepare_results(items):
        dicts = []
        for item in items:
            item_dict = prepare_case(item)
            dicts.append(item_dict)

        return dicts

    query = db.select(Case).join(Court).join(Region)

    # Execute w. cursor-based pagination
    (before, after, items_per_page) = pagination_args(request)
    (items, total_items) = execute_cursor_pagination(
        before, after, items_per_page, Case, Case.id, Case.entry_date, query, filter
    )
    items = prepare_results(items)
    return paginated_response(items, before, after, items_per_page, total_items)


@api.route("/cases/<int:id>", methods=["GET"])
def case(id):
    """
    Case details
    """
    query = db.select(Case).join(Court).join(Region).where(Case.id == id)
    result = db.session.execute(query).scalars().first()
    return prepare_case(result)


@api.route("/cases/<int:id>/history", methods=["GET"])
def case_history(id):
    """
    History of all case updates
    """

    def prepare_results(items):
        dicts = []
        for item in items:
            item_dict = serialize(item)
            item_dict["case"] = prepare_case(item.case)
            dicts.append(item_dict)
        return dicts

    query = db.select(ScrapeLog).join(Case)
    filter = [Case.id == id]

    # Execute w. cursor-based pagination
    (before, after, items_per_page) = pagination_args(request)
    (items, total_items) = execute_cursor_pagination(
        before,
        after,
        items_per_page,
        ScrapeLog,
        ScrapeLog.id,
        ScrapeLog.created_at,
        query,
        filter,
    )
    items = prepare_results(items)
    return paginated_response(items, before, after, items_per_page, total_items)
