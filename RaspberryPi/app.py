from flask import Flask, request, render_template, make_response
from database import AccessCard, AccessAttempt, db
import sqlite3
import logging
import os

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context():
    db.create_all()


@app.route('/', methods=['GET'])
def main_page():
    access_cards = AccessCard.query.all()
    access_attempts = AccessAttempt.query.all()

    return render_template('index.html', access_cards=access_cards, access_attempts=access_attempts)


@app.route('/enter', methods=['GET'])
def enter():
    card_id = str(request.args.get('card'))
    logging.debug(f"attempt enter: {card_id}")

    access_card: AccessCard = AccessCard.query.get(card_id)
    if access_card is None:
        failed_attempt = AccessAttempt(
            access_card=card_id, was_accepted=False, reason='unknown card id')
        db.session.add(failed_attempt)
        db.session.commit()
        return '0'

    logging.debug(
        f'is_locked: {access_card.is_locked}, in_room: {access_card.in_room}')

    if access_card.in_room:
        return '0'

    if access_card.is_locked:
        failed_attempt = AccessAttempt(
            access_card=access_card.id, was_accepted=False, reason='card locked')
        db.session.add(failed_attempt)
        db.session.commit()
        return '0'

    access_card.in_room = True
    db.session.add(access_card)
    success_attempt = AccessAttempt(
        access_card=access_card.id, was_accepted=True)
    db.session.add(success_attempt)
    db.session.commit()
    return '1'


@app.route('/exit', methods=['GET'])
def exit():
    card_id = str(request.args.get('card'))
    logging.debug(f'attempt exit: {card_id}')

    access_card: AccessCard = AccessCard.query.get(card_id)
    if access_card is None or access_card.in_room is False:
        return '0'

    access_card.in_room = False
    db.session.add(access_card)
    db.session.commit()
    return '1'


@app.route('/error', methods=['POST'])
def alarm():
    card_id = str(request.args.get('card'))
    logging.debug(f'alarm sounded: {card_id}')
    return '1'


@app.route('/api/access_card/<card_id>', methods=['PATCH'])
def lock_card(card_id):
    logging.debug(f'locking/unlocking access card: {card_id}')

    access_card: AccessCard = AccessCard.query.get_or_404(card_id)
    access_card.is_locked = False if access_card.is_locked else True
    db.session.add(access_card)
    db.session.commit()

    return "", 200


@app.route('/api/access_card/<card_id>', methods=['DELETE'])
def delete_card(card_id):
    logging.debug(f'removing access card: {card_id}')

    deleted_card = AccessCard.query.get_or_404(card_id)
    db.session.delete(deleted_card)
    db.session.commit()

    response = make_response("", 200)
    response.headers['HX-Refresh'] = 'true'
    return response


@app.route('/api/access_card/', methods=['POST'])
def add_card():
    logging.debug(f'adding access card')

    card_id = request.form.get('ac_code')
    is_locked = 1 if request.form.get('ac_locked') == 'on' else 0

    if AccessCard.query.get(card_id) is not None:
        return "", 400

    access_card = AccessCard(id=card_id, is_locked=is_locked, in_room=False)
    db.session.add(access_card)
    db.session.commit()

    response = make_response("", 201)
    response.headers['HX-Refresh'] = 'true'
    return response


if __name__ == '__main__':
    level = logging.DEBUG
    format = '[%(levelname)s] %(asctime)s - %(message)s'
    logging.basicConfig(level=level, format=format)
    app.run(debug=True, port=5000, host='0.0.0.0')
