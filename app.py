from flask import Flask, request, jsonify
from flask_cors import CORS

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr
import sqlite3
from dotenv import load_dotenv
import os
import sys

# Установка кодировки по умолчанию на UTF-8
sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')

# Загрузка переменных окружения
load_dotenv()

app = Flask("Ilgar")
CORS(app, resources={r"/*": {"origins": "*"}})

def init_db():
    conn = sqlite3.connect('reviews.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        branch TEXT NOT NULL,
        shisha_quality INTEGER NOT NULL,
        staff_quality INTEGER NOT NULL,
        venue_quality INTEGER NOT NULL,
        feedback TEXT,
        visit_date DATE NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()

init_db()

def send_email(staff, shisha_quality, staff_quality, venue_quality, feedback, visit_date):
    to = 'ilgar_guliyev2003@mail.ru'
    subject = 'Новый отзыв о персонале'
    body = f"""Филиал: {staff}
Качество кальяна: {shisha_quality}
Уровень обслуживания: {staff_quality}
Состояние игровых контроллеров: {venue_quality}
Отзыв: {feedback}
Дата посещения: {visit_date}"""

    print(f"Email Body: {body}")  # Добавляем печать тела письма

    msg = MIMEMultipart()
    msg['From'] = formataddr((str(Header('ilgar_guliyev2003@mail.ru', 'utf-8')), 'ilgar_guliyev2003@mail.ru'))
    msg['To'] = formataddr((str(Header(to, 'utf-8')), to))
    msg['Subject'] = Header(subject, 'utf-8')
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    print("Подготовка к отправке email...")
    email_password = os.getenv('EMAIL_PASSWORD')
    if email_password is None:
        print("Ошибка: Переменная окружения EMAIL_PASSWORD не установлена")
        return 'Ошибка: Переменная окружения EMAIL_PASSWORD не установлена'

    try:
        server = smtplib.SMTP_SSL('smtp.mail.ru', 587)
        print("Подготовка к логину...")
        server.login('ilgar_guliyev2003@mail.ru', email_password)
        print("Логин успешен")
        print("Отправка сообщения...")
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        print("Сообщение отправлено")
        server.quit()
        print("Сессия SMTP завершена")

        return 'Отзыв успешно отправлен!'

    except smtplib.SMTPAuthenticationError:
        print("Ошибка аутентификации SMTP. Пожалуйста, проверьте логин и пароль.")
        return 'Ошибка аутентификации. Пожалуйста, проверьте логин и пароль.'
    except smtplib.SMTPException as e:
        print(f"Ошибка SMTP: {e}")
        return f'Произошла ошибка при отправке email: {e}'
    except Exception as e:
        print(f"Общая ошибка: {e}")
        return f'Произошла ошибка: {e}'

@app.route('/send_review', methods=['POST'])
def send_review():
    conn = sqlite3.connect('reviews.db')
    cursor = conn.cursor()

    try:
        # Валидация данных
        staff = request.form.get('staff', '').strip()
        if not staff:
            return jsonify({'error': 'Не указан филиал'}), 400

        shisha_quality = int(request.form.get('shisha-quality', 0))
        staff_quality = int(request.form.get('staff-quality', 0))
        venue_quality = int(request.form.get('venue-quality', 0))
        feedback = request.form.get('feedback', '').strip()
        visit_date = request.form.get('visit-date', '').strip()

        if not visit_date:
            return jsonify({'error': 'Не указана дата посещения'}), 400

        # Сохранение отзыва
        cursor.execute('''
        INSERT INTO reviews (branch, shisha_quality, staff_quality, venue_quality, feedback, visit_date)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (staff, shisha_quality, staff_quality, venue_quality, feedback, visit_date))

        conn.commit()

        # Отправка email
        result = send_email(staff, shisha_quality, staff_quality, venue_quality, feedback, visit_date)
        if result == 'Отзыв успешно отправлен!':
            return jsonify({'message': result}), 200
        else:
            return jsonify({'error': result}), 500

    except Exception as e:
        print(f"Общая ошибка: {e}")
        return jsonify({'error': f'Произошла ошибка: {e}'}), 500

    finally:
        conn.close()

from waitress import serve

if __name__ == '__main__':
    print("Запуск сервера на порту 80...")
    serve(app, host='0.0.0.0', port=80)




