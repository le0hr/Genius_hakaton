import io
import matplotlib.pyplot as plt
from aiogram import Router, types, F
import test_data
import algo 
import asyncio

statistic_router = Router()

@statistic_router.callback_query(F.data.in_(["stat_compare", "compare_greedy_base", "compare_dp_base"]))
async def show_statistics(callback: types.CallbackQuery):
    mode = callback.data
    wait_msg = await callback.message.answer("⏳ Йде розрахунок...")

    base_cons_array = [test_data.TOTAL_BUILDINGS[i] * test_data.AVG_CONSUMPTION[i] * 12 for i in range(3)]
    
    # Використовуємо thread для важких розрахунків
    h_greedy = await asyncio.to_thread(algo.greedy_optimization, test_data.MEASURES, base_cons_array, test_data.COSTS, test_data.BUDGET)
    h_dp = await asyncio.to_thread(algo.dynamic_optimization, test_data.MEASURES, base_cons_array, test_data.COSTS, test_data.BUDGET)

    plt.figure(figsize=(10, 6))
    
    # ПРАВИЛЬНА ВІСЬ X: створюємо стільки років, скільки є точок у результаті (0...10)
    years = list(range(len(h_greedy))) 

    if mode == "compare_greedy_base":
        no_action = [h_greedy[0]] * len(years)
        plt.plot(years, no_action, label="Без заходів", color='gray', linestyle='--')
        plt.plot(years, h_greedy, label="Greedy (Поточна)", color='red', marker='o')
    
    elif mode == "compare_dp_base":
        no_action = [h_dp[0]] * len(years)
        plt.plot(years, no_action, label="Без заходів", color='gray', linestyle='--')
        plt.plot(years, h_dp, label="DP (Оптимальна)", color='green', marker='o')

    else: # stat_compare
        plt.plot(years, h_greedy, label="Greedy (Швидка)", color='red', linestyle='--')
        plt.plot(years, h_dp, label="DP (Оптимальна)", color='green', linewidth=2)

    plt.title("Прогноз енергоспоживання (10 років)")
    plt.xlabel("Рік")
    plt.ylabel("кВт-год / рік")
    plt.grid(True, alpha=0.3)
    plt.legend()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    await wait_msg.delete()
    await callback.message.answer_photo(types.BufferedInputFile(buf.read(), filename="chart.png"))