from flask import Flask, request
import sqlite3
import logging

app = Flask(__name__)


@app.route('/', methods=["GET"])
def hello_world():
    return '<p>Hello World!</p>'


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


if __name__ == '__main__':
    level = logging.DEBUG
    format = '[%(levelname)s] %(asctime)s - %(message)s'
    logging.basicConfig(level=level, format=format)
    app.run(debug=True, port=5000, host='0.0.0.0')
