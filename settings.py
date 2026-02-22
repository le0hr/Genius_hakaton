from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import test_data

settings_router = Router()

class EditSettings(StatesGroup):
    waiting_for_budget_val = State()
    waiting_for_totals_list = State()
    waiting_for_avg_cons = State()

@settings_router.callback_query(F.data == "settings")
async def settings_main_menu(event: types.CallbackQuery | types.Message, state: FSMContext):
    await state.clear()
    
    # Визначаємо, як відповісти (на кнопку чи на повідомлення)
    if isinstance(event, types.CallbackQuery):
        call_or_msg = event.message
    else:
        call_or_msg = event

    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="💰 Встановити бюджет", callback_data="edit_budget_val"))
    builder.row(types.InlineKeyboardButton(text="🏠 Кількість будинків", callback_data="edit_city_totals"))
    builder.row(types.InlineKeyboardButton(text="⚡️ Сер. споживання", callback_data="edit_avg_cons"))
    builder.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main"))
    
    text = (
        "⚙️ <b>Налаштування міста (за замовчуванням ТЗ)</b>\n\n"
        f"💰 <b>Річний бюджет:</b> {test_data.BUDGET[0]} у.о.\n"
        f"🏠 <b>Фонд:</b> {list(test_data.TOTAL_BUILDINGS.values())}\n"
        f"⚡️ <b>Споживання (міс):</b> {list(test_data.AVG_CONSUMPTION.values())}"
    )
    
    await call_or_msg.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")

# --- ОБРОБКА БЮДЖЕТУ ---
@settings_router.callback_query(F.data == "edit_budget_val")
async def ask_budget(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("💰 Введіть суму щорічного бюджету (наприклад, 150):")
    await state.set_state(EditSettings.waiting_for_budget_val)

@settings_router.message(EditSettings.waiting_for_budget_val)
async def process_budget(message: types.Message, state: FSMContext):
    try:
        val = float(message.text.replace(",", "."))
        test_data.BUDGET = [val] * 10
        await message.answer(f"✅ Бюджет встановлено: {val} у.о./рік")
        await settings_main_menu(message, state)
    except:
        await message.answer("❌ Введіть число.")

# --- ОБРОБКА СПОЖИВАННЯ ---
@settings_router.callback_query(F.data == "edit_avg_cons")
async def ask_avg_cons(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("⚡️ Введіть 3 числа місячного споживання через пробіл:")
    await state.set_state(EditSettings.waiting_for_avg_cons)

@settings_router.message(EditSettings.waiting_for_avg_cons)
async def process_avg_cons(message: types.Message, state: FSMContext):
    try:
        vals = [float(x) for x in message.text.replace(",", ".").split()]
        if len(vals) == 3:
            for i in range(3): test_data.AVG_CONSUMPTION[i] = vals[i]
            await message.answer("✅ Споживання оновлено!")
            await settings_main_menu(message, state)
    except:
        await message.answer("❌ Помилка формату.")

# --- ОБРОБКА КІЛЬКОСТІ БУДИНКІВ ---
@settings_router.callback_query(F.data == "edit_city_totals")
async def ask_totals(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("🏠 Введіть 3 числа кількості будинків:")
    await state.set_state(EditSettings.waiting_for_totals_list)

@settings_router.message(EditSettings.waiting_for_totals_list)
async def process_totals(message: types.Message, state: FSMContext):
    try:
        vals = [int(x) for x in message.text.split()]
        if len(vals) == 3:
            for i in range(3): test_data.TOTAL_BUILDINGS[i] = vals[i]
            await message.answer("✅ Фонд оновлено!")
            await settings_main_menu(message, state)
    except:
        await message.answer("❌ Введіть цілі числа.")