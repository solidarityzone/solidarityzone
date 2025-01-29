import json

import click
from flask import current_app

from . import tasks
from .models import Court, Region, db


@click.command("init-db")
def init_db_command():
    with current_app.app_context():
        # Create database tables
        click.echo("Create tables ..")
        db.create_all()

        # Populate database with initial courts and regions data
        click.echo("Populate database with initial data ..")
        with open("./solidarityzone/data/court-codes.json", "r") as file:
            data = json.load(file)
            courts_added = []
            for region_name, courts in data.items():
                # Insert region
                query = db.select(Region).where(Region.name == region_name)
                result = db.session.execute(query).scalars().first()
                if result is None:
                    query = db.insert(Region).values(name=region_name)
                    result = db.session.execute(query)
                    region_id = result.inserted_primary_key[0]
                else:
                    region_id = result.id

                # Insert courts in this region
                for court_name, court_code in courts.items():
                    query = db.select(Court).where(Court.code == court_code)
                    result = db.session.execute(query).scalars().first()
                    if result is None:
                        courts_added.append(court_code)
                        query = db.insert(Court).values(
                            name=court_name,
                            code=court_code,
                            # @TODO: Value should be inside the .json file
                            is_military=False,
                            region_id=region_id,
                        )
                        db.session.execute(query)
            db.session.commit()

    click.echo(
        "Initialized database successfully, added {} new courts".format(
            len(courts_added)
        )
    )


@click.command("scrape")
@click.argument("court_code")
@click.argument("article")
@click.argument("sub_type_index")
def scrape(court_code, article, sub_type_index):
    with current_app.app_context():
        click.echo("Send scraping task to worker queue ..")
        tasks.scrape_court.apply_async(
            (court_code, article, tasks.SUB_TYPES[int(sub_type_index)]), retry=False
        )


@click.command("scrape-all-articles")
@click.argument("court_code")
def scrape_all(court_code):
    with current_app.app_context():
        click.echo("Send scraping all articles task to worker queue ..")
        tasks.scrape_all_articles.apply_async((court_code,), retry=False)


@click.command("scrape-test-courts")
def scrape_test_courts():
    with current_app.app_context():
        click.echo("Send scraping test courts task to worker queue ..")
        tasks.scrape_test_courts.apply_async((), retry=False)


@click.command("scrape-next-batch")
def scrape_next_batch():
    with current_app.app_context():
        click.echo("Send scraping next batch task to worker queue ..")
        tasks.scrape_next_batch.apply_async((5,), retry=False)


@click.command("clean-sessions")
def clean_sessions():
    with current_app.app_context():
        click.echo("Send clean sessions task to worker queue ..")
        tasks.clean_sessions.apply_async((), retry=False)
