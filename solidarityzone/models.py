from typing import List

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class BaseMixin(object):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(
        db.DateTime(timezone=True), server_default=db.func.now(), index=True
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        server_default=db.func.now(),
        onupdate=db.func.now(),
        nullable=False,
    )


class ScrapeState(BaseMixin, db.Model):
    __tablename__ = "scrape_state"
    __table_args__ = {"sqlite_autoincrement": True}

    batch_next_index = db.Column(db.Integer, nullable=False)


class ScrapeSession(BaseMixin, db.Model):
    __tablename__ = "scrape_sessions"
    __table_args__ = {"sqlite_autoincrement": True}

    court_id: db.Mapped[int] = db.mapped_column(
        db.ForeignKey("courts.id"), nullable=True
    )
    court: db.Mapped["Court"] = db.relationship()

    input_article = db.Column(db.String, nullable=False)
    input_court_code = db.Column(db.String, nullable=False)
    created_cases = db.Column(db.Integer, nullable=False)
    updated_cases = db.Column(db.Integer, nullable=False)
    ignored_cases = db.Column(db.Integer, nullable=False)
    is_successful = db.Column(db.Boolean, nullable=False)
    is_captcha = db.Column(db.Boolean, nullable=False)
    is_captcha_successful = db.Column(db.Boolean, nullable=False)
    error_type = db.Column(db.String)
    debug_message = db.Column(db.String)


class ScrapeLog(BaseMixin, db.Model):
    __tablename__ = "scrape_log"
    __table_args__ = {"sqlite_autoincrement": True}

    scrape_session_id: db.Mapped[int] = db.mapped_column(
        db.ForeignKey("scrape_sessions.id"), nullable=False
    )
    scrape_session: db.Mapped["ScrapeSession"] = db.relationship()
    case_id: db.Mapped[int] = db.mapped_column(
        db.ForeignKey("cases.id"), nullable=False
    )
    case: db.Mapped["Case"] = db.relationship()

    is_update = db.Column(db.Boolean, nullable=False)
    diff = db.Column(db.String, nullable=False)


class Region(BaseMixin, db.Model):
    __tablename__ = "regions"
    __table_args__ = (
        db.UniqueConstraint("name"),
        {"sqlite_autoincrement": True},
    )

    courts: db.Mapped[List["Court"]] = db.relationship()

    name = db.Column(db.String, nullable=False)


class Court(BaseMixin, db.Model):
    __tablename__ = "courts"
    __table_args__ = (
        db.UniqueConstraint("code"),
        {"sqlite_autoincrement": True},
    )

    region_id: db.Mapped[int] = db.mapped_column(
        db.ForeignKey("regions.id"), nullable=False
    )
    region: db.Mapped["Region"] = db.relationship(back_populates="courts")

    name = db.Column(db.String, nullable=False)
    code = db.Column(db.String, nullable=False)
    is_military = db.Column(db.Boolean, nullable=False)


class Case(BaseMixin, db.Model):
    __tablename__ = "cases"
    __table_args__ = (
        # Sometimes two defendants are mentioned within one case,
        # in case they are both anonymized we distinct them via
        # articles
        db.UniqueConstraint("case_number", "court_id", "articles", "defendant_name"),
        {"sqlite_autoincrement": True},
    )

    court_id: db.Mapped[int] = db.mapped_column(
        db.ForeignKey("courts.id"), nullable=False
    )
    court: db.Mapped["Court"] = db.relationship()

    articles = db.Column(db.String)
    case_number = db.Column(db.String)
    defendant_name = db.Column(db.String)
    effective_date = db.Column(db.DateTime)
    entry_date = db.Column(db.DateTime, index=True)
    judge_name = db.Column(db.String)
    result = db.Column(db.String)
    result_date = db.Column(db.DateTime)
    sub_type = db.Column(db.String)
    url = db.Column(db.String)
