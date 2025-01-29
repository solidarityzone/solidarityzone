import datetime

from celery import shared_task
from celery.utils.log import get_task_logger
from flask import current_app, json
from sqlalchemy.exc import IntegrityError

from .models import Case, Court, ScrapeLog, ScrapeSession, ScrapeState, db
from .scraper import CourtScraperMoscow, CourtScraperRegion
from .utils import group_by

logger = get_task_logger(__name__)


BEGIN_OF_WAR = "24.02.2022"

# "Meta" court code for handling all Moscow-based courts
ALL_MOSCOW_COURTS = "mos-gorsud"

# Hard-coded sub-type of legal case we always search for
SUB_TYPES = ["Первая инстанция", "Апелляционная инстанция"]

# Hard-coded list of articles which are scraped right now
ARTICLES = [
    "205",
    "207",
    "213",
    "214",
    "222",
    "223",
    "244",
    "280",
    "328",
    "329",
    "332",
    "337",
    "338",
    "339",
    "361",
]

CASE_FIELDS = [
    "articles",
    "case_number",
    "defendant_name",
    "effective_date",
    "entry_date",
    "judge_name",
    "result",
    "result_date",
    "url",
]

UPDATEABLE_CASE_FIELDS = [
    "effective_date",
    "judge_name",
    "result",
    "result_date",
]

CLEAN_UP_AFTER_DAYS = 7


# Helper method to find out if a case changed
def get_updated_fields(updated_case, current_case):
    changed_field_names = []

    if updated_case is None:
        return changed_field_names

    for field_name in UPDATEABLE_CASE_FIELDS:
        updated = getattr(updated_case, field_name)
        current = current_case[field_name]

        # Change format to make date comparison possible
        if "date" in field_name:
            if updated is not None:
                updated = updated.strftime("%d.%m.%Y")

            if current is not None:
                current = current.strftime("%d.%m.%Y")
        else:
            if updated is not None:
                updated = updated.strip()

            if current is not None:
                current = current.strip()

        if updated != current:
            changed_field_names.append(field_name)

    return changed_field_names


# Returns a JSON object as a string with all key/value pairs which got changed
def calculate_diff(case, updated_fields):
    case_dict = {}
    for field_name in updated_fields:
        if "date" in field_name and case[field_name] is not None:
            case_dict[field_name] = case[field_name].isoformat()
        else:
            case_dict[field_name] = case[field_name]
    return json.dumps(case_dict)


@shared_task(ignore_result=True)
def scrape_court(court_code, article, sub_type):
    with current_app.app_context():
        # Hard-coded scrape parameters
        entry_date = {"from": BEGIN_OF_WAR, "to": ""}
        result_date = {"from": "", "to": ""}

        logger.info(
            "Start scraping with: sub_type='{}', article={}, \
entry_date={}, court_code={}".format(
                sub_type, article, BEGIN_OF_WAR, court_code
            )
        )

        # Run scraper
        if court_code == ALL_MOSCOW_COURTS:
            scraper = CourtScraperMoscow()
        else:
            scraper = CourtScraperRegion(court_code)
        data = scraper.get_court_data(article, sub_type, entry_date, result_date)
        (
            error,
            error_type,
            error_debug_message,
            urls,
            is_captcha,
            is_captcha_successful,
            data_items,
        ) = (
            data["error"],
            data["error_type"],
            data["error_debug_message"],
            data["url"],
            data["is_captcha"],
            data["is_captcha_successful"],
            data["result"],
        )

        # Format debug and error messages
        debug_message = "court_code={}\narticle={}\nsub_type={}\nis_captcha={}\nis_captcha_successful={}\nerror_type={}\nurls=\n* {}\ndebug_message={}".format(
            court_code,
            article,
            sub_type,
            is_captcha,
            is_captcha_successful,
            error_type,
            "\n* ".join(urls),
            error_debug_message,
        )

        if error and len(data_items) == 0:
            # Insert scrape session even when it was not successful, it will help us during debugging
            court = (
                db.session.execute(db.select(Court).where(Court.code == court_code))
                .scalars()
                .first()
            )
            if court is not None:
                court_id = court.id
            else:
                court_id = None
            query = db.insert(ScrapeSession).values(
                court_id=court_id,
                input_article=article,
                input_court_code=court_code,
                created_cases=0,
                updated_cases=0,
                ignored_cases=0,
                is_successful=not error,
                is_captcha=is_captcha,
                is_captcha_successful=is_captcha_successful,
                error_type=str(error_type),
                debug_message=debug_message,
            )
            db.session.execute(query)
            db.session.commit()
            raise Exception("Scraper failed with error_type={}".format(error_type))

        elif error:
            logger.error(
                "Scraper failed but found {} data items, error_type={}".format(
                    len(data_items), error_type
                )
            )
        else:
            logger.info("Scraper found total {} data items".format(len(data_items)))

        # Group results by court code
        grouped_by_court = group_by(data_items, "court_code")
        total_created_cases = 0
        total_updated_cases = 0
        total_ignored_cases = 0

        for group in grouped_by_court:
            group_court_code = group[0]["court_code"]

            # Get court from database
            court = (
                db.session.execute(
                    db.select(Court).where(Court.code == group_court_code)
                )
                .scalars()
                .first()
            )
            if court is None:
                raise Exception(
                    "Could not find court with code '{}' in database".format(court_code)
                )

            # Insert scrape session with initial values, to be completed later when we're done
            query = db.insert(ScrapeSession).values(
                court_id=court.id,
                input_article=article,
                input_court_code=court_code,
                created_cases=0,
                updated_cases=0,
                ignored_cases=0,
                is_successful=not error,
                is_captcha=is_captcha,
                is_captcha_successful=is_captcha_successful,
                error_type=str(error_type),
                debug_message=debug_message,
            )
            session_data = db.session.execute(query)
            session_id = session_data.inserted_primary_key[0]
            db.session.commit()

            # Create or update all cases from this court group
            created_cases = 0
            updated_cases = 0
            ignored_cases = 0
            for item in group:
                # Check if case already exists
                query = db.select(Case).where(
                    Case.articles == item["articles"],
                    Case.case_number == item["case_number"],
                    Case.defendant_name == item["defendant_name"],
                    Case.court_id == court.id,
                )
                existing_case = db.session.execute(query).scalars().first()

                # Find out how many fields got changed when case already existed
                updated_fields = get_updated_fields(existing_case, item)

                if not existing_case:
                    try:
                        # Create new case
                        query = db.insert(Case).values(
                            articles=item["articles"],
                            case_number=item["case_number"],
                            defendant_name=item["defendant_name"],
                            effective_date=item["effective_date"],
                            entry_date=item["entry_date"],
                            judge_name=item["judge_name"],
                            result=item["result"],
                            result_date=item["result_date"],
                            court_id=court.id,
                            sub_type=sub_type,
                            url=item["url"],
                        )
                        case_data = db.session.execute(query)
                        case_id = case_data.inserted_primary_key[0]

                        # Keep history of all fields which got created
                        query = db.insert(ScrapeLog).values(
                            is_update=False,
                            scrape_session_id=session_id,
                            case_id=case_id,
                            diff=calculate_diff(item, CASE_FIELDS),
                        )
                        db.session.execute(query)

                        db.session.commit()
                        created_cases += 1
                    except IntegrityError as err:
                        # Silently ignore duplicate errors, we should have checked for them,
                        # so this is a race condition
                        print(err)
                elif len(updated_fields) > 0:
                    # Update existing case
                    query = (
                        db.update(Case)
                        .where(Case.id == existing_case.id)
                        .values(
                            effective_date=item["effective_date"],
                            judge_name=item["judge_name"],
                            result=item["result"],
                            result_date=item["result_date"],
                            url=item["url"],
                        )
                    )
                    db.session.execute(query)

                    # Keep history of all fields which got updated
                    query = db.insert(ScrapeLog).values(
                        is_update=True,
                        scrape_session_id=session_id,
                        case_id=existing_case.id,
                        diff=calculate_diff(item, updated_fields),
                    )
                    db.session.execute(query)

                    db.session.commit()
                    updated_cases += 1
                else:
                    # Do nothing
                    ignored_cases += 1

            # Finalize scrape session
            query = (
                db.update(ScrapeSession)
                .where(ScrapeSession.id == session_id)
                .values(
                    created_cases=created_cases,
                    updated_cases=updated_cases,
                    ignored_cases=ignored_cases,
                )
            )
            db.session.execute(query)
            db.session.commit()

            # Increase total counters for further analytics
            total_created_cases = total_created_cases + created_cases
            total_updated_cases = total_updated_cases + updated_cases
            total_ignored_cases = total_ignored_cases + ignored_cases

        logger.info(
            "Successfully scraped page, \
created {} new cases, \
updated {} existing ones and ignored {}".format(
                total_created_cases, total_updated_cases, total_ignored_cases
            )
        )

        return {
            "created_cases": total_created_cases,
            "updated_cases": total_updated_cases,
            "ignored_cases": total_ignored_cases,
        }


@shared_task(ignore_result=True)
def scrape_test_courts():
    # Set of test courses which have been used during development of the
    # scraper. Use the (stateful) "scrape_next_batch" task for scraping _all_
    # courts in the database
    TEST_COURT_CODES = [
        ALL_MOSCOW_COURTS,
        "2zovs.msk",
        "1vovs--hbr",
        "1zovs--spb",
        "2vovs--cht",
        "covs--svd",
        "gor-kluch--krd",
        "groznensky--chn",
        "oblsud--kln",
        "oblsud--lo",
        "oblsud--vol",
        "sankt-peterburgsky--spb",
        "yovs--ros",
    ]
    for court_code in TEST_COURT_CODES:
        scrape_all_articles.apply_async((court_code,), retry=False)


@shared_task(ignore_result=True)
def scrape_all_articles(court_code):
    for article in ARTICLES:
        for sub_type in SUB_TYPES:
            scrape_court.apply_async((court_code, article, sub_type), retry=False)


@shared_task(ignore_result=True)
def scrape_next_batch(num_courts):
    # Use persisted state to identify progress of "batched" scraper
    query = db.select(ScrapeState).where(ScrapeState.id == 1)
    state = db.session.scalars(query).first()
    batch_next_index = 0
    if state is None:
        query = db.insert(ScrapeState).values(batch_next_index=0)
        db.session.execute(query)
        db.session.commit()
    else:
        batch_next_index = state.batch_next_index
    logger.info("Scrape next batch {}".format(batch_next_index))

    # Take next batch of courts from database and scrape them
    query = (
        db.select(Court)
        .order_by(Court.id.asc())
        .offset(batch_next_index * num_courts)
        .limit(num_courts)
    )
    courts = db.session.scalars(query).all()
    for court in courts:
        scrape_all_articles.apply_async((court.code,), retry=False)
    # Moscow courts are hard-coded and not in the database as they are a
    # special case, we trigger them here whenever the loop begins again
    if batch_next_index == 0:
        scrape_all_articles.apply_async((ALL_MOSCOW_COURTS,), retry=False)

    # Prepare state for next iteration
    if len(courts) == 0:
        logger.info("Reset batch counter")
        batch_next_index = 0
    else:
        batch_next_index += 1
    query = (
        db.update(ScrapeState)
        .where(ScrapeState.id == state.id)
        .values(batch_next_index=batch_next_index)
    )
    db.session.execute(query)
    db.session.commit()


@shared_task(ignore_result=True)
def clean_sessions():
    # Remove all sessions after some time which did not change data
    threshold = datetime.datetime.now() - datetime.timedelta(days=CLEAN_UP_AFTER_DAYS)
    query = db.delete(ScrapeSession).where(
        ScrapeSession.created_cases == 0,
        ScrapeSession.updated_cases == 0,
        ScrapeSession.created_at < threshold,
    )
    result = db.session.execute(query)
    db.session.commit()
    logger.info("Cleaned up {} scrape sessions".format(result.rowcount))
