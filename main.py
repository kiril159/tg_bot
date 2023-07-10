from telebot import types
import openai
from func_for_bot import main_start, write_json_to_s3, clean_data, send_message
import time
from secure.utils import bot, key_ai


openai.api_key = key_ai
auth_suc = 0
model_type = None
file_name = None
main_dict = {}


@bot.message_handler(commands=['start'])
def start_message(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    reg_button = types.KeyboardButton(text="Отправить номер телефона",
                                      request_contact=True)
    keyboard.add(reg_button)
    bot.send_message(message.chat.id, 'Необходимо пройти авторизацию по номеру телефона ',
                     reply_markup=keyboard)


@bot.message_handler(content_types=['contact'])
def auth_and_choose(message):
    global auth_suc, mes
    with open('secure/secret.csv', 'r') as base:
        base_number = [el.replace('\n', '') for el in base]
    if message.contact.phone_number in base_number:
        mes = []
        bot.send_message(message.chat.id, 'Успешно пройдена')
        text = 'Нажмите на соответсвующую команду, чтобы перейти на нужного вам бота:\n 1) /gpt_3 - для ' \
               'обещния с ChatGPT 3.5 \n2)/gpt_4 - для общения с ChatGPT 4\n3) /GetRentaCar - для создания заявки в GetRentaCar'
        bot.send_message(message.chat.id,
                         text=text)
        bot.register_next_step_handler(message, talk_with_ai)
        auth_suc = 1
    else:
        bot.send_message(message.chat.id, 'Не пройдена')


@bot.message_handler(content_types=['text'])
def talk_with_ai(message):
    global auth_suc, model_type, file_name
    if model_type is None:
        model_type = message.text
    if message.text == 'Завершить общение':
        bot.send_message(message.chat.id, 'Ждем вас снова')
        auth_suc = 0
    else:
        if auth_suc == 1:
            if model_type == '/gpt_3' or model_type == '/gpt_4':
                if message.text == '/gpt_3' or message.text == '/gpt_3':
                    text = 'Для прекращения общения ввведите "Завершить общение"'
                    bot.send_message(message.chat.id,
                                     text=text)
                content = message.text
                mes.append({"role": "user", "content": content})

                completion = openai.ChatCompletion.create(
                    model='gpt-3.5-turbo' if '3' in model_type else 'gpt-4',messages=mes)
                chat_response = completion.choices[0].message.content
                bot.send_message(message.chat.id,
                                 text=chat_response)
                mes.append({"role": "assistant", "content": chat_response})
            elif model_type == '/GetRentaCar':
                if message.text == '/GetRentaCar':
                    try:
                        main_dict.pop(message.from_user.id)
                    except:
                        pass
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    btn1 = types.KeyboardButton("Заполнить заявку")
                    markup.add(btn1)
                    rule = 'Инструкция: \n1) Для запуска заполнения заявки нажать кнопку ' \
                           '"Заполнить заявку"\n2) Пообщаться\n3) После заполнения заявки нажать на кнопку "Отменить заявку"' \
                           '. После этого диалог запишется в хранилище '
                    bot.send_message(message.chat.id, text=rule, reply_markup=markup)
                elif message.text == 'Заполнить заявку':
                    response, message_log = main_start()
                    main_dict.update({message.from_user.id: message_log})
                    file_name = str(time.time()) + ".json"
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    btn1 = types.KeyboardButton("Отменить заявку")
                    markup.add(btn1)
                    write_json_to_s3({"AI": response}, message.from_user.id, file_name)
                    bot.send_message(message.from_user.id, text=clean_data(response), reply_markup=markup)
                elif 'тзыв:' in message.text:
                    write_json_to_s3({"USER_feedback": message.text[6:]}, message.from_user.id, file_name)
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    btn1 = types.KeyboardButton("Заполнить заявку")
                    markup.add(btn1)
                    bot.send_message(message.chat.id, text="Спасибо за отзыв", reply_markup=markup)
                    auth_suc = 0
                else:
                    if message.text == '/end' or message.text == "Отменить заявку":
                        main_dict.pop(message.from_user.id)
                        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                        btn1 = types.KeyboardButton("Заполнить заявку")
                        markup.add(btn1)
                        feedback = 'Оставьте, пожалуста, отзыв об общении по поводу заявки в формате: \n' \
                                   'Отзыв: <Текст отзыва>'
                        bot.send_message(message.chat.id, text=feedback, reply_markup=markup)
                    else:
                        message_log = main_dict[message.from_user.id]
                        user_input = message.text
                        message_log.append({"role": "user", "content": user_input})
                        response = send_message(message_log)
                        message_log.append({"role": "assistant", "content": response})
                        main_dict.update({message.from_user.id: message_log})
                        write_json_to_s3({"USER": message.text}, message.from_user.id, file_name)
                        write_json_to_s3({"AI": response}, message.from_user.id, file_name)
                        write_json_to_s3({"LOG": response[response.find('{'):response.rfind('}') + 1] if response.find(
                            '{') != -1 else None},
                                         message.from_user.id, file_name)
                        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                        btn1 = types.KeyboardButton("Отменить заявку")
                        markup.add(btn1)

                        bot.send_message(message.from_user.id, text=clean_data(response))
            else:
                bot.send_message(message.chat.id, 'Выберите версию для общения')
        else:
            bot.send_message(message.chat.id, 'Необходимо авторизоваться')


bot.polling(none_stop=True, interval=0)
