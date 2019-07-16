import random
from datetime import datetime

import markdown
from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for)
from sqlalchemy import func

from . import auth
from .auth import login_required
from .card_processing import load_md_files_to_db
from .config import Config
from .models import DB, Deck, FlashCard, Tag, User, User_Card


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(auth.bp)
    DB.init_app(app)

    @app.shell_context_processor
    def make_shell_context():
        return {'DB': DB, 'FlashCard': FlashCard, 'Tag': Tag, 'Deck': Deck,
                'User': User, 'User_Card': User_Card}

    @app.route('/reset')
    def reset():
        DB.drop_all()
        DB.create_all()
        load_md_files_to_db()
        return redirect(url_for('index'))

    @app.route('/', methods=('GET', 'POST'))
    @login_required
    def index():
        if request.method == 'POST' and 'start_quiz' in request.form:
            error = None

            if 'tag' not in request.form and 'deck' not in request.form:
                error = 'Must select tags or decks.'
            else:
                # queue deck of new cards
                requested_tags = request.form.getlist('tag')
                requested_decks = request.form.getlist('deck')

                cards_to_study = FlashCard.query.join(Deck).filter(
                    FlashCard.tags.any(Tag.name.in_(requested_tags)) |
                    Deck.name.in_(requested_decks)
                ).all()
                random.shuffle(cards_to_study)

                if not cards_to_study:
                    error = 'No cards found with selected tags.'

            if not error:
                user_id = session['user_id']
                clear_queued_cards(user_id)

                for queue_idx, card in enumerate(cards_to_study):
                    # check if card already in user_cards (add if not)
                    # assign order to cards in user_cards
                    queue_idx += 1  # to avoid 0
                    user_cards = User_Card.query.filter(
                        User_Card.flashcard_id == card.id,
                        User_Card.user_id == user_id
                    ).all()

                    if not user_cards:
                        user_card = User_Card(user_id=user_id,
                                              flashcard_id=card.id,
                                              queue_idx=queue_idx)
                        DB.session.add(user_card)
                    else:
                        user_card = user_cards[0]
                        user_card.queue_idx = queue_idx

                    DB.session.commit()

                return redirect(url_for('flashcard', id=cards_to_study[0].id))

            flash(error)

        deck_tags = {}
        decks = Deck.query.all()
        for deck in decks:
            tags = Tag.query.filter(
                Tag.flashcards.any(FlashCard.deck_id == deck.id)
            ).all()
            deck_tags[deck.name] = sorted([tag.name for tag in tags])

        return render_template('index.html', deck_tags=deck_tags)

    @app.route('/flashcard/<int:id>', methods=('GET', 'POST'))
    @login_required
    def flashcard(id):
        user_id = session['user_id']
        card = FlashCard.query.filter(FlashCard.id == id).one()
        user_card = User_Card.query.filter(
            User_Card.flashcard_id == id,
            User_Card.user_id == user_id,
        ).one()

        queue_idx_max = DB.session.query(func.max(User_Card.queue_idx)).filter(
            User_Card.user_id == user_id
        ).scalar()

        if request.method == 'POST':
            next_idx = user_card.queue_idx + 1
            user_card.queue_idx = None

            user_card.last_attempt_date = datetime.utcnow()
            user_card.total_attempts = user_card.total_attempts + 1

            if 'pass' in request.values:
                user_card.total_successful = user_card.total_successful + 1
                user_card.last_attempt_successful = True
            else:
                user_card.last_attempt_successful = False

            DB.session.commit()

            next_card = User_Card.query.filter(
                User_Card.user_id == user_id,
                User_Card.queue_idx == next_idx
            ).all()

            if not next_card:
                return redirect(url_for('complete'))
            else:
                return redirect(url_for('flashcard',
                                        id=next_card[0].flashcard_id))

        question_html = markdown.markdown(
            card.question,
            extensions=['markdown.extensions.fenced_code']
        )
        answer_html = markdown.markdown(
            card.answer,
            extensions=['markdown.extensions.fenced_code']
        )

        return render_template('flashcard.html',
                               question_html=question_html,
                               answer_html=answer_html,
                               n_total=queue_idx_max,
                               n_current=user_card.queue_idx)

    @app.route('/complete', methods=('GET', 'POST'))
    @login_required
    def complete():
        if request.method == 'POST':
            return redirect(url_for('index'))
        return render_template('complete.html')

    return app


def clear_queued_cards(user_id):
    cards_to_clear = User_Card.query.filter(
        User_Card.user_id == user_id,
        User_Card.queue_idx.isnot(None),
    ).all()

    for card in cards_to_clear:
        card.queue_idx = None

    DB.session.commit()

    return True
