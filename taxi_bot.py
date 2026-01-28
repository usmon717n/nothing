import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler
from datetime import datetime
import json
import os

# Logging sozlamalari
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Admin ID
ADMIN_ID = 6723737087

# Ma'lumotlar bazasi fayli
DB_FILE = "orders.json"
DRIVERS_FILE = "drivers.json"

# Conversation holatlari - YANGI TARTIB
(MAIN_MENU, CLIENT_DRIVER, GET_ROUTE, GET_PASSENGERS, 
 GET_PRICE, GET_PHONE, DRIVER_INFO) = range(7)

# Ma'lumotlar bazasini yuklash/saqlash funksiyalari
def load_orders():
    """Zakazlarni yuklash"""
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Zakazlarni yuklashda xatolik: {e}")
    return []

def save_order(order):
    """Zakazni saqlash"""
    try:
        orders = load_orders()
        orders.append(order)
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(orders, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ Zakaz saqlandi: {order.get('user_id')}")
        return True
    except Exception as e:
        logger.error(f"❌ Zakazni saqlashda xatolik: {e}")
        return False

def load_drivers():
    """Shofyorlarni yuklash"""
    try:
        if os.path.exists(DRIVERS_FILE):
            with open(DRIVERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Shofyorlarni yuklashda xatolik: {e}")
    return []

def save_driver(driver):
    """Shofyorni saqlash"""
    try:
        drivers = load_drivers()
        drivers.append(driver)
        with open(DRIVERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(drivers, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ Shofyor saqlandi: {driver.get('user_id')}")
        return True
    except Exception as e:
        logger.error(f"❌ Shofyorni saqlashda xatolik: {e}")
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start komandasi"""
    # User data tozalash
    context.user_data.clear()
    
    keyboard = [
        [KeyboardButton("📝 Zakaz berish")],
        [KeyboardButton("📊 Mening zakazlarim"), KeyboardButton("ℹ️ Yordam")],
        [KeyboardButton("📞 Bog'lanish"), KeyboardButton("⭐ Narxlar")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    user = update.message.from_user
    await update.message.reply_text(
        f"Assalomu alaykum, {user.first_name}! 👋\n\n"
        f"🚖 Taksi botiga xush kelibsiz!\n\n"
        f"Bu bot orqali siz:\n"
        f"✅ Tez va oson zakaz berishingiz\n"
        f"✅ Shofyor sifatida ro'yxatdan o'tishingiz\n"
        f"✅ O'z zakazlaringizni kuzatishingiz mumkin\n\n"
        f"Kerakli bo'limni tanlang:",
        reply_markup=reply_markup
    )
    return MAIN_MENU

async def zakaz_berish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Zakaz berish tugmasi bosilganda"""
    keyboard = [
        [KeyboardButton("👤 Klient"), KeyboardButton("🚗 Shofyor")],
        [KeyboardButton("🔙 Ortga")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "Siz klient yoki shofyorsiz?",
        reply_markup=reply_markup
    )
    return CLIENT_DRIVER

# ============ KLIENT BO'LIMI ============

async def klient_tanlandi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Klient tugmasi bosilganda"""
    context.user_data['role'] = 'Klient'
    logger.info("👤 Klient tanlandi")
    
    await update.message.reply_text(
        "🚕 Klient bo'limi\n\n"
        "📝 Yo'nalish va vaqtni quyidagi ko'rinishda yozing:\n\n"
        "📌 Namuna: Namangandan Qarshiga bugun soat 15:00 da ketish kerak\n\n"
        "Iltimos, ma'lumotni kiriting:",
        reply_markup=ReplyKeyboardRemove()
    )
    return GET_ROUTE

async def get_route(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yo'nalish ma'lumotini olish"""
    route_info = update.message.text
    context.user_data['route'] = route_info
    logger.info(f"📍 Yo'nalish: {route_info[:50]}")
    
    keyboard = [
        [KeyboardButton("1 kishi"), KeyboardButton("2 kishi"), KeyboardButton("3 kishi")],
        [KeyboardButton("4 kishi"), KeyboardButton("5+ kishi")],
        [KeyboardButton("🔙 Ortga")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "👥 Necha kishi yo'lga chiqasiz?",
        reply_markup=reply_markup
    )
    return GET_PASSENGERS

async def get_passengers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yo'lovchilar sonini olish"""
    passengers = update.message.text
    context.user_data['passengers'] = passengers
    logger.info(f"👥 Yo'lovchilar: {passengers}")
    
    keyboard = [
        [KeyboardButton("🔙 Ortga")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "💰 Narx taklifingiz bormi?\n\n"
        "Masalan: 150 000 so'm\n\n"
        "Yoki 'Kelishiladi' deb yozing:",
        reply_markup=reply_markup
    )
    return GET_PRICE

async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Narx taklifini olish"""
    price = update.message.text
    context.user_data['price'] = price
    logger.info(f"💰 Narx: {price}")
    
    keyboard = [
        [KeyboardButton("📱 Telefon raqamni ulashish", request_contact=True)],
        [KeyboardButton("🔙 Ortga")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "📱 Iltimos, telefon raqamingizni ulashing:",
        reply_markup=reply_markup
    )
    return GET_PHONE

# ============ SHOFYOR BO'LIMI ============

async def shofyor_tanlandi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shofyor tugmasi bosilganda"""
    context.user_data['role'] = 'Shofyor'
    logger.info("🚗 Shofyor tanlandi")
    
    await update.message.reply_text(
        "🚗 Shofyor bo'limi\n\n"
        "Quyidagi ma'lumotlarni kiriting:\n\n"
        "📝 Namuna:\n"
        "Ism: Sardor Karimov\n"
        "Mashina: Nexia 3\n"
        "Rang: Oq\n"
        "Raqam: 01 A 123 BC\n"
        "Yo'nalish: Toshkent-Namangan",
        reply_markup=ReplyKeyboardRemove()
    )
    return DRIVER_INFO

async def get_driver_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shofyor ma'lumotlarini olish"""
    driver_info = update.message.text
    context.user_data['driver_info'] = driver_info
    logger.info(f"🚗 Shofyor ma'lumoti: {driver_info[:50]}")
    
    keyboard = [
        [KeyboardButton("📱 Telefon raqamni ulashish", request_contact=True)],
        [KeyboardButton("🔙 Ortga")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "📱 Iltimos, telefon raqamingizni ulashing:",
        reply_markup=reply_markup
    )
    return GET_PHONE

# ============ TELEFON OLISH (Klient va Shofyor uchun) ============

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Telefon raqamni olish va ma'lumotlarni adminga yuborish"""
    
    if not update.message.contact:
        await update.message.reply_text(
            "❌ Iltimos, 📱 'Telefon raqamni ulashish' tugmasini bosing!"
        )
        return GET_PHONE
    
    try:
        # Telefon olish
        phone = update.message.contact.phone_number
        user = update.message.from_user
        role = context.user_data.get('role', 'Noma\'lum')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        logger.info(f"📱 Telefon olindi: {phone} | Rol: {role}")
        
        # Rol bo'yicha ajratish
        if role == 'Klient':
            # Klient ma'lumotlarini to'plash
            route = context.user_data.get('route', 'Kiritilmagan')
            passengers = context.user_data.get('passengers', 'Kiritilmagan')
            price = context.user_data.get('price', 'Kelishiladi')
            
            # Zakazni saqlash
            order = {
                'timestamp': timestamp,
                'order_id': len(load_orders()) + 1,
                'user_id': user.id,
                'name': f"{user.first_name} {user.last_name or ''}",
                'username': user.username or 'Yo\'q',
                'phone': phone,
                'role': role,
                'route': route,
                'passengers': passengers,
                'price': price,
                'status': 'Kutilmoqda'
            }
            
            saved = save_order(order)
            
            # Admin uchun xabar
            admin_message = (
                f"🆕 YANGI ZAKAZ!\n"
                f"{'='*35}\n\n"
                f"📝 Zakaz #: {order['order_id']}\n"
                f"👤 Ism: {user.first_name} {user.last_name or ''}\n"
                f"🆔 Username: @{user.username or 'Yo\'q'}\n"
                f"📱 Telefon: {phone}\n\n"
                f"📍 Yo'nalish:\n{route}\n\n"
                f"👥 Yo'lovchilar: {passengers}\n"
                f"💰 Narx taklifi: {price}\n\n"
                f"🕐 Vaqt: {timestamp}\n"
                f"🆔 User ID: {user.id}\n"
                f"{'='*35}"
            )
            
            # Inline tugmalar
            admin_keyboard = [
                [
                    InlineKeyboardButton("✅ Qabul", callback_data=f"accept_{user.id}"),
                    InlineKeyboardButton("❌ Rad", callback_data=f"reject_{user.id}")
                ]
            ]
            admin_reply_markup = InlineKeyboardMarkup(admin_keyboard)
            
            # User uchun xabar
            success_message = (
                "✅ Zakazingiz muvaffaqiyatli qabul qilindi!\n\n"
                f"📝 Zakaz raqami: #{order['order_id']}\n"
                f"📍 Yo'nalish: {route[:40]}...\n"
                f"👥 Yo'lovchilar: {passengers}\n"
                f"💰 Narx: {price}\n"
                f"🕐 Vaqt: {timestamp}\n\n"
                "Tez orada operator siz bilan bog'lanadi.\n"
                "Rahmat! 🙏"
            )
            
        elif role == 'Shofyor':
            # Shofyor ma'lumotlarini to'plash
            driver_info = context.user_data.get('driver_info', 'Kiritilmagan')
            
            # Shofyorni saqlash
            driver = {
                'timestamp': timestamp,
                'user_id': user.id,
                'name': f"{user.first_name} {user.last_name or ''}",
                'username': user.username or 'Yo\'q',
                'phone': phone,
                'info': driver_info,
                'status': 'Faol'
            }
            
            saved = save_driver(driver)
            
            # Admin uchun xabar
            admin_message = (
                f"🚗 YANGI SHOFYOR!\n"
                f"{'='*35}\n\n"
                f"👤 Ism: {user.first_name} {user.last_name or ''}\n"
                f"🆔 Username: @{user.username or 'Yo\'q'}\n"
                f"📱 Telefon: {phone}\n\n"
                f"📝 Ma'lumotlar:\n{driver_info}\n\n"
                f"🕐 Vaqt: {timestamp}\n"
                f"🆔 User ID: {user.id}\n"
                f"{'='*35}"
            )
            
            admin_reply_markup = None
            
            # User uchun xabar
            success_message = (
                "✅ Siz shofyor sifatida muvaffaqiyatli ro'yxatdan o'tdingiz!\n\n"
                f"📱 Telefon: {phone}\n"
                f"🕐 Vaqt: {timestamp}\n\n"
                "Yangi zakazlar mavjud bo'lganda sizga xabar beramiz.\n"
                "Rahmat! 🙏"
            )
        else:
            raise Exception(f"Noma'lum rol: {role}")
        
        # Adminga xabar yuborish
        logger.info("📤 Adminga xabar yuborilmoqda...")
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_message,
            reply_markup=admin_reply_markup
        )
        logger.info("✅ Admin xabari yuborildi!")
        
        # Foydalanuvchiga tasdiqlash
        keyboard = [
            [KeyboardButton("📝 Zakaz berish")],
            [KeyboardButton("📊 Mening zakazlarim"), KeyboardButton("ℹ️ Yordam")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            success_message,
            reply_markup=reply_markup
        )
        logger.info("✅ User tasdiqlash xabari yuborildi!")
        
    except Exception as e:
        logger.error(f"❌ XATOLIK: {e}", exc_info=True)
        await update.message.reply_text(
            f"❌ Xatolik yuz berdi!\n\n"
            f"Xatolik: {str(e)}\n\n"
            "Iltimos, /start ni bosib qaytadan urinib ko'ring."
        )
    
    # User data tozalash
    context.user_data.clear()
    return MAIN_MENU

# ============ BOSHQA FUNKSIYALAR ============

async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchining zakazlarini ko'rsatish"""
    user_id = update.message.from_user.id
    orders = load_orders()
    user_orders = [o for o in orders if o.get('user_id') == user_id]
    
    if not user_orders:
        await update.message.reply_text(
            "📊 Sizda hozircha zakazlar yo'q.\n\n"
            "Yangi zakaz berish uchun '📝 Zakaz berish' tugmasini bosing."
        )
        return MAIN_MENU
    
    message = "📊 SIZNING ZAKAZLARINGIZ\n" + "="*35 + "\n\n"
    
    for order in user_orders[-5:]:  # Oxirgi 5 ta zakaz
        message += (
            f"📝 Zakaz #{order.get('order_id', 'N/A')}\n"
            f"📍 {order.get('route', 'N/A')[:40]}...\n"
            f"👥 {order.get('passengers', 'N/A')}\n"
            f"💰 {order.get('price', 'N/A')}\n"
            f"🕐 {order.get('timestamp', 'N/A')}\n"
            f"📊 {order.get('status', 'Kutilmoqda')}\n"
            f"{'-'*35}\n\n"
        )
    
    await update.message.reply_text(message)
    return MAIN_MENU

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yordam bo'limi"""
    help_text = (
        "ℹ️ YORDAM BO'LIMI\n"
        f"{'='*35}\n\n"
        "📝 ZAKAZ BERISH:\n"
        "1. 'Zakaz berish' tugmasini bosing\n"
        "2. Klient yoki Shofyorni tanlang\n"
        "3. Ma'lumotlarni ketma-ket kiriting\n"
        "4. Telefon raqamni ulashing\n\n"
        "📊 MENING ZAKAZLARIM:\n"
        "Oxirgi 5 ta zakazingizni ko'ring\n\n"
        "📞 BOG'LANISH:\n"
        "Qo'shimcha savollar uchun\n\n"
        "⭐ NARXLAR:\n"
        "Taxminiy narxlarni ko'ring\n\n"
        "🔄 Qayta boshlash: /start"
    )
    
    await update.message.reply_text(help_text)
    return MAIN_MENU

async def contact_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bog'lanish ma'lumotlari"""
    contact_text = (
        "📞 BOG'LANISH\n"
        f"{'='*35}\n\n"
        "☎️ Telefon: +998 XX XXX XX XX\n"
        "📧 Email: info@taxibot.uz\n"
        "🌐 Website: www.taxibot.uz\n\n"
        "⏰ Ish vaqti: 24/7\n\n"
        "Doimo xizmatdamiz! 🚖"
    )
    
    await update.message.reply_text(contact_text)
    return MAIN_MENU

async def prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Narxlar ro'yxati"""
    prices_text = (
        "⭐ TAXMINIY NARXLAR\n"
        f"{'='*35}\n\n"
        "Toshkent → Namangan: 150 000 so'm\n"
        "Toshkent → Andijon: 180 000 so'm\n"
        "Toshkent → Farg'ona: 160 000 so'm\n"
        "Toshkent → Samarqand: 120 000 so'm\n"
        "Toshkent → Buxoro: 150 000 so'm\n"
        "Namangan → Qarshi: 200 000 so'm\n"
        "Namangan → Toshkent: 150 000 so'm\n\n"
        "💡 Narxlar taxminiy.\n"
        "Aniq narx uchun zakaz bering."
    )
    
    await update.message.reply_text(prices_text)
    return MAIN_MENU

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin inline button callback"""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("accept_"):
        await query.edit_message_text(
            text=query.message.text + "\n\n✅ QABUL QILINDI!"
        )
    elif query.data.startswith("reject_"):
        await query.edit_message_text(
            text=query.message.text + "\n\n❌ RAD ETILDI!"
        )

async def ortga(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ortga qaytish"""
    context.user_data.clear()
    return await start(update, context)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bekor qilish"""
    context.user_data.clear()
    await update.message.reply_text(
        "Bekor qilindi. /start ni bosing.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def main():
    """Botni ishga tushirish"""
    TOKEN = "8412060276:AAFxeEs6sQo5sJNQtebLRJ8Fbi1QfR-Iyfs"
    
    application = Application.builder().token(TOKEN).build()
    
    # Conversation handler
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            MessageHandler(filters.Regex('^📝 Zakaz berish$'), zakaz_berish)
        ],
        states={
            MAIN_MENU: [
                MessageHandler(filters.Regex('^📝 Zakaz berish$'), zakaz_berish),
                MessageHandler(filters.Regex('^📊 Mening zakazlarim$'), my_orders),
                MessageHandler(filters.Regex('^ℹ️ Yordam$'), help_command),
                MessageHandler(filters.Regex('^📞 Bog\'lanish$'), contact_info),
                MessageHandler(filters.Regex('^⭐ Narxlar$'), prices),
            ],
            CLIENT_DRIVER: [
                MessageHandler(filters.Regex('^👤 Klient$'), klient_tanlandi),
                MessageHandler(filters.Regex('^🚗 Shofyor$'), shofyor_tanlandi),
                MessageHandler(filters.Regex('^🔙 Ortga$'), ortga),
            ],
            GET_ROUTE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_route),
                MessageHandler(filters.Regex('^🔙 Ortga$'), zakaz_berish),
            ],
            GET_PASSENGERS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_passengers),
                MessageHandler(filters.Regex('^🔙 Ortga$'), ortga),
            ],
            GET_PRICE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_price),
                MessageHandler(filters.Regex('^🔙 Ortga$'), ortga),
            ],
            DRIVER_INFO: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_driver_info),
                MessageHandler(filters.Regex('^🔙 Ortga$'), zakaz_berish),
            ],
            GET_PHONE: [
                MessageHandler(filters.CONTACT, get_phone),
                MessageHandler(filters.Regex('^🔙 Ortga$'), ortga),
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            CommandHandler('start', start)
        ],
    )
    
    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(button_callback))
    
    logger.info("="*50)
    logger.info("🚖 TAKSI BOT ISHGA TUSHDI!")
    logger.info("="*50)
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()