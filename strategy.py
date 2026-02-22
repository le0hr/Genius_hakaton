from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
import test_data

strategy_router = Router()

@strategy_router.callback_query(F.data == "propose_strategy")
async def strategy_menu(callback: types.CallbackQuery):
    # Якщо ми прийшли сюди з графіка (де є фото), краще видалити старе повідомлення
    # і надіслати чисте меню, щоб не виникало помилок редагування тексту в фото
    if callback.message.photo:
        try:
            await callback.message.delete()
        except:
            pass
        send_func = callback.message.answer
    else:
        send_func = callback.message.edit_text

    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="📉 Greedy vs Стандарт", callback_data="compare_greedy_base"))
    builder.row(types.InlineKeyboardButton(text="📈 DP vs Стандарт", callback_data="compare_dp_base"))
    builder.row(types.InlineKeyboardButton(text="⚖️ Greedy vs DP (Повне)", callback_data="stat_compare"))
    builder.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main"))
    
    text = (
        "🧠 <b>Оберіть режим аналізу стратегій:</b>\n\n"
        "Алгоритми порівнюють базове споживання міста з обраною моделлю оптимізації."
    )
    
    try:
        await send_func(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    except Exception:
        # На випадок, якщо edit_text не спрацював (наприклад, повідомлення вже видалене)
        await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    
    await callback.answer()