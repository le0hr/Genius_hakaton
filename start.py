from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from test_data import GLOBAL_LOGS

start = Router()

def main_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🏠 Список об'єктів", callback_data="list_buildings"))
    builder.row(InlineKeyboardButton(text="🧠 Запропонувати стратегію", callback_data="propose_strategy"))
    builder.row(InlineKeyboardButton(text="⚙️ Налаштування міста", callback_data="settings"))
    builder.row(InlineKeyboardButton(text="📜 Лог дій", callback_data="view_logs"))
    return builder.as_markup()

@start.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 <b>Вітаємо у системі управління енергоефективністю!</b>\n\n"
        "Дані успішно завантажені.\n"
        "Оберіть дію нижче:",
        reply_markup=main_menu_kb(),
        parse_mode="HTML"
    )

@start.callback_query(F.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    # Видаляємо старе повідомлення (наприклад, меню налаштувань)
    try:
        await callback.message.delete()
    except:
        pass
    
    # Надсилаємо нове чисте повідомлення головного меню
    await callback.message.answer(
        "👋 <b>Головне меню системи:</b>",
        reply_markup=main_menu_kb(),
        parse_mode="HTML"
    )
    await callback.answer()