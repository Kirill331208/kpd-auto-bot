import logging
import requests
import asyncio
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from telegram.ext import CallbackContext

# Включение логирования для отслеживания ошибок
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
CHOICE, MODEL, YEAR, COLOR, MILEAGE, BUDGET, CONTACT, NAME, CITY, PHOTO, REVIEW_TEXT, CURRENCY = range(12)

# ID вашего Telegram аккаунта для отправки уведомлений
OWNER_ID = '434248995'  # Ваш Telegram User ID

# Функция для удаления сообщений после отправки нового сообщения
async def delete_message(update, context, message_id, delay=5):
    await asyncio.sleep(delay)  # Уменьшаем задержку перед удалением
    try:
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=message_id)
    except Exception as e:
        logger.error(f"Ошибка при удалении сообщения: {e}")

# Удаление сообщений клиента и бота
async def delete_all_messages(update, context, delay=5):
    await asyncio.sleep(delay)
    try:
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
    except Exception as e:
        logger.error(f"Ошибка при удалении сообщения клиента: {e}")

# Функция старт (кнопка всегда видна)
async def start(update, context):
    # Приветственное сообщение и кнопки главного меню
    keyboard = [['Получить расчет', 'Оставить отзыв', 'Актуальный курс валют'], ['В главное меню']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)
    
    message = await update.message.reply_text(
        'Здравствуйте, Вас приветствует компания KPD AUTO! Выберите нужное действие.',
        reply_markup=reply_markup
    )
    # Удаляем это сообщение через 5 секунд после отправки нового
    await delete_message(update, context, message.message_id, 5)
    return CHOICE

# Реагирование на текстовые сообщения сразу при открытии чата
async def handle_message(update, context):
    if update.message.text == "/start" or update.message.text == "В главное меню":
        return await start(update, context)

# Обработка выбора кнопок "Получить расчет", "Оставить отзыв" и "Актуальный курс валют"
async def choice(update, context):
    if update.message.text == "Получить расчет":
        return await get_calculation(update, context)
    elif update.message.text == "Оставить отзыв":
        return await leave_feedback(update, context)
    elif update.message.text == "Актуальный курс валют":
        return await get_currency(update, context)
    elif update.message.text == "В главное меню":
        # Вернуться в главное меню
        return await start(update, context)

# 1. Получить расчет
async def get_calculation(update, context):
    keyboard = [['В главное меню']]  # Кнопка для возвращения в главное меню
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)
    
    message = await update.message.reply_text("Укажите модель авто:", reply_markup=reply_markup)
    # Удаляем это сообщение через 5 секунд после отправки нового
    await delete_message(update, context, message.message_id, 5)
    return MODEL

# Функции для сбора данных на расчет, с отправкой информации в Telegram
async def get_model(update, context):
    if update.message.text == "В главное меню":
        return await start(update, context)

    context.user_data['model'] = update.message.text
    message = await update.message.reply_text("Желаемый год выпуска:")
    # Удаляем это сообщение через 5 секунд
    await delete_message(update, context, message.message_id, 5)
    return YEAR

# Последующие функции следуют аналогично для других параметров
async def get_year(update, context):
    context.user_data['year'] = update.message.text
    message = await update.message.reply_text("Цвет автомобиля:")
    await delete_message(update, context, message.message_id, 5)
    return COLOR

async def get_color(update, context):
    context.user_data['color'] = update.message.text
    message = await update.message.reply_text("Примерный пробег:")
    await delete_message(update, context, message.message_id, 5)
    return MILEAGE

async def get_mileage(update, context):
    context.user_data['mileage'] = update.message.text
    message = await update.message.reply_text("Бюджет:")
    await delete_message(update, context, message.message_id, 5)
    return BUDGET

async def get_budget(update, context):
    context.user_data['budget'] = update.message.text
    message = await update.message.reply_text("Ваш контактный номер для связи:")
    await delete_message(update, context, message.message_id, 5)
    return CONTACT

async def get_contact(update, context):
    context.user_data['contact'] = update.message.text
    message = f"У вас новая заявка!\nХарактеристики:\nМодель: {context.user_data['model']}\nГод: {context.user_data['year']}\nЦвет: {context.user_data['color']}\nПробег: {context.user_data['mileage']}\nБюджет: {context.user_data['budget']}\nКонтактный номер: {context.user_data['contact']}"
    
    await context.bot.send_message(chat_id=OWNER_ID, text=message)
    
    whatsapp_link = "https://wa.me/79089892300"  # Пустая ссылка, без предзаполненного текста
    message = await update.message.reply_text(f"Ваша заявка уже направлена нашему менеджеру! Вы можете связаться с ним через чат: {whatsapp_link}")
    
    keyboard = [['В главное меню']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)
    await update.message.reply_text("Вы можете вернуться в главное меню:", reply_markup=reply_markup)
    
    # Удаляем это сообщение через 5 секунд
    await delete_message(update, context, message.message_id, 5)
    return ConversationHandler.END

# 2. Оставить отзыв
async def leave_feedback(update, context):
    message = await update.message.reply_text("Как вас зовут?")
    await delete_message(update, context, message.message_id, 5)
    return NAME

async def get_name(update, context):
    context.user_data['name'] = update.message.text
    message = await update.message.reply_text("Из какого вы города?")
    await delete_message(update, context, message.message_id, 5)
    return CITY

async def get_city(update, context):
    context.user_data['city'] = update.message.text
    message = await update.message.reply_text("Ваш отзыв:")
    await delete_message(update, context, message.message_id, 5)
    return REVIEW_TEXT

async def get_review_text(update, context):
    context.user_data['review'] = update.message.text
    keyboard = [['Прикрепить фото', 'Без фото'], ['В главное меню']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)
    message = await update.message.reply_text("Прикрепите фото (если есть):", reply_markup=reply_markup)
    await delete_message(update, context, message.message_id, 5)
    return PHOTO

async def get_photo(update, context):
    if update.message.text == "Без фото":
        context.user_data['photo'] = None
        # Отправляем сообщение, что отзыв принят
        message = await update.message.reply_text("Спасибо, ваш отзыв принят!")
        await delete_message(update, context, message.message_id, 5)
        
        # Отправляем отзыв в личку (если нужно)
        review_text = f"Отзыв от {context.user_data['name']} ({context.user_data['city']}): {context.user_data['review']}"
        if context.user_data['photo']:
            await context.bot.send_photo(chat_id=OWNER_ID, photo=context.user_data['photo'])
            review_text += f"\nФото: {context.user_data['photo']}"
        
        # Отправляем отзыв в личку владельцу
        await context.bot.send_message(chat_id=OWNER_ID, text=review_text)
        
        # Кнопка "В главное меню"
        keyboard = [['В главное меню']]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)
        await update.message.reply_text("Вы можете вернуться в главное меню:", reply_markup=reply_markup)
        
        # Удаляем это сообщение через 5 секунд
        await delete_message(update, context, message.message_id, 5)
    else:
        message = await update.message.reply_text("Пожалуйста, отправьте файл.")
        await delete_message(update, context, message.message_id, 5)
        return PHOTO  # Ожидаем отправку файла

async def handle_photo(update, context):
    if update.message.photo:
        context.user_data['photo'] = update.message.photo[-1].file_id
        message = await update.message.reply_text("Спасибо, ваш отзыв принят!")
        
        # Отправляем фото-отзыв и текстовые данные владельцу
        await context.bot.send_photo(chat_id=OWNER_ID, photo=update.message.photo[-1].file_id)
        await context.bot.send_message(chat_id=OWNER_ID, text=f"Отзыв от {context.user_data['name']} ({context.user_data['city']}): {context.user_data['review']}\nФото: {update.message.photo[-1].file_id}")
        
        # Удаляем это сообщение через 5 секунд
        await delete_message(update, context, message.message_id, 5)
        
        keyboard = [['В главное меню']]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)
        await update.message.reply_text("Вы можете вернуться в главное меню:", reply_markup=reply_markup)
    else:
        message = await update.message.reply_text("Фото не найдено, попробуйте снова!")
        await delete_message(update, context, message.message_id, 5)

    return ConversationHandler.END

# 3. Актуальный курс валют
async def get_currency(update, context):
    try:
        url = "https://api.exchangerate-api.com/v4/latest/RUB"
        response = requests.get(url)
        data = response.json()

        usd_rate = data["rates"]["USD"]
        jpy_rate = data["rates"]["JPY"]
        cny_rate = data["rates"]["CNY"]

        message = f"Актуальный курс валют для осуществления платежей в банке АТБ:\n" \
                  f"1 RUB = {usd_rate:.2f} USD\n" \
                  f"1 RUB = {jpy_rate:.2f} JPY\n" \
                  f"1 RUB = {cny_rate:.2f} CNY"
        
        message = await update.message.reply_text(message)
        await delete_message(update, context, message.message_id, 5)
    except Exception as e:
        message = await update.message.reply_text("Ошибка при получении данных по валютам.")
        await delete_message(update, context, message.message_id, 5)
    return CHOICE

# Основная функция для запуска бота
def main():
    application = Application.builder().token("7208190743:AAG4nqLETAq810JcwKWnjznl0BvpLOa3O1E").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choice)],
            MODEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_model)],
            YEAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_year)],
            COLOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_color)],
            MILEAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_mileage)],
            BUDGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_budget)],
            CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_contact)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_city)],
            REVIEW_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_review_text)],
            PHOTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_photo),
                    MessageHandler(filters.PHOTO, handle_photo)],
            CURRENCY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_currency)],
        },
        fallbacks=[],
    )

    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.TEXT, handle_message))  # Для реакции на любое сообщение

    application.run_polling()

if __name__ == '__main__':
    main()
