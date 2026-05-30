import logging
import requests
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = "8890268404:AAFMGKm7PqGm6zriD5nNvYLo0ZyQGHCwo18"
OWNER_CHAT_ID = 8418562620
CARD_NUMBER = "5614 6818 7542 0154"
CARD_OWNER = "S.K"
PROFIT_UZS = 50000
USD_TO_UZS = 12700

ENTER_AMOUNT, ENTER_WALLET, WAIT_RECEIPT = range(3)

user_langs = {}


def get_lang(uid):
    return user_langs.get(uid, "uz")


def get_price(symbol):
    try:
        ids = {"BTC": "bitcoin", "LTC": "litecoin", "USDT": "tether"}
        cid = ids[symbol]
        r = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={cid}&vs_currencies=usd", timeout=8)
        return r.json()[cid]["usd"]
    except Exception:
        return {"BTC": 67000, "LTC": 85, "USDT": 1.0}[symbol]


def main_kb(lang="uz"):
    if lang == "uz":
        kb = [
            [KeyboardButton("₿ BTC sotib olish"), KeyboardButton("Ł LTC sotib olish")],
            [KeyboardButton("💵 USDT sotib olish")],
            [KeyboardButton("📊 Kurslar"), KeyboardButton("🌐 Til / Язык")],
            [KeyboardButton("📞 Yordam")]
        ]
    else:
        kb = [
            [KeyboardButton("₿ Купить BTC"), KeyboardButton("Ł Купить LTC")],
            [KeyboardButton("💵 Купить USDT")],
            [KeyboardButton("📊 Курсы"), KeyboardButton("🌐 Язык / Til")],
            [KeyboardButton("📞 Помощь")]
        ]
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)


def cancel_kb(lang="uz"):
    t = "❌ Bekor qilish" if lang == "uz" else "❌ Отмена"
    return ReplyKeyboardMarkup([[KeyboardButton(t)]], resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = get_lang(uid)
    name = update.effective_user.first_name or "Do'st"
    if lang == "uz":
        txt = (f"👋 Assalomu alaykum, <b>{name}</b>!\n\n"
               "🏦 <b>Crypto Exchange Botiga xush kelibsiz!</b>\n\n"
               "💱 Xizmatlar:\n• Bitcoin (BTC)\n• Litecoin (LTC)\n• USDT\n\n"
               "👇 Tanlang:")
    else:
        txt = (f"👋 Привет, <b>{name}</b>!\n\n"
               "🏦 <b>Добро пожаловать в Crypto Exchange!</b>\n\n"
               "💱 Услуги:\n• Bitcoin (BTC)\n• Litecoin (LTC)\n• USDT\n\n"
               "👇 Выберите:")
    await update.message.reply_text(txt, parse_mode="HTML", reply_markup=main_kb(lang))
    return ConversationHandler.END


async def show_rates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = get_lang(uid)
    btc = get_price("BTC")
    ltc = get_price("LTC")
    usdt = get_price("USDT")
    if lang == "uz":
        txt = (f"📊 <b>Joriy kurslar (bizning narx):</b>\n\n"
               f"₿ BTC: <b>${btc:,.0f}</b> = <b>{btc*USD_TO_UZS+PROFIT_UZS:,.0f} UZS</b>\n"
               f"Ł LTC: <b>${ltc:,.2f}</b> = <b>{ltc*USD_TO_UZS+PROFIT_UZS:,.0f} UZS</b>\n"
               f"💵 USDT: <b>${usdt:,.2f}</b> = <b>{usdt*USD_TO_UZS+PROFIT_UZS:,.0f} UZS</b>")
    else:
        txt = (f"📊 <b>Текущие курсы (наша цена):</b>\n\n"
               f"₿ BTC: <b>${btc:,.0f}</b> = <b>{btc*USD_TO_UZS+PROFIT_UZS:,.0f} UZS</b>\n"
               f"Ł LTC: <b>${ltc:,.2f}</b> = <b>{ltc*USD_TO_UZS+PROFIT_UZS:,.0f} UZS</b>\n"
               f"💵 USDT: <b>${usdt:,.2f}</b> = <b>{usdt*USD_TO_UZS+PROFIT_UZS:,.0f} UZS</b>")
    await update.message.reply_text(txt, parse_mode="HTML", reply_markup=main_kb(lang))


async def start_exchange(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = get_lang(uid)
    txt = update.message.text

    if "BTC" in txt:
        cur = "BTC"
    elif "LTC" in txt:
        cur = "LTC"
    elif "USDT" in txt:
        cur = "USDT"
    else:
        return ConversationHandler.END

    price_usd = get_price(cur)
    price_uzs = price_usd * USD_TO_UZS + PROFIT_UZS
    context.user_data["cur"] = cur
    context.user_data["price_uzs"] = price_uzs
    context.user_data["price_usd"] = price_usd

    em = {"BTC": "₿", "LTC": "Ł", "USDT": "💵"}[cur]

    if lang == "uz":
        msg = (f"{em} <b>{cur} sotib olish</b>\n\n"
               f"Narx: 1 {cur} = <b>{price_uzs:,.0f} UZS</b>\n\n"
               f"Necha {cur} sotib olmoqchisiz?\n<i>Misol: 0.01</i>")
    else:
        msg = (f"{em} <b>Купить {cur}</b>\n\n"
               f"Цена: 1 {cur} = <b>{price_uzs:,.0f} UZS</b>\n\n"
               f"Сколько {cur} хотите купить?\n<i>Пример: 0.01</i>")

    await update.message.reply_text(msg, parse_mode="HTML", reply_markup=cancel_kb(lang))
    return ENTER_AMOUNT


async def enter_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = get_lang(uid)
    txt = update.message.text.strip()

    if "Bekor" in txt or "Отмена" in txt or "❌" in txt:
        return await do_cancel(update, context)

    try:
        amount = float(txt.replace(",", "."))
        if amount <= 0:
            raise ValueError
    except ValueError:
        err = "❌ To'g'ri raqam kiriting! Misol: <b>0.05</b>" if lang == "uz" else "❌ Введите правильное число! Пример: <b>0.05</b>"
        await update.message.reply_text(err, parse_mode="HTML")
        return ENTER_AMOUNT

    cur = context.user_data["cur"]
    price_uzs = context.user_data["price_uzs"]
    total = amount * price_uzs
    context.user_data["amount"] = amount
    context.user_data["total"] = total

    if lang == "uz":
        msg = (f"✅ <b>Buyurtma:</b> {amount} {cur}\n"
               f"💰 To'lov: <b>{total:,.0f} UZS</b>\n\n"
               f"📬 {cur} hamyon manzilingizni yuboring:")
    else:
        msg = (f"✅ <b>Заказ:</b> {amount} {cur}\n"
               f"💰 К оплате: <b>{total:,.0f} UZS</b>\n\n"
               f"📬 Отправьте ваш {cur} адрес кошелька:")

    await update.message.reply_text(msg, parse_mode="HTML", reply_markup=cancel_kb(lang))
    return ENTER_WALLET


async def enter_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = get_lang(uid)
    wallet = update.message.text.strip()

    if "Bekor" in wallet or "Отмена" in wallet or "❌" in wallet:
        return await do_cancel(update, context)

    if len(wallet) < 20:
        err = "❌ Noto'g'ri manzil!" if lang == "uz" else "❌ Неверный адрес!"
        await update.message.reply_text(err)
        return ENTER_WALLET

    context.user_data["wallet"] = wallet
    cur = context.user_data["cur"]
    total = context.user_data["total"]

    if lang == "uz":
        msg = (f"💳 <b>TO'LOV</b>\n\n"
               f"Summa: <b>{total:,.0f} UZS</b>\n\n"
               f"🏦 Karta:\n<code>{CARD_NUMBER}</code>\n"
               f"👤 {CARD_OWNER}\n\n"
               f"1️⃣ Kartaga pul o'tkazing\n"
               f"2️⃣ Chek rasmini yuboring\n\n"
               f"⚠️ <b>DIQQAT!</b> Soxta cheklar tekshiriladi! Bunday holda buyurtma bekor bo'ladi va huquq-tartibot organlari xabardor qilinadi!")
    else:
        msg = (f"💳 <b>ОПЛАТА</b>\n\n"
               f"Сумма: <b>{total:,.0f} UZS</b>\n\n"
               f"🏦 Карта:\n<code>{CARD_NUMBER}</code>\n"
               f"👤 {CARD_OWNER}\n\n"
               f"1️⃣ Переведите деньги на карту\n"
               f"2️⃣ Отправьте скриншот чека\n\n"
               f"⚠️ <b>ВНИМАНИЕ!</b> Поддельные чеки проверяются! При обнаружении — заказ аннулируется и передаётся в правоохранительные органы!")

    await update.message.reply_text(msg, parse_mode="HTML", reply_markup=cancel_kb(lang))
    return WAIT_RECEIPT


async def receive_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = get_lang(uid)
    user = update.effective_user

    if update.message.text and ("Bekor" in update.message.text or "Отмена" in update.message.text or "❌" in update.message.text):
        return await do_cancel(update, context)

    if not (update.message.photo or update.message.document):
        err = "📸 Chek rasmini yuboring!" if lang == "uz" else "📸 Отправьте фото чека!"
        await update.message.reply_text(err)
        return WAIT_RECEIPT

    cur = context.user_data.get("cur", "?")
    amount = context.user_data.get("amount", 0)
    total = context.user_data.get("total", 0)
    wallet = context.user_data.get("wallet", "-")
    uname = f"@{user.username}" if user.username else "username yoq"

    admin_msg = (f"🆕 <b>YANGI BUYURTMA!</b>\n\n"
                 f"👤 {user.full_name}\n"
                 f"🆔 ID: <code>{uid}</code>\n"
                 f"📱 {uname}\n\n"
                 f"💱 {amount} {cur}\n"
                 f"💰 {total:,.0f} UZS\n"
                 f"📬 <code>{wallet}</code>")

    try:
        if update.message.photo:
            await context.bot.send_photo(OWNER_CHAT_ID, update.message.photo[-1].file_id, caption=admin_msg, parse_mode="HTML")
        else:
            await context.bot.send_document(OWNER_CHAT_ID, update.message.document.file_id, caption=admin_msg, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Admin xabar xatosi: {e}")

    if lang == "uz":
        ok = (f"✅ <b>Chek qabul qilindi!</b>\n\n"
              f"⏳ Operator tekshirmoqda...\n"
              f"🚀 Tasdiqlangandan keyin {amount} {cur} yuboriladi.\n"
              f"⏱ 15-30 daqiqa ichida.")
    else:
        ok = (f"✅ <b>Чек получен!</b>\n\n"
              f"⏳ Оператор проверяет...\n"
              f"🚀 После подтверждения {amount} {cur} будет отправлено.\n"
              f"⏱ В течение 15-30 минут.")

    await update.message.reply_text(ok, parse_mode="HTML", reply_markup=main_kb(lang))
    context.user_data.clear()
    return ConversationHandler.END


async def change_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("🇺🇿 O'zbek", callback_data="lang_uz"),
        InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")
    ]])
    await update.message.reply_text("🌐 Tilni tanlang / Выберите язык:", reply_markup=kb)


async def set_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    if q.data == "lang_uz":
        user_langs[uid] = "uz"
        await q.edit_message_text("✅ Til: O'zbek")
        await context.bot.send_message(uid, "👇 Asosiy menyu:", reply_markup=main_kb("uz"))
    else:
        user_langs[uid] = "ru"
        await q.edit_message_text("✅ Язык: Русский")
        await context.bot.send_message(uid, "👇 Главное меню:", reply_markup=main_kb("ru"))


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = get_lang(uid)
    if lang == "uz":
        txt = "📞 <b>Yordam</b>\n\nSavollar bo'lsa operator bilan bog'laning.\n⏱ 09:00-22:00"
    else:
        txt = "📞 <b>Помощь</b>\n\nПо вопросам свяжитесь с оператором.\n⏱ 09:00-22:00"
    await update.message.reply_text(txt, parse_mode="HTML", reply_markup=main_kb(lang))


async def do_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = get_lang(uid)
    context.user_data.clear()
    txt = "❌ Bekor qilindi." if lang == "uz" else "❌ Отменено."
    await update.message.reply_text(txt, reply_markup=main_kb(lang))
    return ConversationHandler.END


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = get_lang(uid)
    txt = "❓ Tugmalardan foydalaning." if lang == "uz" else "❓ Используйте кнопки."
    await update.message.reply_text(txt, reply_markup=main_kb(lang))


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(r"(BTC|LTC|USDT)"), start_exchange)],
        states={
            ENTER_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_amount)],
            ENTER_WALLET: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_wallet)],
            WAIT_RECEIPT: [
                MessageHandler(filters.PHOTO | filters.Document.ALL, receive_receipt),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_receipt),
            ],
        },
        fallbacks=[MessageHandler(filters.Regex(r"(Bekor|Отмена|❌)"), do_cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(conv)
    app.add_handler(MessageHandler(filters.Regex(r"(Kurslar|Курсы|📊)"), show_rates))
    app.add_handler(MessageHandler(filters.Regex(r"(Til|Язык|🌐)"), change_lang))
    app.add_handler(MessageHandler(filters.Regex(r"(Yordam|Помощь|📞)"), help_cmd))
    app.add_handler(CallbackQueryHandler(set_lang, pattern=r"^lang_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))

    print("Bot ishga tushdi!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
