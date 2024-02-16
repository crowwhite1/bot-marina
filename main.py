import logging
import sqlite3
import asyncio
import sys
import pandas as pd
from aiogram import Bot, Dispatcher, Router, types
from aiogram.utils.keyboard import *
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

with open(r'token.txt') as q:
    API_TOKEN = q.readline().strip()
dp = Dispatcher()

db = sqlite3.connect('database.db')
cursor = db.cursor()

cursor.execute("DROP TABLE IF EXISTS subject")
db.commit()

cursor.execute('''
CREATE TABLE IF NOT EXISTS subject(
id Integer PRiMARY KEY,
name TEXT
)
''')
db.commit()
cursor.execute('''
CREATE TABLE IF NOT EXISTS user (
id INTEGER PRIMARY KEY,
subjects TEXT,
subjects_mark TEXT
)
''')
db.commit()

cursor.execute('''
CREATE TABLE IF NOT EXISTS university (
id INTEGER PRIMARY KEY,
name_univer TEXT,
name_napr TEXT,
platno TEXT,
subjects TEXT,
subjects_mark TEXT,
minimum_last INTEGER,
link TEXT
)
''')
db.commit()
keyboard_subjects = []
subject_buttons = InlineKeyboardBuilder()
with open(r'subjects.txt', encoding='UTF-8') as f:
    subjects_arr = list(map(str.strip, f.readlines()))
    for i in range(len(subjects_arr)):
        cursor.execute('''INSERT INTO subject(id,name) values (?,?)''', (i, subjects_arr[i].strip()))
        keyboard_subjects.append(InlineKeyboardButton(
            text=subjects_arr[i].strip(),
            callback_data=f'set_subj {i}'
        ))
    keyboard_subjects.append(
        InlineKeyboardButton(
            text='Готово',
            callback_data='ready_set_subj'
        )
    )
    subject_buttons.row(*keyboard_subjects, width=1)
    db.commit()


def get_user_from_message(message) -> int:
    """
    Получение id юзера при получении от него сообщения
    :param message:Message
    :return id:int
    """
    return message.from_user.id


def get_user_from_db(id: int):
    """
    Получение юзера из базы данных по id
    :type id: int
    :param id:int
    :return:
    """
    cursor.execute(f"SELECT * FROM user WHERE id == {id}")
    return cursor.fetchone()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Метод при команде старт
    :param message:
    """
    user_id = get_user_from_message(message)
    user = get_user_from_db(user_id)
    if user is None:
        await message.reply(
            "Привет! Этот бот создан, чтобы помочь найти тебе вуз для поступления." +
            "\n" +
            "Выбери предметы, которые планируешь сдавать",
            reply_markup=subject_buttons.as_markup())
        try:
            cursor.execute(f'''INSERT INTO user(id) values ({user_id})''')
            db.commit()
        except:
            pass
    else:
        await message.reply(
            "Привет! Давай начнём регистрацию заново!" +
            "\n" +
            "Выбери предметы, которые планируешь сдавать: ",
            reply_markup=subject_buttons.as_markup())
        try:
            cursor.execute(f'''UPDATE user SET subjects = ?, subjects_mark = ? WHERE id = ?''', (None, None, user_id))
            db.commit()
        except:
            pass


async def set_subject(callback_query: CallbackQuery):
    update_subjects_query = '''UPDATE user SET subjects = ? WHERE id = ?'''
    user_id = get_user_from_message(callback_query)
    user = get_user_from_db(user_id)
    users_subj = user[-2]
    selected_subj = int(callback_query.data.split()[1])
    if users_subj is None:
        users_subj = [selected_subj]
        cursor.execute(update_subjects_query, (' '.join(list(map(str, users_subj))), user_id))
        markup = await add_subj(callback_query, selected_subj)
        await callback_query.message.edit_reply_markup(
            inline_message_id=callback_query.inline_message_id,
            reply_markup=markup.as_markup()
        )
        db.commit()
    else:
        users_subj = list(map(int, users_subj.split()))
        if selected_subj not in users_subj:
            users_subj.append(selected_subj)
            cursor.execute(update_subjects_query, (' '.join(list(map(str, users_subj))), user_id))
            markup = await add_subj(callback_query, selected_subj)
            await callback_query.message.edit_reply_markup(
                inline_message_id=callback_query.inline_message_id,
                reply_markup=markup.as_markup()
            )
            db.commit()
        else:
            users_subj.remove(selected_subj)
            cursor.execute(update_subjects_query, (' '.join(list(map(str, users_subj))), user_id))
            markup = await remove_subj(callback_query, selected_subj)
            await callback_query.message.edit_reply_markup(
                inline_message_id=callback_query.inline_message_id,
                reply_markup=markup.as_markup()
            )
            db.commit()


async def add_subj(callback_query, selected_subj):
    new_keyboard = callback_query.message.reply_markup.inline_keyboard.copy()
    temp = []
    for e in new_keyboard:
        temp.append(InlineKeyboardButton(
            text=e[0].text,
            callback_data=e[0].callback_data
        ))
    temp[int(selected_subj)] = InlineKeyboardButton(
        text=temp[int(selected_subj)].text + ' ✅',
        callback_data=callback_query.data
    )
    markup = InlineKeyboardBuilder()
    markup = markup.row(*temp, width=1)
    return markup


async def remove_subj(callback_query, selected_subj):
    new_keyboard = callback_query.message.reply_markup.inline_keyboard.copy()
    temp = []
    for e in new_keyboard:
        temp.append(InlineKeyboardButton(
            text=e[0].text,
            callback_data=e[0].callback_data
        ))
    temp[int(selected_subj)] = InlineKeyboardButton(
        text=temp[int(selected_subj)].text.replace(' ✅', ''),
        callback_data=callback_query.data
    )
    markup = InlineKeyboardBuilder()
    markup = markup.row(*temp, width=1)
    return markup


async def set_mark(callback_query: CallbackQuery):
    update_subjects_mark_query = '''UPDATE user SET subjects_mark = ? WHERE id = ?'''
    user_id = get_user_from_message(callback_query)
    user = get_user_from_db(user_id)
    user_subj = user[-2]
    user_mark = user[-1]
    buttons = []
    for i in range(1, 11):
        buttons.append(
            InlineKeyboardButton(
                text=str(10 * i),
                callback_data=f'mark_{i}'
            )
        )
    markup = InlineKeyboardBuilder()
    markup = markup.row(*buttons, width=2)
    if callback_query.data == 'ready_set_subj':
        if user_subj is None or user_subj == '' or user_subj == ' ':
            text = 'Вы не выбрали ни одного предмета, используйте команду /change для смены выбранных предметов'
            await callback_query.message.edit_text(
                text=text,
                inline_message_id=callback_query.inline_message_id,
                reply_markup=None
            )
        else:
            user_subj = list(map(int, user_subj.split()))
            subj = user_subj[0]
            text = f'Выберите максимальный полученный/ожидаемый балл на экзамене по предмету: {subjects_arr[subj]}'
            await callback_query.message.edit_text(
                text=text,
                inline_message_id=callback_query.inline_message_id,
                reply_markup=markup.as_markup()
            )
    else:
        i = int(callback_query.data.split('_')[1])
        user_mark = list(map(int, user_mark.split())) if user_mark is not None else []
        user_mark.append(i)
        cursor.execute(update_subjects_mark_query, (' '.join(list(map(str, user_mark))), user_id))
        db.commit()
        user_subj = list(map(int, user_subj.split()))
        if len(user_subj) == len(user_mark):
            await callback_query.message.edit_text(
                text='Поздравляем с успешной регистрацией, используйте команду /get, чтобы получить список ВУЗов ',
                inline_message_id=callback_query.inline_message_id,
                reply_markup=None
            )
        else:
            if user_subj is None or user_subj == []:
                text = 'Вы не выбрали ни одного предмета, используйте команду /change для смены выбранных предметов'
                await callback_query.message.edit_text(
                    text=text,
                    inline_message_id=callback_query.inline_message_id,
                    reply_markup=None
                )
            else:
                subj = user_subj[len(user_mark):][0]
                text = f'Выберите максимальный полученный/ожидаемый балл на экзамене по предмету: {subjects_arr[subj]}'
                await callback_query.message.edit_text(
                    text=text,
                    inline_message_id=callback_query.inline_message_id,
                    reply_markup=markup.as_markup()
                )


@dp.message(Command("get"))
async def get_universities(message: Message):
    user_id = get_user_from_message(message)
    user = get_user_from_db(user_id)
    user_subj = user[-2]
    user_mark = user[-1]
    query = 'SELECT * from university'
    if user_mark is None or user_subj is None:
        await message.reply(
            text='Пожалуйста пройдите регистрацию заново, используя команду /start'
        )
    else:
        flag_to_ret = True
        user_subj = list(map(int, user_subj.split()))
        user_mark = list(map(int, user_mark.split()))
        univers = cursor.execute(query).fetchall()
        text = 'Вот список подходящих университетов: ' + '\n'
        for univer in univers:
            id = univer[0]
            name_univer = univer[1]
            name_napr = univer[2]
            platno = univer[3]
            subjects = univer[4]
            subj_list = list(map(int, subjects.split()))
            subjects_mark = univer[5]
            minimum_last = univer[6]
            link = univer[7]
            if set(subj_list).issubset(set(user_subj)):
                flag = True
                summ = 0
                for idx in subj_list:
                    if idx not in user_subj and user_mark[user_subj.index(idx)] < subjects_mark[subj_list.index(idx)]:
                        flag = False
                        break
                    else:
                        summ += 10 * user_mark[user_subj.index(idx)]
                if summ + 10 < minimum_last:
                    flag = False
                if flag:
                    text += f'ВУЗ: {name_univer}' + '\n' + f'Направление: {name_napr}' + '\n'
                    text += f'Платно: {'Да' if platno == 'True' else 'Нет'}' + '\n'
                    text += f'Ссылка: {link}' + '\n' + '---------' + '\n'
                    flag_to_ret = False
        if flag_to_ret:
            await message.reply(text='К сожалению, для тебя нет подходящих ВУЗов')
        else:
            await message.reply(text=text)


@dp.callback_query()
async def handle_query(callback_query: CallbackQuery):
    if callback_query.data:
        if callback_query.data.startswith("set_subj"):
            await set_subject(callback_query)
        elif callback_query.data == 'ready_set_subj' or callback_query.data.startswith('mark_'):
            await set_mark(callback_query)


async def main() -> None:
    bot = Bot(API_TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
