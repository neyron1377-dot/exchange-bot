import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters, ConversationHandler
)

# ==================== SOZLAMALAR ====================
BOT_TOKEN = "8890268404:AAFMGKm7PqGm6zriD5nNvYLo0ZyQGHCwo18"  # @BotFather dan olingan token

OWNER_CHAT_ID = "8418562620"  # Sizning Telegram ID (@userinfobot dan oling)

CARD_NUMBER = "5614 6818 7542 0154"
CARD_OWNER = "S.K"

PROFIT_UZS = 50000  # Har bir almashuv uchun foyda (UZS)

# UZS/USD kurs (taxminiy, real kurs API dan olinadi)
USD_TO_UZS = 12700  # 1 USD = 12700 UZS (taxminiy)

# ==================== STATE'LAR ====================
CHOOSE_CURRENCY, ENTER_AMOUNT, ENTER_WALLET, WAIT_RECEIPT = range(4)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==================== KURS OLISH ====================
def get_crypto_price(symbol: str) -> float:
    """CoinGecko API dan kurs olish"""
    try:
        ids = {"BTC": "bitcoin", "LTC": "litecoin", "USDT": "tether"}
        coin_id = ids.get(symbol.upper(), "bitcoin")
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
        response = requests.get(url, timeout=10)
        data = response.json()
        return data[coin_id]["usd"]
    except Exception:
        # Fallback narxlar
        fallback = {"BTC": 67000, "LTC": 85, "USDT": 1.0}
        return fallback.get(symbol.upper(), 1.0)


def usd_to_uzs(usd_amount: float) -> float:
    return usd_amount * USD_TO_UZS


# ==================== KLAVIATURA ====================
def main_keyboard(lang="uz"):
    if lang == "uz":
        keyboard = [
            [KeyboardButton("₿ Bitcoin (BTC) sotib olish"), KeyboardButton("Ł Litecoin (LTC) sotib olish")],
            [KeyboardButton("💵 USDT sotib olish")],
            [KeyboardButton("📊 Joriy kurslar"), KeyboardButton("🌐 Til / Язык")],
            [KeyboardButton("📞 Aloqa / Yordam")]
        ]
    else:
        keyboard = [
            [KeyboardButton("₿ Купить Bitcoin (BTC)"), KeyboardButton("Ł Купить Litecoin (LTC)")],
            [KeyboardButton("💵 Купить USDT")],
            [KeyboardButton("📊 Текущие курсы"), KeyboardButton("🌐 Язык / Til")],
            [KeyboardButton("📞 Контакты / Помощь")]
        ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def cancel_keyboard(lang="uz"):
    text = "❌ Bekor qilish" if lang == "uz" else "❌ Отмена"
    return ReplyKeyboardMarkup([[KeyboardButton(text)]], resize_keyboard=True)


# ==================== TILNI SAQLASH ====================
user_langs = {}
user_states = {}


def get_lang(user_id):
    return user_langs.get(user_id, "uz")


# ==================== /START ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_lang(user_id)
    name = update.effective_user.first_name or "Do'stim"

    if lang == "uz":
        text = (
            f"👋 Assalomu alaykum, <b>{name}</b>!\n\n"
            "🏦 <b>Crypto Exchange Botiga xush kelibsiz!</b>\n\n"
            "💱 Biz quyidagi xizmatlarni taqdim etamiz:\n"
            "• <b>Bitcoin (BTC)</b> sotib olish\n"
            "• <b>Litecoin (LTC)</b> sotib olish\n"
            "• <b>USDT (TRC20/ERC20)</b> sotib olish\n\n"
            "⚡ Tez va xavfsiz almashuv xizmati!\n\n"
            "👇 Quyidagi tugmalardan birini tanlang:"
        )
    else:
        text = (
            f"👋 Привет, <b>{name}</b>!\n\n"
            "🏦 <b>Добро пожаловать в Crypto Exchange Bot!</b>\n\n"
            "💱 Мы предоставляем следующие услуги:\n"
            "• <b>Bitcoin (BTC)</b> — купить\n"
            "• <b>Litecoin (LTC)</b> — купить\n"
            "• <b>USDT (TRC20/ERC20)</b> — купить\n\n"
            "⚡ Быстрый и безопасный обмен!\n\n"
            "👇 Выберите одну из кнопок ниже:"
        )

    await update.message.reply_text(text, parse_mode="HTML", reply_markup=main_keyboard(lang))
    return ConversationHandler.END


# ==================== KURSLAR ====================
async def show_rates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_lang(user_id)

    btc_usd = get_crypto_price("BTC")
    ltc_usd = get_crypto_price("LTC")
    usdt_usd = get_crypto_price("USDT")

    profit_usd = PROFIT_UZS / USD_TO_UZS

    btc_uzs = usd_to_uzs(btc_usd) + PROFIT_UZS
    ltc_uzs = usd_to_uzs(ltc_usd) + PROFIT_UZS
    usdt_uzs = usd_to_uzs(usdt_usd) + PROFIT_UZS

    if lang == "uz":
        text = (
            "📊 <b>Joriy kurslar (bizning narxlar):</b>\n\n"
            f"₿ <b>Bitcoin (BTC):</b>\n"
            f"  • 1 BTC = <b>${btc_usd:,.2f}</b> USD\n"
            f"  • 1 BTC = <b>{btc_uzs:,.0f}</b> UZS\n\n"
            f"Ł <b>Litecoin (LTC):</b>\n"
            f"  • 1 LTC = <b>${ltc_usd:,.2f}</b> USD\n"
            f"  • 1 LTC = <b>{ltc_uzs:,.0f}</b> UZS\n\n"
            f"💵 <b>USDT (Tether):</b>\n"
            f"  • 1 USDT = <b>${usdt_usd:,.2f}</b> USD\n"
            f"  • 1 USDT = <b>{usdt_uzs:,.0f}</b> UZS\n\n"
            f"💱 USD/UZS: <b>{USD_TO_UZS:,}</b>\n\n"
            "🕐 Kurslar real vaqtda yangilanadi"
        )
    else:
        text = (
            "📊 <b>Текущие курсы (наши цены):</b>\n\n"
            f"₿ <b>Bitcoin (BTC):</b>\n"
            f"  • 1 BTC = <b>${btc_usd:,.2f}</b> USD\n"
            f"  • 1 BTC = <b>{btc_uzs:,.0f}</b> UZS\n\n"
            f"Ł <b>Litecoin (LTC):</b>\n"
            f"  • 1 LTC = <b>${ltc_usd:,.2f}</b> USD\n"
            f"  • 1 LTC = <b>{ltc_uzs:,.0f}</b> UZS\n\n"
            f"💵 <b>USDT (Tether):</b>\n"
            f"  • 1 USDT = <b>${usdt_usd:,.2f}</b> USD\n"
            f"  • 1 USDT = <b>{usdt_uzs:,.0f}</b> UZS\n\n"
            f"💱 USD/UZS: <b>{USD_TO_UZS:,}</b>\n\n"
            "🕐 Курсы обновляются в реальном времени"
        )

    await update.message.reply_text(text, parse_mode="HTML", reply_markup=main_keyboard(lang))


# ==================== ALMASHUV BOSHLASH ====================
async def start_exchange(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_lang(user_id)
    text = update.message.text

    # Qaysi valyuta tanlangani aniqlash
    if "BTC" in text or "Bitcoin" in text or "Биткоин" in text or "биткоин" in text.lower():
        currency = "BTC"
    elif "LTC" in text or "Litecoin" in text or "Лайткоин" in text or "лайткоин" in text.lower():
        currency = "LTC"
    elif "USDT" in text:
        currency = "USDT"
    else:
        return ConversationHandler.END

    context.user_data["currency"] = currency

    price_usd = get_crypto_price(currency)
    price_uzs = usd_to_uzs(price_usd) + PROFIT_UZS

    context.user_data["price_usd"] = price_usd
    context.user_data["price_uzs"] = price_uzs

    emoji = {"BTC": "₿", "LTC": "Ł", "USDT": "💵"}[currency]

    if lang == "uz":
        text_reply = (
            f"{emoji} <b>{currency} sotib olish</b>\n\n"
            f"📈 Joriy narx:\n"
            f"  • 1 {currency} = <b>${price_usd:,.2f}</b> USD\n"
            f"  • 1 {currency} = <b>{price_uzs:,.0f}</b> UZS\n\n"
            f"✍️ Necha {currency} sotib olmoqchisiz?\n"
            f"<i>Miqdorni yozing (masalan: 0.01 yoki 0.5)</i>"
        )
    else:
        text_reply = (
            f"{emoji} <b>Купить {currency}</b>\n\n"
            f"📈 Текущая цена:\n"
            f"  • 1 {currency} = <b>${price_usd:,.2f}</b> USD\n"
            f"  • 1 {currency} = <b>{price_uzs:,.0f}</b> UZS\n\n"
            f"✍️ Сколько {currency} хотите купить?\n"
            f"<i>Введите количество (например: 0.01 или 0.5)</i>"
        )

    await update.message.reply_text(text_reply, parse_mode="HTML", reply_markup=cancel_keyboard(lang))
    return ENTER_AMOUNT


# ==================== MIQDOR KIRITISH ====================
async def enter_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_lang(user_id)
    text = update.message.text.strip()

    # Bekor qilish
    if "Bekor" in text or "Отмена" in text or "❌" in text:
        await cancel(update, context)
        return ConversationHandler.END

    try:
        amount = float(text.replace(",", "."))
        if amount <= 0:
            raise ValueError
    except ValueError:
        if lang == "uz":
            await update.message.reply_text("❌ Iltimos, to'g'ri raqam kiriting! Masalan: <b>0.05</b>", parse_mode="HTML")
        else:
            await update.message.reply_text("❌ Пожалуйста, введите правильное число! Например: <b>0.05</b>", parse_mode="HTML")
        return ENTER_AMOUNT

    currency = context.user_data.get("currency", "BTC")
    price_uzs = context.user_data.get("price_uzs", 0)

    total_uzs = amount * price_uzs

    context.user_data["amount"] = amount
    context.user_data["total_uzs"] = total_uzs

    emoji = {"BTC": "₿", "LTC": "Ł", "USDT": "💵"}[currency]

    if lang == "uz":
        text_reply = (
            f"✅ <b>Buyurtma tafsilotlari:</b>\n\n"
            f"{emoji} <b>{amount} {currency}</b>\n"
            f"💰 Narx: <b>{price_uzs:,.0f}</b> UZS / {currency}\n"
            f"💳 Jami to'lov: <b>{total_uzs:,.0f} UZS</b>\n\n"
            f"📬 Endi <b>{currency} hamyon manzilingizni</b> yuboring:\n"
            f"<i>(Crypto olish uchun hamyon adresingiz)</i>"
        )
    else:
        text_reply = (
            f"✅ <b>Детали заказа:</b>\n\n"
            f"{emoji} <b>{amount} {currency}</b>\n"
            f"💰 Цена: <b>{price_uzs:,.0f}</b> UZS / {currency}\n"
            f"💳 Итого к оплате: <b>{total_uzs:,.0f} UZS</b>\n\n"
            f"📬 Теперь отправьте ваш <b>{currency} адрес кошелька:</b>\n"
            f"<i>(Адрес для получения криптовалюты)</i>"
        )

    await update.message.reply_text(text_reply, parse_mode="HTML", reply_markup=cancel_keyboard(lang))
    return ENTER_WALLET


# ==================== HAMYON MANZILI ====================
async def enter_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_lang(user_id)
    wallet = update.message.text.strip()

    # Bekor qilish
    if "Bekor" in wallet or "Отмена" in wallet or "❌" in wallet:
        await cancel(update, context)
        return ConversationHandler.END

    if len(wallet) < 20:
        if lang == "uz":
            await update.message.reply_text("❌ Noto'g'ri hamyon manzili! Iltimos, to'g'ri manzil kiriting.")
        else:
            await update.message.reply_text("❌ Неверный адрес кошелька! Пожалуйста, введите правильный адрес.")
        return ENTER_WALLET

    context.user_data["wallet"] = wallet

    currency = context.user_data.get("currency", "BTC")
    amount = context.user_data.get("amount", 0)
    total_uzs = context.user_data.get("total_uzs", 0)

    if lang == "uz":
        text_reply = (
            f"💳 <b>TO'LOV MA'LUMOTLARI</b>\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📦 Buyurtma: <b>{amount} {currency}</b>\n"
            f"💰 To'lov summasi: <b>{total_uzs:,.0f} UZS</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"🏦 <b>Karta raqami:</b>\n"
            f"<code>{CARD_NUMBER}</code>\n"
            f"👤 Egasi: <b>{CARD_OWNER}</b>\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📋 <b>Ko'rsatma:</b>\n"
            f"1️⃣ Yuqoridagi karta raqamiga <b>{total_uzs:,.0f} UZS</b> o'tkazing\n"
            f"2️⃣ To'lov chekini (screenshot) bu yerga yuboring\n\n"
            f"⚠️ <b>DIQQAT!</b> Soxta cheklar tekshiriladi va bunday holatlarda buyurtma bekor qilinib, huquq-tartibot organlari ma'lumot oladi!\n\n"
            f"✅ To'lovni amalga oshirgach, chekni yuboring."
        )
    else:
        text_reply = (
            f"💳 <b>ДЕТАЛИ ОПЛАТЫ</b>\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📦 Заказ: <b>{amount} {currency}</b>\n"
            f"💰 Сумма к оплате: <b>{total_uzs:,.0f} UZS</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"🏦 <b>Номер карты:</b>\n"
            f"<code>{CARD_NUMBER}</code>\n"
            f"👤 Владелец: <b>{CARD_OWNER}</b>\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📋 <b>Инструкция:</b>\n"
            f"1️⃣ Переведите <b>{total_uzs:,.0f} UZS</b> на карту выше\n"
            f"2️⃣ Отправьте чек об оплате (скриншот) сюда\n\n"
            f"⚠️ <b>ВНИМАНИЕ!</b> Поддельные чеки проверяются! При обнаружении фальшивого чека заказ аннулируется и передаётся информация в правоохранительные органы!\n\n"
            f"✅ После оплаты отправьте чек."
        )

    await update.message.reply_text(text_reply, parse_mode="HTML", reply_markup=cancel_keyboard(lang))
    return WAIT_RECEIPT


# ==================== CHEK KUTISH ====================
async def receive_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_lang(user_id)
    user = update.effective_user

    # Bekor qilish
    if update.message.text and ("Bekor" in update.message.text or "Отмена" in update.message.text or "❌" in update.message.text):
        await cancel(update, context)
        return ConversationHandler.END

    # Chek tekshirish (rasm yoki hujjat kerak)
    if not (update.message.photo or update.message.document):
        if lang == "uz":
            await update.message.reply_text(
                "📸 Iltimos, to'lov chekini <b>rasm (screenshot)</b> ko'rinishida yuboring!",
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text(
                "📸 Пожалуйста, отправьте чек об оплате в виде <b>изображения (скриншота)</b>!",
                parse_mode="HTML"
            )
        return WAIT_RECEIPT

    currency = context.user_data.get("currency", "BTC")
    amount = context.user_data.get("amount", 0)
    total_uzs = context.user_data.get("total_uzs", 0)
    wallet = context.user_data.get("wallet", "—")

    # ===== ADMINGA XABAR YUBORISH =====
    admin_text = (
        f"🆕 <b>YANGI BUYURTMA!</b>\n\n"
        f"👤 Mijoz: {user.full_name}\n"
        f"🆔 Telegram ID: <code>{user_id}</code>\n"
        f"📱 Username: @{user.username or 'yoq'}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💱 Valyuta: <b>{currency}</b>\n"
        f"📦 Miqdor: <b>{amount} {currency}</b>\n"
        f"💰 To'lov: <b>{total_uzs:,.0f} UZS</b>\n"
        f"📬 Hamyon: <code>{wallet}</code>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"⚠️ Chekni tekshiring va tasdiqlang!"
    )

    try:
        # Chekni adminga yuborish
        if update.message.photo:
            photo = update.message.photo[-1].file_id
            await context.bot.send_photo(
                chat_id=OWNER_CHAT_ID,
                photo=photo,
                caption=admin_text,
                parse_mode="HTML"
            )
        elif update.message.document:
            doc = update.message.document.file_id
            await context.bot.send_document(
                chat_id=OWNER_CHAT_ID,
                document=doc,
                caption=admin_text,
                parse_mode="HTML"
            )
    except Exception as e:
        logger.error(f"Admin ga xabar yuborishda xatolik: {e}")

    # ===== MIJOZGA TASDIQLASH =====
    if lang == "uz":
        confirm_text = (
            f"✅ <b>Chekingiz qabul qilindi!</b>\n\n"
            f"⏳ Operatorimiz chekni tekshirmoqda...\n\n"
            f"📋 <b>Buyurtmangiz:</b>\n"
            f"  • {amount} {currency}\n"
            f"  • Hamyon: <code>{wallet}</code>\n\n"
            f"🚀 Tekshirilgandan so'ng, <b>{amount} {currency}</b> hamyoningizga o'tkaziladi.\n\n"
            f"⏱ Odatda <b>15-30 daqiqa</b> ichida bajariladi.\n\n"
            f"📞 Savollar bo'lsa, aloqa: /help"
        )
    else:
        confirm_text = (
            f"✅ <b>Чек получен!</b>\n\n"
            f"⏳ Оператор проверяет ваш чек...\n\n"
            f"📋 <b>Ваш заказ:</b>\n"
            f"  • {amount} {currency}\n"
            f"  • Кошелёк: <code>{wallet}</code>\n\n"
            f"🚀 После проверки, <b>{amount} {currency}</b> будет отправлено на ваш кошелёк.\n\n"
            f"⏱ Обычно выполняется в течение <b>15-30 минут</b>.\n\n"
            f"📞 По вопросам: /help"
        )

    await update.message.reply_text(confirm_text, parse_mode="HTML", reply_markup=main_keyboard(lang))

    # State tozalash
    context.user_data.clear()
    return ConversationHandler.END


# ==================== TIL O'ZGARTIRISH ====================
async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_lang(user_id)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🇺🇿 O'zbek tili", callback_data="lang_uz"),
         InlineKeyboardButton("🇷🇺 Русский язык", callback_data="lang_ru")]
    ])

    if lang == "uz":
        text = "🌐 Tilni tanlang / Выберите язык:"
    else:
        text = "🌐 Выберите язык / Tilni tanlang:"

    await update.message.reply_text(text, reply_markup=keyboard)


async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "lang_uz":
        user_langs[user_id] = "uz"
        await query.edit_message_text("✅ Til o'zbekchaga o'zgartirildi!")
        await context.bot.send_message(user_id, "👇 Asosiy menyu:", reply_markup=main_keyboard("uz"))
    elif query.data == "lang_ru":
        user_langs[user_id] = "ru"
        await query.edit_message_text("✅ Язык изменён на русский!")
        await context.bot.send_message(user_id, "👇 Главное меню:", reply_markup=main_keyboard("ru"))


# ==================== YORDAM ====================
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_lang(user_id)

    if lang == "uz":
        text = (
            "📞 <b>Aloqa va yordam</b>\n\n"
            "Savollar yoki muammolar bo'lsa:\n"
            "👤 Operator bilan bog'laning\n\n"
            "⏱ Ish vaqti: <b>09:00 - 22:00</b>\n\n"
            "📌 <b>Buyurtma berish tartibi:</b>\n"
            "1️⃣ Valyutani tanlang\n"
            "2️⃣ Miqdorni kiriting\n"
            "3️⃣ Hamyon manzilingizni yuboring\n"
            "4️⃣ Karta raqamiga to'lov qiling\n"
            "5️⃣ To'lov chekini yuboring\n"
            "6️⃣ Cryptoni qabul qiling! ✅"
        )
    else:
        text = (
            "📞 <b>Контакты и помощь</b>\n\n"
            "По вопросам и проблемам:\n"
            "👤 Свяжитесь с оператором\n\n"
            "⏱ Рабочее время: <b>09:00 - 22:00</b>\n\n"
            "📌 <b>Как сделать заказ:</b>\n"
            "1️⃣ Выберите валюту\n"
            "2️⃣ Введите количество\n"
            "3️⃣ Отправьте адрес кошелька\n"
            "4️⃣ Оплатите на карту\n"
            "5️⃣ Отправьте чек об оплате\n"
            "6️⃣ Получите криптовалюту! ✅"
        )

    await update.message.reply_text(text, parse_mode="HTML", reply_markup=main_keyboard(lang))


# ==================== BEKOR QILISH ====================
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_lang(user_id)
    context.user_data.clear()

    if lang == "uz":
        text = "❌ Buyurtma bekor qilindi. Asosiy menyuga qaytdingiz."
    else:
        text = "❌ Заказ отменён. Вы вернулись в главное меню."

    await update.message.reply_text(text, reply_markup=main_keyboard(lang))
    return ConversationHandler.END


# ==================== NOMA'LUM XABAR ====================
async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_lang(user_id)

    if lang == "uz":
        text = "❓ Tushunarli emas. Iltimos, quyidagi tugmalardan foydalaning."
    else:
        text = "❓ Не понятно. Пожалуйста, используйте кнопки меню."

    await update.message.reply_text(text, reply_markup=main_keyboard(lang))


# ==================== MAIN ====================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Conversation handler
    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(
                filters.Regex(r"(BTC|Bitcoin|LTC|Litecoin|USDT|Купить|sotib olish)"),
                start_exchange
            )
        ],
        states={
            ENTER_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_amount)],
            ENTER_WALLET: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_wallet)],
            WAIT_RECEIPT: [
                MessageHandler(filters.PHOTO | filters.Document.ALL, receive_receipt),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_receipt),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            MessageHandler(filters.Regex(r"(Bekor|Отмена|❌)"), cancel),
        ],
    )

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.Regex(r"(kurslar|Joriy|курсы|Текущие|📊)"), show_rates))
    app.add_handler(MessageHandler(filters.Regex(r"(Til|Язык|🌐)"), change_language))
    app.add_handler(MessageHandler(filters.Regex(r"(Aloqa|Контакты|📞|help|Yordam|Помощь)"), help_command))
    app.add_handler(CallbackQueryHandler(set_language, pattern=r"^lang_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_message))

    print("✅ Bot ishga tushdi!")
    print("🚀 Polling boshlandi...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
