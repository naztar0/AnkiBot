#!/usr/bin/env python
import constants as c
import text_to_speech as tts
import telegraph_publisher as tp
import json
import random

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage


bot = Bot(c.token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Start_learning(StatesGroup): deck = State()
class Create_deck(StatesGroup): deck = State()
class Delete_deck(StatesGroup): deck = State()


class Editing(StatesGroup):
    deck = State()
    words = State()


status_random_weights = {1: 50, 2: 5, 3: 2, 4: 1}
side_list = ('front', 'back')
buttons = ["⭐ Start learning", "🆕 Create deck", "📝 Edit deck", "❌ Delete deck"]
back_button = "⬅ Back"


def keyboard():
    key = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key.add(buttons[0], buttons[1])
    key.add(buttons[2], buttons[3])
    return key


def back_keyboard():
    key = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key.add(back_button)
    return key


async def cancel(message, state):
    if message.text == back_button:
        await state.finish()
        await message.answer("Canceled", reply_markup=keyboard())
        return True
    return False


async def choose_deck(message: types.Message):
    try:
        with open(f'json_words/{message.chat.id}.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not data:
            raise FileNotFoundError
    except FileNotFoundError:
        await message.answer("You don't have a single deck. Please, create at least one")
        return None

    titles = []
    for title in data:
        titles.append(title)
    return titles


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Hello! Choose option from buttons below", reply_markup=keyboard())


@dp.message_handler(content_types=['text'])
async def message_handler(message: types.Message):
    if message.text == buttons[0]:
        await leaning_mode(message)
    elif message.text == buttons[1]:
        await message.answer("Send me a list of words. Please use this format:\n\n"
                             "Deck title\nword1 front side - word1 back side\nword2 front side - word2 back side",
                             reply_markup=back_keyboard())
        await Create_deck.deck.set()
    elif message.text == buttons[2]:
        await editing_mode(message)
    elif message.text == buttons[3]:
        await deleting_mode(message)
    elif message.text == back_button:
        await message.answer("Canceled", reply_markup=keyboard())


@dp.message_handler(content_types=['text'], state=Create_deck.deck)
async def create_deck(message: types.Message, state: FSMContext):
    if await cancel(message, state):
        return

    text_sep = str(message.text).split('\n')
    if len(text_sep) < 2:
        await message.reply("No words themselves, please try again")
        return
    title = text_sep[0]
    if len(title) > 30:
        await message.reply("Title is too long, please try again")
        return
    text_dict = {title: {'1': [], '2': [], '3': [], '4': []}}
    for t in text_sep[1:]:
        t = t.split(' - ')
        try:
            text_dict[title]['1'].append({'front': t[0], 'back': t[1]})
        except IndexError:
            await message.reply("Wrong input, please try again")
            return

    try:
        with open(f'json_words/{message.chat.id}.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        data.update(text_dict)
        with open(f'json_words/{message.chat.id}.json', 'wt', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    except FileNotFoundError:
        with open(f'json_words/{message.chat.id}.json', 'wt', encoding='utf-8') as f:
            json.dump(text_dict, f, ensure_ascii=False, indent=2)

    await state.finish()
    await message.answer("Successfully created!", reply_markup=keyboard())


async def leaning_mode(message):
    titles = await choose_deck(message)
    if not titles:
        return

    key = types.InlineKeyboardMarkup()
    for t in titles:
        but_1 = types.InlineKeyboardButton(t, callback_data=f'1{t}')
        but_2 = types.InlineKeyboardButton('Show words', callback_data=f'4{t}')
        key.add(but_1, but_2)
    await Start_learning.deck.set()
    await message.answer("Learning mode", reply_markup=back_keyboard())
    await message.answer("Choose the deck", reply_markup=key)


async def editing_mode(message):
    titles = await choose_deck(message)
    if not titles:
        return

    key = types.InlineKeyboardMarkup()
    for t in titles:
        key.add(types.InlineKeyboardButton(t, callback_data=str(t)))
    await Editing.deck.set()
    await message.answer("Editing mode", reply_markup=back_keyboard())
    await message.answer("Choose the deck", reply_markup=key)


async def deleting_mode(message):
    titles = await choose_deck(message)
    if not titles:
        return

    key = types.InlineKeyboardMarkup()
    for t in titles:
        key.add(types.InlineKeyboardButton(t, callback_data=str(t)))
    await Delete_deck.deck.set()
    await message.answer("Deleting mode", reply_markup=back_keyboard())
    await message.answer("Choose the deck", reply_markup=key)


async def learning_first(state, callback_query=None, title=None, message=None):
    chat_id = message.chat.id if message else callback_query.message.chat.id
    if message:
        state_data = await state.get_data()
        title = state_data['title']
    with open(f'json_words/{chat_id}.json', 'r', encoding='utf-8') as f:
        data = json.load(f)[title]

    none_empty_keys = []
    for i in range(1, 5):
        if data[str(i)]:
            none_empty_keys.append(i)
    if not none_empty_keys:
        with open(f'json_words/{chat_id}.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        del data[title]
        with open(f'json_words/{chat_id}.json', 'wt', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        await bot.send_message(chat_id, "Congratulations! You have learned all words! Deck deleted.")
        await bot.send_sticker(chat_id, 'CAACAgIAAxkBAAEBIc1fJa69B9GvKo7oD4pGYc7SA4BLOQACSgIAAladvQrJasZoYBh68BoE')
        return

    weights = [status_random_weights[x] for x in status_random_weights if x in none_empty_keys]
    status = str(random.choices(none_empty_keys, weights=weights, k=1)[0])

    num = random.randrange(0, len(data[status]))
    word = data[status][num]
    side = side_list[random.getrandbits(1)]
    key = types.InlineKeyboardMarkup()
    but_1 = types.InlineKeyboardButton("Show", callback_data='2')
    but_2 = types.InlineKeyboardButton("Listen", callback_data='3')
    if side == side_list[0]:
        key.add(but_1, but_2)
    else:
        key.add(but_1)
    await state.update_data({'status': status, 'num': num, 'side': side})
    await bot.send_message(chat_id, str(word[side]), parse_mode="Markdown", reply_markup=key)
    if callback_query:
        await callback_query.answer()


async def learning_second(callback_query, state):
    state_data = await state.get_data()
    with open(f'json_words/{callback_query.from_user.id}.json', 'r', encoding='utf-8') as f:
        data = json.load(f)[state_data['title']]
    word = data[state_data['status']][state_data['num']]
    await callback_query.answer()
    await callback_query.message.edit_text(f"{word['front']}\n➖➖➖➖➖\n{word['back']}")
    await learning_first(state, callback_query, state_data['title'])


@dp.message_handler(content_types=['text'], state=Start_learning.deck)
async def answer_handler(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    if await cancel(message, state):
        if state_data:
            if state_data['words_in_deck'] > 0:
                await message.answer(f"Words: {state_data['score']}/{state_data['words_in_deck']} "
                                     f"({(state_data['score']*100/state_data['words_in_deck']).__round__(1)}%)")
        return

    with open(f'json_words/{message.from_user.id}.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    word = data[state_data['title']][state_data['status']][state_data['num']]

    side = state_data['side']
    if str(message.text).lower() == str(word[side_list[0] if side == side_list[1] else side_list[1]]).lower():
        new_status = str(int(state_data['status']) + 1)
        del data[state_data['title']][state_data['status']][state_data['num']]
        if new_status != '5':
            data[state_data['title']][new_status].append(word)
        else:
            await message.answer("You have completely learned this word! Word deleted.")

        with open(f'json_words/{message.from_user.id}.json', 'wt', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        if not word['front'] in state_data['completed']:
            state_data['completed'].add(word['front'])
            await state.update_data({'score': state_data['score'] + 1, 'completed': state_data['completed']})
        await message.answer("Right!")
    else:
        await message.answer(f"Wrong!\nAnswer: {word[side_list[0] if side == side_list[1] else side_list[1]]}")
    await learning_first(state, message=message)


@dp.callback_query_handler(lambda callback_query: True, state=Start_learning.deck)
async def callback_inline(callback_query: types.CallbackQuery, state: FSMContext):
    data = callback_query.data
    if data[:1] == "1":
        title = data[1:]
        with open(f'json_words/{callback_query.from_user.id}.json', 'r', encoding='utf-8') as f:
            data = json.load(f)[title]
        words_in_deck = sum(len(data[status]) for status in data)
        await state.update_data({'title': title, 'score': 0, 'words_in_deck': words_in_deck, 'completed': set()})
        await callback_query.answer()
        await callback_query.message.answer("Send translation or click 'Show'")
        await learning_first(state, callback_query, title)
    elif data == "2":
        await learning_second(callback_query, state)
    elif data == "3":
        data = await state.get_data()
        with open(f'json_words/{callback_query.from_user.id}.json', 'r', encoding='utf-8') as f:
            text = json.load(f)[data['title']][data['status']][data['num']]['front']
        speech = tts.synthesise(text)
        key = types.InlineKeyboardMarkup()
        key.add(types.InlineKeyboardButton("Show", callback_data='2'))
        await callback_query.message.edit_reply_markup(key)
        await bot.send_voice(callback_query.from_user.id, speech)
    elif data[:1] == "4":
        await state.finish()
        title = data[1:]
        with open(f'json_words/{callback_query.from_user.id}.json', 'r', encoding='utf-8') as f:
            data = json.load(f)[title]
        string = ''
        i = 1
        for status in data:
            for word in data[status]:
                string += f"<b>{i}.</b> {word['front']} - {word['back']}<br>"
                i += 1
        url = tp.create_post(title, string)
        await callback_query.answer()
        await callback_query.message.answer(f"[{title}]({url})", parse_mode="Markdown", reply_markup=keyboard())


@dp.message_handler(content_types=['text'], state=Editing.deck)
async def answer_handler(message: types.Message, state: FSMContext):
    if await cancel(message, state):
        return


@dp.message_handler(content_types=['text'], state=Editing.words)
async def answer_handler(message: types.Message, state: FSMContext):
    if await cancel(message, state):
        return

    state_data = await state.get_data()
    text_sep = str(message.text).split('\n')

    with open(f'json_words/{message.chat.id}.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    for t in text_sep:
        t = t.split(' - ')
        try:
            data[state_data['title']]['1'].append({'front': t[0], 'back': t[1]})
        except IndexError:
            await message.reply("Wrong input, please try again")
            return

    with open(f'json_words/{message.chat.id}.json', 'wt', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    await state.finish()
    await message.answer("Successfully edited!", reply_markup=keyboard())


@dp.callback_query_handler(lambda callback_query: True, state=Editing.deck)
async def callback_inline(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data({"title": callback_query.data})
    await callback_query.answer()
    await callback_query.message.answer("You can add words to this deck.\n"
                                        "Send me a list of words. Please use this format:\n\n"
                                        "word1 front side - word1 back side\nword2 front side - word2 back side")
    await Editing.next()


@dp.message_handler(content_types=['text'], state=Delete_deck.deck)
async def answer_handler(message: types.Message, state: FSMContext):
    if await cancel(message, state):
        return


@dp.callback_query_handler(lambda callback_query: True, state=Delete_deck.deck)
async def callback_inline(callback_query: types.CallbackQuery, state: FSMContext):
    with open(f'json_words/{callback_query.message.chat.id}.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    del data[callback_query.data]
    with open(f'json_words/{callback_query.message.chat.id}.json', 'wt', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    await state.finish()
    await callback_query.answer()
    await callback_query.message.answer("Successfully deleted!")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
