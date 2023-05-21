import sqlite3
import telebot
from telebot import types
from datetime import datetime
import random


id_seller = [6131680389, 361109226, 64862928]
TOKEN = '6066868239:AAF6j0ELFVyuWa1khfDMCDLxiBghUMMxGt4' #@selmot_bot
bot = telebot.TeleBot(TOKEN)

global db
global sql

db = sqlite3.connect('./TuttyFrutty.db', check_same_thread=False) #Соединение с Баззой Данных
sql = db.cursor() #Создание курсора

sql.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "name TEXT, price BIGINT, count BIGINT, discount BIGINT DEFAULT 0,"
            "final_price BIGINT GENERATED ALWAYS AS (Price * (100 - Discount) / 100) STORED)") #Таблица с продуктами

sql.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "user_name TEXT, user_id BIGINT, balance BIGINT)") #Таблица с пользователями

sql.execute("CREATE TABLE IF NOT EXISTS status (id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "user_id BIGINT, order_id INT, order_status INT)") #Таблица со статусом заказов

sql.execute("CREATE TABLE IF NOT EXISTS cart (id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "number_order, user_id BIGINT, id_product BIGINT, count BIGINT)") #Таблица с корзинами


@bot.message_handler(commands = ['start']) #Обработка команды /start
def register(message):
    """Регистрация пользователя. Если он уникальный, то его регестрирует и пишет "Здравствуйте!",
    если он был ранее зарегестрирован, то ему пишет 'С возвращением!'"""
    user_id = message.from_user.id
    sql.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    if sql.fetchone() is None:
        sql.execute(
            f"INSERT INTO users (user_name, user_id, balance) VALUES ('{message.from_user.username}', '{message.from_user.id}', {0})")
            #Вставить значения в таблицу. (Название ячеек) (Сами переменные)
        db.commit() #Сохранение изменения в БД
        bot.send_message(message.chat.id, f'Здравствуйте, {message.from_user.first_name}! Добро пожаловать в магазин.')
        buttons(message)
    else:
        bot.send_message(message.chat.id, f'C возвращением, {message.from_user.first_name}! Добро пожаловать в магазин.')
        buttons(message)


def otzovikto(message): #Добавление функции отзывов
    text_for_otzyv = message.text
    if message.text:
        markup_inline = types.InlineKeyboardMarkup(row_width = 2)
        item_accept = types.InlineKeyboardButton(text = 'Отправить продавцу', callback_data = 'publish_otz')
        item_decline = types.InlineKeyboardButton(text = 'Отклонить', callback_data = 'decline_otz')
        markup_inline.add(item_accept, item_decline)
        bot.send_message(message.chat.id, f"{text_for_otzyv}", reply_markup = markup_inline)


@bot.message_handler(commands = ['otzyv']) #Обработка команды /otzyv
def otzovik(message):
    msg = bot.send_message(message.chat.id, '📝 Напишите свой отзыв: ')
    bot.register_next_step_handler(msg, otzovikto)

@bot.message_handler(commands = ['menu']) #Обработка команды /menu
def buttons(message):
    markup_reply = types.ReplyKeyboardMarkup(resize_keyboard = True, row_width = 2) #Создание клавиатуры
    item_catalog = types.KeyboardButton(text = '📓 Каталог товаров')
    item_cart = types.KeyboardButton(text='🛒 Моя корзина')
    item_profile = types.KeyboardButton(text = '👨🏻‍💻 Мой профиль')
    markup_reply.add(item_catalog, item_cart, item_profile) #Добавление кнопок в клавиатуру
    bot.send_message(message.chat.id, 'Выберите опцию меню:',
        reply_markup = markup_reply
    )

def webAppKeyboard(): #создание клавиатуры с webapp кнопкой
   keyboard = types.ReplyKeyboardMarkup(row_width=1) #создаем клавиатуру
   webAppTest = types.WebAppInfo("https://melnikmarina.github.io/WebApp/") #создаем webappinfo - формат хранения url
   one_butt = types.KeyboardButton(text="Selmot_shop", web_app=webAppTest) #создаем кнопку типа webapp
   keyboard.add(one_butt) #добавляем кнопки в клавиатуру
   return keyboard #возвращаем клавиатуру

@bot.message_handler(content_types="web_app_data") #получаем отправленные данные
def answer(webAppMes):
   product_ids=webAppMes.web_app_data.data
   number_ids=[]
   random_number = random.randint(10000000, 99999999)
   for i in range (0, len(product_ids)): #Обработка полученных данных
       if (product_ids[i] != '"' and product_ids[i] != ',' and product_ids[i]!=' ' and product_ids[i]!=']'
               and product_ids[i]!='[' and product_ids[i]!='\n'):
           number_ids.append(int(product_ids[i])) #Добавление данных в Базу Данных
           sql.execute(f"INSERT INTO cart (user_id,number_order, id_product, count)"
                       f"VALUES"
                       f"({webAppMes.chat.id},{random_number},{int(product_ids[i])},1)"
                       )
           db.commit()


   order_products=[]
   for i in range(0, len(number_ids)):
       sql.execute(f"SELECT DISTINCT name FROM products WHERE id = {number_ids[i]}")
       result = sql.fetchone()
       order_products.append(result)
   str=''
   for i in order_products:
       for j in i:
           if(j!= ')' and j!='(' and j!=','):
               str+=j
       str+='\n'
   bot.send_message(webAppMes.chat.id, f'👕{str}')

   markup_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)  # Создание клавиатуры
   item_catalog = types.KeyboardButton(text='📓 Каталог товаров')
   item_profile = types.KeyboardButton(text='👨🏻‍💻 Мой профиль')
   item_cart = types.KeyboardButton(text='🛒 Моя корзина')
   markup_menu.add(item_catalog, item_profile, item_cart)  # Добавление кнопок в клавиатуру
   bot.send_message(webAppMes.chat.id, 'Возвращаемся в главное меню:',
                    reply_markup=markup_menu)


@bot.message_handler(content_types = ['text']) #Обработчик текста
def get_text(message):
    user_id = message.from_user.id
    if message.text == '📓 Каталог товаров':
        bot.send_message(message.chat.id, 'Наслаждайтесь покупками!',
                         reply_markup=webAppKeyboard())

    if message.text == '🛒 Моя корзина':
        first_name = message.from_user.first_name; user_id = message.from_user.id
        sql.execute(f"SELECT DISTINCT name FROM products JOIN cart ON products.id = cart.id_product WHERE cart.user_id = '{user_id}'")

        result = sql.fetchall()
        str = ""; count = 1
        markup_menu = types.InlineKeyboardMarkup()  # Создание клавиатуры
        confirm = types.InlineKeyboardButton(text='Совершить покупку ✅', callback_data='confirm_cart')
        decline = types.InlineKeyboardButton(text='Отменить заказ ❌', callback_data='cancel_cart')
        markup_menu.add(confirm, decline)
        if result:
            for i in result:
                item = i[0]
                str += f'Товар #{count} - "{item}" 👕\n'
                count += 1

            bot.send_message(message.chat.id, f'{first_name}, ваша корзина:\n'
                                              f'\n{str}', reply_markup=markup_menu)
        else:
            bot.send_message(message.chat.id, f'{first_name}, ваша корзина пуста.')

    elif message.text == '👨🏻‍💻 Мой профиль':
        markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True)
        сheck_balance = types.KeyboardButton(text = '💵 Проверить баланс')
        check_status = types.KeyboardButton(text='💡 Проверить статус заказа')
        go_back = types.KeyboardButton(text='❌ Отменить заказ')
        delete = types.KeyboardButton(text='⏪ Вернуться в меню')
        seller_menu = types.KeyboardButton(text='💼 Зайти в меню продавца')
        markup_reply.add(сheck_balance, check_status, go_back, delete,seller_menu)
        bot.send_message(message.chat.id, 'Личный кабинет:',
                         reply_markup=markup_reply
                         )

    elif message.text == '💵 Проверить баланс':
        user_id = message.from_user.id
        sql.execute(f"SELECT balance FROM users WHERE user_id = {user_id}")
        result = sql.fetchone()
        if result: #Проверяем есть ли запись в БД
            balance = result[0]
            bot.send_message(message.chat.id, f'Ваш баланс: {balance} 💳')
        else: #Если её нет, тогда выполняем другое условие
            bot.send_message(message.chat.id, f'Пользователь #{message.from_user.id} не найден')

    elif message.text == '💡 Проверить статус заказа':
        user_id = message.from_user.id
        now = datetime.now()
        datetime_str = now.strftime("%d.%m.%Y %H:%M")
        sql.execute(f"SELECT id, user_id, order_status, order_id FROM status WHERE user_id = {user_id}") #Выбираем, что достаем. Выбираем откуда. Выбираем фильтр для отбора
        results = sql.fetchall() #fetchall() записываешь все данные, которые собрал по запросу в БД
        order_list = ""
        if results:
            for result in results:
                id, user_id, order_status, order_id = result
                if order_status == 0:
                    order_list += f'\nЗаказ #{order_id} успешно оформлен 📝 Ожидайте подтверждения! \n'
                if order_status == 1:
                    order_list += f'\nЗаказ #{order_id} был подтвержден продавцом ✅ Ожидайте отправления! \n'
                if order_status == 2:
                    order_list += f'\nЗаказ #{order_id} был отправлен продавцом 📦 При получении вы можете оставить отзыв - /otzyv\n'
            bot.send_message(message.chat.id, f'{message.from_user.first_name}, список ваших актуальных заказов на {datetime_str}: \n'
                                              f'\n{order_list}')
        else:
            bot.send_message(message.chat.id, f'{message.from_user.first_name}, у вас на данный момент нет активных заказов 😦')

    elif message.text == '❌ Отменить заказ':
        user_id = message.from_user.id
        sql.execute(f"SELECT id, user_id, order_status FROM status WHERE user_id = {user_id}")
        result = sql.fetchone()
        if result is not None:
            id, user_id, order_status = result
            markup = types.InlineKeyboardMarkup() #Кнопки в самом сообщении
            confirm = types.InlineKeyboardButton(text="Да ✔", callback_data=f"confirm_delete") #callback_data для работы в callback_handler
            cancel = types.InlineKeyboardButton(text="Нет ✖", callback_data=f"cancel_delete")
            markup.add(confirm, cancel)
            bot.send_message(message.chat.id,
                             f'Вы действительно хотите удалить свои заказы?',
                             reply_markup=markup)
            return id
        else:
            bot.send_message(message.chat.id,
                             f'{message.from_user.first_name}, у вас на данный момент нет активных заказов 😦')

    elif message.text == '⏪ Вернуться в меню':
        markup_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)  # Создание клавиатуры
        item_catalog = types.KeyboardButton(text='📓 Каталог товаров')
        item_profile = types.KeyboardButton(text='👨🏻‍💻 Мой профиль')
        item_cart = types.KeyboardButton(text='🛒 Моя корзина')
        markup_menu.add(item_catalog, item_profile,item_cart)  # Добавление кнопок в клавиатуру
        bot.send_message(message.chat.id, 'Возвращаемся в главное меню:',
                         reply_markup = markup_menu)


    elif message.text == '💼 Зайти в меню продавца': #Меню продавца-администратора
        user_id = message.from_user.id
        if user_id in id_seller:
            markup_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)  # Создание клавиатуры
            send = types.KeyboardButton(text='📢 Рассылка покупателям')
            change_balance = types.KeyboardButton(text='💳 Изменить баланс')
            work_products = types.KeyboardButton(text='📁 Работа над товарами')
            list_products = types.KeyboardButton(text='📓 Список товаров')
            back = types.KeyboardButton(text='⏪ Вернуться в меню')
            markup_menu.add(send, change_balance, work_products, list_products, back)  # Добавление кнопок в клавиатуру
            bot.send_message(message.chat.id, f'Меню продавца.',
                             reply_markup= markup_menu) #Богдан
        else:
            bot.send_message(message.chat.id, f'В доступе отказано.')

    elif message.text == '📢 Рассылка покупателям':
        msg = bot.send_message(message.chat.id, 'Напишите текст для рассылки')
        bot.register_next_step_handler(msg, distribution_go)

    elif message.text == '💳 Изменить баланс':
        msg = bot.send_message(message.chat.id, 'Введите имя пользователя (Его тег): ')
        bot.register_next_step_handler(msg, balance_change)

    elif message.text == '📓 Список товаров':
        sql.execute(f'SELECT * FROM products')
        products_list = sql.fetchall()
        string = ""
        for product in products_list:
            id, name, price, count, discount, final_price = product
            string += f"\nID: {id}, Название: {name}, Количество: {count}, Скидка: {discount}, Цена: {final_price}\n"
        bot.send_message(message.chat.id, f'Список товаров, доступных на продажу: \n{string}')

    elif message.text == '📁 Работа над товарами':
        sql.execute(f'SELECT * FROM products')
        products_list = sql.fetchall()
        string = ""
        for product in products_list:
            id, name, price, count, discount, final_price = product
            string += f"\nID: {id}, Название: {name}, Количество: {count}, Скидка: {discount}, Цена: {final_price}\n"
        bot.send_message(message.chat.id, f'Список товаров для изменения: \n{string}')

        markup_menu = types.InlineKeyboardMarkup()  # Создание клавиатуры
        one = types.InlineKeyboardButton(text='1', callback_data='1')
        two = types.InlineKeyboardButton(text='2', callback_data='2')
        three = types.InlineKeyboardButton(text='3', callback_data='3')
        four = types.InlineKeyboardButton(text='4', callback_data='4')
        five = types.InlineKeyboardButton(text='5', callback_data='5')
        six = types.InlineKeyboardButton(text='6', callback_data='6')
        seven = types.InlineKeyboardButton(text='7', callback_data='7')
        eight = types.InlineKeyboardButton(text='8', callback_data='8')
        nine = types.InlineKeyboardButton(text='9', callback_data='9')
        markup_menu.add(one,two,three,four,five,six,seven,eight,nine)

        bot.send_message(message.chat.id, f'Выберите ID товара',
                         reply_markup=markup_menu)

def distribution_go(message): #Обработка сообщения для рассылки
    text_for_distribution = message.text #Получение текста от продавца
    if message.text: #Если текст есть
        markup_inline = types.InlineKeyboardMarkup(row_width = 2)
        accept = types.InlineKeyboardButton(text = 'Отправить', callback_data = 'publish')
        decline = types.InlineKeyboardButton(text = 'Отклонить', callback_data = 'decline')
        markup_inline.add(accept, decline)
        bot.send_message(message.chat.id, f"{text_for_distribution}", reply_markup = markup_inline)

def balance_change(message): #Запрашиваем ID и сумму на которую нужно увеличить/уменьшить баланс пользователю
    user_name = message.text #Получение текста от продавца
    sql.execute(f'SELECT user_id FROM users WHERE user_name = "{user_name}"')
    result = sql.fetchone()
    if message.text: #Если текст есть
        if result: #Проверяем есть ли пользователь с таким именем
            user_id = result[0]
        else:
            bot.send_message(message.chat.id, f'Такого пользователя нет')
    bot.send_message(message.chat.id, 'Введите сумму, на которую вы хотите увеличить баланс:')
    bot.register_next_step_handler(message, set_balance, user_id)

def set_balance(message, user_id): #Функция установки баланса
    amount = int(message.text)
    sql.execute(f"UPDATE users SET balance = balance + {amount} where user_id = {user_id}")
    db.commit()
    bot.send_message(message.chat.id, 'Баланс успешно обновлен!')

def change_value(message, call_data, id_product): #Изменения значения для выбранного ID продукта
    new_amount = message.text
    start = call_data
    if start.startswith('price_change'): #Если поменять нужно цену
        action, id_product = start.split(';') #Достаём ID продукта
        sql.execute(f"UPDATE products SET price = {new_amount} where id = {id_product}")
        db.commit()
        bot.send_message(message.chat.id, f'Значение было успешно обновлено. Новый баланс: {new_amount}!')

    if start.startswith('count_change'): #Если поменять нужно количество
        action, id_product = start.split(';') #Достаём ID продукта
        sql.execute(f"UPDATE products SET count = {new_amount} where id = {id_product}")
        db.commit()
        bot.send_message(message.chat.id, f'Значение было успешно обновлено. Новое количество: {new_amount}!')

    if start.startswith('discount_change'): #Если поменять нужно скидку. Отображается в итоговой цене корзины
        action, id_product = start.split(';') #Достаём ID продукта
        sql.execute(f"UPDATE products SET discount = {new_amount} where id = {id_product}")
        db.commit()
        bot.send_message(message.chat.id, f'Значение было успешно обновлено. Скидка: {new_amount}!')

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    id_product = None
    if call.data == "confirm_delete": #Подтверждение удаление заказа
        user_id = call.message.chat.id
        sql.execute(f"DELETE FROM status WHERE user_id = {user_id}")
        db.commit()
        bot.send_message(call.message.chat.id, f'Ваш заказ успешно удален!')

    elif call.data == "cancel_delete": #Отмена удаления заказа
        bot.send_message(call.message.chat.id, f'Вы отменили удаление заказа.')

    elif call.data == "confirm_cart":
        '''Подтверждение корзины покупателем. Дальше идёт проверка хватит ли у него средств для осуществления покупки.
        После чего, если средств достаточно, бот спрашивает адрес и происходит подтверждение заказа. В этот момент
        удаляется корзина и забираются продукты из "products" и оформляется новый заказ в "status". 
        Одновременно продавцы получают оповещение что пользователь совершил покупку и содержание его заказа.
        В случае, если денег нет, тогда покупатель не сможет оформить покупку и его корзина обнуляется.'''
        user_id = call.message.chat.id
        sql.execute(f"SELECT balance FROM users WHERE user_id = {user_id}")
        balance = sql.fetchone()[0]
        final_sum = 0

        def change_balance(): #Изменение баланса пользователя после совершения покупки
            sql.execute(f"UPDATE users SET balance = balance - {final_sum} where user_id = {user_id}")
            db.commit()

        sql.execute(f"SELECT id_product, count FROM cart where user_id = {user_id}") #Проверка стоимости всей корзины
        rows = sql.fetchall()
        for row in rows:
            id_product, count = row
            sql.execute(f"SELECT final_price FROM products WHERE id = {id_product}")
            price = sql.fetchone()[0]
            final_sum += price*count

        def get_cart(message):  # Оформление карзины с получением адреса от пользователя
            address = message.text
            user_id = message.chat.id;
            user_name = message.chat.username
            sql.execute(f"SELECT number_order, id_product, count FROM cart where user_id = {user_id}")
            order_list = ""
            rows = sql.fetchall()
            order_id = rows[0][0]
            for row in rows:
                number_order, id_product, count = row
                sql.execute(f"UPDATE products SET count = count - {count} where id = {id_product}")
                db.commit()
                sql.execute(f"SELECT name FROM PRODUCTS WHERE id = {id_product}")
                name_product = sql.fetchone()
                order_list += f'Товар: "{name_product[0]}", количество: {count}.\n'
            sql.execute(f"INSERT INTO status (user_id, order_id, order_status) VALUES ('{user_id}', '{order_id}', {0})")
            db.commit()
            sql.execute(f"DELETE FROM cart WHERE user_id = {user_id}")
            db.commit()
            change_balance()

            markup_inline = types.InlineKeyboardMarkup(row_width=2)
            accept = types.InlineKeyboardButton(text='Подтвердить', callback_data=f'push_order;{order_id}')
            decline = types.InlineKeyboardButton(text='Отклонить', callback_data=f'decline_order;{order_id}')
            markup_inline.add(accept, decline)

            for id in id_seller:
                bot.send_message(id,
                                 f'Пользователь @{user_name} оформил заказ #{order_id} 📧\n \n{order_list}\n'
                                 f'Адрес покупателя: {address} 🚛\nИтоговая сумма заказа: {final_sum} 💳',
                                 reply_markup=markup_inline)

            bot.send_message(message.chat.id,f'Вы успешно оформили заказ #{order_id} 📧\n \n{order_list}\n'
                                 f'Адрес получения: {address} 🚛\nИтоговая сумма заказа: {final_sum} 💳')

        if final_sum <= balance: #Проверка хватает ли у пользователя средств для совершения покупки
            address_new = bot.send_message(call.message.chat.id, f'Введите адрес доставки (город, улица, дом, квартира):')
            bot.register_next_step_handler(address_new, get_cart)
        else:
            user_id = call.message.chat.id
            bot.send_message(call.message.chat.id, f'На вашем счету недостаточно средств. Не хватает {final_sum - balance}')


    elif call.data == "cancel_cart": #Если пользователь отменяет корзину
        user_id = call.message.chat.id
        sql.execute(f"DELETE FROM cart WHERE user_id = {user_id}")
        db.commit()
        bot.send_message(call.message.chat.id, f'Ваша корзина удалена.')

    elif call.data == "publish_otz": #Опубликовать отзыв
        user_id = call.message.chat.id
        sql.execute(f"DELETE FROM status WHERE user_id = {user_id} and order_status = {2}")
        db.commit()
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                 text='✅ Отзыв опубликован!')
        for id in id_seller:
            bot.send_message(id, f'Опубликован новый отзыв: {call.message.text} 💬')

    elif call.data == "decline_otz": #Отклонить отзыв
        bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = '❌ Отзыв отклонён')

    elif call.data == "publish": #Если продавец выбрал отправить
        sql.execute(f"SELECT user_id FROM users")  # Запрос в БД для получение всех id
        list = sql.fetchall()  # превращение в список
        for id in list:
            id_to_say = id[0]  # трансформация для работы с ID
            if id_to_say in id_seller:  # если id - продавец, он не получит сообщение
                pass
            else:
                bot.send_message(id_to_say,f'{call.message.text}')

    elif call.data == "decline": #Если продавец отклонил
        bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = '❌ Рассылка отклонена')

    elif call.data in ['1', '2', '3', '4', '5', '6', '7', '8', '9',]: #Проверяем для какого ID продукта, что можно изменить
        id_product = call.data
        markup_menu = types.InlineKeyboardMarkup()  # Создание клавиатуры
        price_change = types.InlineKeyboardButton(text='Цена продукта', callback_data=f'price_change;{id_product}')
        count_change = types.InlineKeyboardButton(text='Количество', callback_data=f'count_change;{id_product}')
        discount_change = types.InlineKeyboardButton(text='Скидка', callback_data=f'discount_change;{id_product}')
        markup_menu.add(price_change, count_change, discount_change)
        sql.execute(f"SELECT name FROM products WHERE id = {id_product}")
        name_product = sql.fetchone()
        bot.send_message(call.message.chat.id, f'Вы выбрали товар: "{name_product[0]}". Что вы хотите изменить?',
                         reply_markup=markup_menu)

    elif call.data.startswith('price_change'): #Если callback data начинается на ..., тогда выполняется это условие
        action, id_product = call.data.split(';') #Достаём ID продукта для дальнейшей работы с неё
        msg = bot.send_message(call.message.chat.id, 'Введите новое значение: ')
        bot.register_next_step_handler(msg, change_value, call.data, id_product)

    elif call.data.startswith('count_change'): #Если callback data начинается на ..., тогда выполняется это условие
        action, id_product = call.data.split(';') #Достаём ID продукта для дальнейшей работы с неё
        msg = bot.send_message(call.message.chat.id, 'Введите новое значение: ')
        bot.register_next_step_handler(msg, change_value, call.data, id_product)

    elif call.data.startswith('discount_change'): #Если callback data начинается на ..., тогда выполняется это условие
        action, id_product = call.data.split(';') #Достаём ID продукта для дальнейшей работы с неё
        msg = bot.send_message(call.message.chat.id, 'Введите новое значение: ')
        bot.register_next_step_handler(msg, change_value, call.data, id_product)

    elif call.data.startswith('push_order'): #Если callback data начинается на ..., тогда выполняется это условие
        user_id = call.message.chat.id
        action, id_order = call.data.split(';') #Достаём ID продукта для дальнейшей работы с неё
        sql.execute(f'SELECT user_id FROM status WHERE order_id = {id_order}')
        id_send = sql.fetchone() #Записываем ID на который нужно отправить сообщение
        sql.execute(f'SELECT user_name FROM users WHERE user_id = {user_id}')
        seller = sql.fetchone() #Записываем ID продавца
        name_seller = seller[0]
        sql.execute(f'UPDATE status SET order_status = 2 WHERE order_id = {id_order}')
        db.commit() #Обновляем статус заказа на 2
        id_to_send = id_send[0]
        random_number = random.randint(10000,99999) #Рандомно генерируем трек-номер

        bot.send_message(id_to_send, f'Ваш заказ был подтвержден продавцом @{name_seller}!\n'
                                     f'Трек-номер вашего заказа: #{random_number}\n'
                                     f'При получении вы можете оставить отзыв - /otzyv')

        bot.send_message(call.message.chat.id, f'Вы успешно подтвердили заказ!\n'
                                               f'Трек-номер заказа: #{random_number}')



    elif call.data.startswith('decline_order'): #Отклонение заказа продавцом
        action, id_order = call.data.split(';')
        sql.execute(f'SELECT user_id FROM status WHERE order_id = {id_order}')
        id_send = sql.fetchone()
        id_to_send = id_send[0]
        sql.execute(f'DELETE FROM status WHERE order_id = {id_order}')
        db.commit()
        bot.send_message(id_to_send, f'Ваш заказ удален.')
        bot.send_message(call.message.chat.id, 'Вы успешно отменили заказ!')


bot.polling(none_stop=True) #Запуск бота без остановки
