from flask import Flask, request, render_template, make_response
import sqlite3
import logging

app = Flask(__name__)


@app.route('/', methods=["GET"])
def main_page():
    try:
        with sqlite3.connect('database.db') as connect:
            cursor = connect.cursor()
            cursor.execute('SELECT id, isLocked, inRoom FROM ACCESS_CARDS')
            access_cards = cursor.fetchall()

            cursor.execute(
                'SELECT id, accessCard, attemptTime, wasAccepted, reason FROM ACCESS_ATTEMPTS')
            access_attempts = cursor.fetchall()

    except sqlite3.OperationalError as e:
        logging.error(e)
        return render_template('error.html', error_msg=e)

    return render_template('index.html', access_cards=access_cards, access_attempts=access_attempts)


@app.route('/enter', methods=["GET"])
def enter():
    card_id = str(request.args.get('card'))
    logging.debug(f"attempt enter: {card_id}")

    try:
        with sqlite3.connect('database.db') as connect:
            cursor = connect.cursor()
            cursor.execute(
                'SELECT isLocked, inRoom FROM ACCESS_CARDS WHERE id = ?', (card_id,))
            row = cursor.fetchone()
            if row is None:
                cursor.execute(
                    'INSERT INTO ACCESS_ATTEMPTS (id, accessCard, attemptTime, wasAccepted, reason) VALUES (NULL, ?, CURRENT_TIMESTAMP, ?, \'unknown card id\')', (card_id, 0))
                return '0'

            (is_locked, in_room) = row
            logging.debug(f"is_locked: {is_locked}, in_room: {in_room}")
            if is_locked == 1:
                cursor.execute(
                    'INSERT INTO ACCESS_ATTEMPTS (id, accessCard, attemptTime, wasAccepted, reason) VALUES (NULL, ?, CURRENT_TIMESTAMP, ?, \'account locked\')', (card_id, 0))
                return '0'
            if in_room == 1:
                cursor.execute(
                    'INSERT INTO ACCESS_ATTEMPTS (id, accessCard, attemptTime, wasAccepted, reason) VALUES (NULL, ?, CURRENT_TIMESTAMP, ?, \'already in the room\')', (card_id, 0))
                return '0'

            cursor.execute(
                'INSERT INTO ACCESS_ATTEMPTS (id, accessCard, attemptTime, wasAccepted) VALUES (NULL, ?, CURRENT_TIMESTAMP, ?)', (card_id, 1))
            cursor.execute(
                'UPDATE ACCESS_CARDS SET inRoom = 1 WHERE id = ?', (card_id,))
            return '1'

    except sqlite3.OperationalError as e:
        logging.error(e)
        return '0'


@app.route('/exit', methods=["GET"])
def exit():
    card_id = str(request.args.get('card'))
    logging.debug(f"attempt exit: {card_id}")

    try:
        with sqlite3.connect('database.db') as connect:
            cursor = connect.cursor()
            cursor.execute(
                'SELECT inRoom FROM ACCESS_CARDS WHERE id = ?', (card_id,))
            row = cursor.fetchone()
            if row is None:
                return '0'

            in_room = row[0]
            logging.debug(f"in_room: {in_room}")
            if in_room == 0:
                return '0'

            cursor.execute(
                'UPDATE ACCESS_CARDS SET inRoom = 0 WHERE id = ?', (card_id,))
            return '1'

    except sqlite3.OperationalError as e:
        logging.error(e)
        return '0'


@app.route('/error', methods=["POST"])
def alarm():
    card_id = str(request.args.get('card'))
    logging.debug(f"alarm sounded: {card_id}")
    return '1'


@app.route('/api/access_card/<card_id>', methods=["PATCH"])
def lock_card(card_id):
    logging.debug(f"locking/unlocking access card: {card_id}")

    try:
        with sqlite3.connect('database.db') as connect:
            cursor = connect.cursor()
            cursor.execute(
                'SELECT isLocked FROM ACCESS_CARDS WHERE id = ?', (card_id,))
            is_locked = cursor.fetchone()[0]
            new_lock = 0 if is_locked == 1 else 1
            cursor.execute(
                'UPDATE ACCESS_CARDS SET isLocked = ? WHERE id = ?', (new_lock, card_id))

    except sqlite3.OperationalError as e:
        logging.error(e)
        return "", 400

    return "", 200


@app.route('/api/access_card/<card_id>', methods=["DELETE"])
def delete_card(card_id):
    logging.debug(f"removing access card: {card_id}")

    try:
        with sqlite3.connect('database.db') as connect:
            cursor = connect.cursor()
            cursor.execute(
                'DELETE FROM ACCESS_CARDS WHERE id = ?', (card_id,))

    except sqlite3.OperationalError as e:
        logging.error(e)
        return "", 400

    response = make_response("", 200)
    response.headers['HX-Refresh'] = 'true'
    return response


@app.route('/api/access_card/', methods=["POST"])
def add_card():
    logging.debug(f"adding access card")

    card_id = request.form.get('ac_code')
    is_locked = 1 if request.form.get('ac_locked') == 'on' else 0

    try:
        with sqlite3.connect('database.db') as connect:
            cursor = connect.cursor()
            cursor.execute(
                'SELECT 1 FROM ACCESS_CARDS WHERE id = ?', (card_id,))
            if len(cursor.fetchall()) > 0:
                return "", 400
            cursor.execute(
                'INSERT INTO ACCESS_CARDS (id, isLocked, inRoom) VALUES (?, ?, 0)', (card_id, is_locked))

    except sqlite3.OperationalError as e:
        logging.error(e)
        return "", 400

    response = make_response("", 201)
    response.headers['HX-Refresh'] = 'true'
    return response


if __name__ == '__main__':
    level = logging.DEBUG
    format = '[%(levelname)s] %(asctime)s - %(message)s'
    logging.basicConfig(level=level, format=format)
    app.run(debug=True, port=5000, host='0.0.0.0')
