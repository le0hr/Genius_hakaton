import test_data
from aiogram import Router, types, F
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

# Використовуємо прямі посилання на об'єкти в RAM
from test_data import CITY_STATE_DETAILED, TOTAL_BUILDINGS, CAT_NAMES, GLOBAL_LOGS

buildings_router = Router() 

class ManageCity(StatesGroup):
    waiting_for_count = State()

def sync_to_disk():
    """Записує поточний стан RAM у файл test_data.py"""
    with open("test_data.py", "w", encoding="utf-8") as f:
        f.write(f"CITY_STATE_DETAILED = {repr(test_data.CITY_STATE_DETAILED)}\n")
        f.write(f"TOTAL_BUILDINGS = {repr(test_data.TOTAL_BUILDINGS)}\n")
        f.write(f"CAT_NAMES = {repr(test_data.CAT_NAMES)}\n")
        f.write(f"GLOBAL_LOGS = {repr(test_data.GLOBAL_LOGS)}\n")

@buildings_router.callback_query(F.data == "list_buildings")
async def categories_menu(event: types.CallbackQuery | types.Message, state: FSMContext):
    await state.clear()
    
    builder = InlineKeyboardBuilder()
    # Ітеруємося строго по довжині списку CAT_NAMES, щоб не вийти за межі
    for idx in range(len(test_data.CAT_NAMES)):
        name = test_data.CAT_NAMES[idx]
        count = test_data.CITY_STATE_DETAILED[idx]["count"]
        total = test_data.TOTAL_BUILDINGS[idx]
        percent = (count / total) * 100 if total > 0 else 0
        
        builder.row(InlineKeyboardButton(
            text=f"{name} ({count}/{total}) - {percent:.1f}%", 
            callback_data=f"manage_cat_{idx}")
        )
    
    builder.row(InlineKeyboardButton(text="⬅️ Назад до меню", callback_data="back_to_main"))
    
    text = "📂 <b>Управління категоріями об'єктів</b>\n\nОберіть категорію:"

    if isinstance(event, types.CallbackQuery):
        await event.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
        await event.answer()
    else:
        await event.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")

@buildings_router.callback_query(F.data.startswith("manage_cat_"))
async def category_setter(callback: types.CallbackQuery, state: FSMContext):
    cat_idx = int(callback.data.split("_")[-1])
    
    if cat_idx >= len(test_data.CITY_STATE_DETAILED):
        await callback.answer("❌ Категорію не знайдено", show_alert=True)
        return

    data = test_data.CITY_STATE_DETAILED[cat_idx]
    total = test_data.TOTAL_BUILDINGS[cat_idx]
    progress = int((data['count'] / total) * 100) if total > 0 else 0
    
    text = (
        f"⚙️ <b>{test_data.CAT_NAMES[cat_idx]}</b>\n"
        f"📊 <b>Прогрес:</b> {progress}%\n\n"
        f"Модернізовано: <b>{data['count']}</b> з {total}"
    )
    
    builder = InlineKeyboardBuilder()
    
    # --- ДОДАЄМО КНОПКИ ШВИДКОЇ ЗМІНИ ---
    # Формат callback_data: delta_{індекс}_{значення}
    
    builder.row(InlineKeyboardButton(text="⌨️ Ввести число вручну", callback_data=f"manual_input_{cat_idx}"))
    builder.row(InlineKeyboardButton(text="⬅️ Назад до списку", callback_data="list_buildings"))
    
    # Використовуємо edit_text для миттєвого оновлення інтерфейсу
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()

@buildings_router.callback_query(F.data.startswith("delta_"))
async def apply_delta(callback: types.CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    cat_idx, delta = int(parts[1]), int(parts[2])
    
    if cat_idx >= len(test_data.CITY_STATE_DETAILED):
        await callback.answer("Помилка індексу", show_alert=True)
        return

    # Зміна в RAM
    old_val = test_data.CITY_STATE_DETAILED[cat_idx]['count']
    limit = test_data.TOTAL_BUILDINGS[cat_idx]
    new_val = min(old_val + delta, limit)
    
    if old_val != new_val:
        test_data.CITY_STATE_DETAILED[cat_idx]['count'] = new_val
        test_data.GLOBAL_LOGS.append(f"🔄 {test_data.CAT_NAMES[cat_idx]}: +{delta} (стало {new_val})")
        # sync_to_disk() # Розкоментуйте для автозбереження у файл
    
    await category_setter(callback, state)

@buildings_router.callback_query(F.data.startswith("manual_input_"))
async def start_manual_input(callback: types.CallbackQuery, state: FSMContext):
    cat_idx = int(callback.data.split("_")[-1])
    await state.set_state(ManageCity.waiting_for_count)
    await state.update_data(current_cat_idx=cat_idx)
    
    await callback.message.answer(
        f"⌨️ Введіть нову кількість для <b>{test_data.CAT_NAMES[cat_idx]}</b>\n"
        f"(від 0 до {test_data.TOTAL_BUILDINGS[cat_idx]}):",
        parse_mode="HTML"
    )
    await callback.answer()

@buildings_router.message(ManageCity.waiting_for_count)
async def process_manual_count(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    cat_idx = user_data.get("current_cat_idx")
    
    if message.text and message.text.isdigit():
        new_val = int(message.text)
        limit = test_data.TOTAL_BUILDINGS[cat_idx]
        
        if 0 <= new_val <= limit:
            # Зміна в RAM
            test_data.CITY_STATE_DETAILED[cat_idx]['count'] = new_val
            test_data.GLOBAL_LOGS.append(f"⌨️ {test_data.CAT_NAMES[cat_idx]}: Ручне оновлення -> {new_val}")
            # sync_to_disk() # Розкоментуйте для автозбереження у файл
            
            await message.answer(f"✅ Дані оновлено!")
            await categories_menu(message, state) 
        else:
            await message.answer(f"❌ Число має бути від 0 до {limit}.")
    else:
        await message.answer("❌ Будь ласка, введіть ціле число.")