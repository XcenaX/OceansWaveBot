# -*- coding: utf-8 -*-
import datetime
import telebot
from telebot import TeleBot, types

from threading import Thread
from django.template.loader import render_to_string
import requests

class Bot():
    owners_file = "bot_data/owners.txt"
    users_file = "bot_data/users.txt"
    api_url = "https://oceans-wave.org/api/"
    bot = None
    channel_name = ""

    def __init__(self, settings):
        self.bot = telebot.TeleBot(settings["bot_token"])
        self.channel_name = settings["channel_name"]
        self.owners_file = settings["BASE_DIR"]/self.owners_file
        self.users_file = settings["BASE_DIR"]/self.users_file
        @self.bot.message_handler(content_types=['text'])
        def start(message):            
            if self.check_owner(message.from_user.id):
                if message.text == "/start":
                    self.add_user(message.from_user.id)
                    self.bot.send_message(message.from_user.id, "Привет", reply_markup=self.get_main_keyboard())
                else:
                    self.bot.send_message(message.from_user.id, "Привет", reply_markup=self.get_main_keyboard())
            else:
                self.bot.send_message(message.from_user.id, "Привет", reply_markup=self.get_user_keyboard())


        @self.bot.callback_query_handler(func=lambda call: True)
        def callback_worker(call):            
            if call.data == "add_new":                
                self.bot.send_message(call.message.chat.id, "Напиши текст рассылки: ")
                self.bot.register_next_step_handler(call.message, self.make_mailing)
            elif call.data == "search_specialist":
                self.bot.send_message(call.message.chat.id, "Выберите страну: ", reply_markup=self.get_countries_keyboard())
            elif "country" in call.data:
                country = self.get_country_by_callback(call.data)
                self.bot.send_message(call.message.chat.id, "Выберите город: ", reply_markup=self.get_cities_keyboard(country))
            elif "city" in call.data:
                text = self.get_specialsts_data_by_city(call.data)
                self.bot.send_message(call.message.chat.id, text, reply_markup=self.get_main_keyboard())
            elif "cancel" in call.data:
                self.bot.send_message(call.message.chat.id, "Выберите действие:", reply_markup=self.get_main_keyboard())
            else:
                self.bot.send_message(call.message.chat.id, "Я тебя не понимаю")
            self.bot.delete_message(call.message.chat.id, call.message.id)

    def get_owners(self):
        with open(self.owners_file) as f:
            content = f.readlines()
        content = [x.strip() for x in content]
        return content

    def get_users(self):
        with open(self.users_file) as f:
            content = f.readlines()
        content = [x.strip() for x in content]
        return content

    def add_user(self, id):
        id = str(id)
        users = self.get_users()
        if id not in users:
            with open(self.users_file, "a") as f:
                f.write("\n"+id)

    def get_countries(self):
        responce = requests.get(self.api_url+"countries/")
        data = responce.json()
        print(data)
        return data

    def get_country_by_callback(self, callback):
        callback = callback.replace("country", "")
        responce = requests.get(self.api_url+"countries/"+callback)
        return responce.json()

    def get_specialsts_data_by_city(self, callback):
        callback = callback.replace("city", "")
        responce = requests.get(self.api_url+"specialists?city="+callback)
        specialists = responce.json()
        text = """Контакты специалистов:\n"""
        for specialist in specialists:
            text += """\n
            Имя: {0}
            Whatsapp: {1}
            Telegram: {2}
            \n
            """.format(specialist["name"], specialist["whatsapp"], specialist["telegram"])
        return text

    def check_owner(self, name):
        name = str(name)
        owners = self.get_owners()
        if name in owners:
            return True
        return False

    def check_date_format(self, date):
        try:
            datetime.datetime.strptime(date, "%Y.%m.%d %H:%M")
        except:
            return False
        return True


    def get_main_keyboard(self):
        keyboard = types.InlineKeyboardMarkup() 
        add_new = types.InlineKeyboardButton(text="Сделать рассылку", callback_data="add_new")
        search_specialist = types.InlineKeyboardButton(text="Написать консультанту", callback_data="search_specialist")
        keyboard.add(add_new)
        keyboard.add(search_specialist)
        return keyboard

    def get_user_keyboard(self):
        keyboard = types.InlineKeyboardMarkup() 
        search_specialist = types.InlineKeyboardButton(text="Написать консультанту", callback_data="search_specialist")
        keyboard.add(search_specialist)
        return keyboard

    def get_countries_keyboard(self):
        keyboard = types.InlineKeyboardMarkup() 
        countries = self.get_countries()
        for country in countries:
            current_country = types.InlineKeyboardButton(text=country["country"], callback_data="country"+country["id"])        
            keyboard.add(current_country)
        cancel = types.InlineKeyboardButton(text="Отмена", callback_data="cancel")        
        keyboard.add(cancel)
        return keyboard

    def get_cities_keyboard(self, country):
        keyboard = types.InlineKeyboardMarkup()
        for city in country["cities"]:
            current_city = types.InlineKeyboardButton(text=city["name"], callback_data="country"+city["id"])        
            keyboard.add(current_city)
        cancel = types.InlineKeyboardButton(text="Отмена", callback_data="cancel")        
        keyboard.add(cancel)
        return keyboard

    def make_mailing(self, message):
        if "wrong" not in message.text:
            self.bot.send_message(chat_id="@%s" % self.channel_name, text=message.text)
            self.bot.send_message(message.from_user.id, "Я закончил рассылку\nЧто дальше?",  reply_markup=self.get_main_keyboard())

    def send_event(self, event):
        users = self.get_users()
        message_html = render_to_string('telegram_message.html', {
            'event': event
        })
        self.bot.send_message(chat_id="@%s" % self.channel_name, text=message_html, parse_mode="html")
        # for user in users:
        #     bot.send_message(user, text=event_text, parse_mode="html")

    def start_bot(self):
        thread = Thread(target = self.bot.polling, args = (True, 0))
        thread.start()

