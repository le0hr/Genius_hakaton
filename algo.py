import numpy as np

def greedy_optimization(measures_eff, base_consumption, costs, budget_years):
    """
    Жадібний алгоритм: щороку купує заходи з найкращим показником Економія/Ціна.
    """
    years = 10
    current_cons = list(base_consumption)
    wallet = 0
    # Початкова точка (Рік 0) - сума споживання до початку модернізації
    history = [sum(current_cons)]
    
    # Список доступних дій: 3 типи будівель * 5 заходів = 15 дій
    potential_actions = []
    for b_idx in range(len(base_consumption)):
        for m_idx in range(len(measures_eff)):
            potential_actions.append({
                'b_idx': b_idx, 'm_idx': m_idx,
                'cost': costs[m_idx], 'eff': measures_eff[m_idx]
            })

    for year in range(years):
        wallet += budget_years[year]
        years_left = years - year
        
        while True:
            best_action = None
            best_val = -1
            
            for action in potential_actions:
                if wallet >= action['cost']:
                    # Прогнозована економія до кінця 10-річного періоду
                    gain = current_cons[action['b_idx']] * action['eff'] * years_left
                    efficiency = gain / action['cost']
                    if efficiency > best_val:
                        best_val = efficiency
                        best_action = action
            
            if best_action:
                wallet -= best_action['cost']
                current_cons[best_action['b_idx']] *= (1 - best_action['eff'])
                potential_actions.remove(best_action)
            else:
                break
        history.append(sum(current_cons))
        
    return history

def dynamic_optimization(measures_eff, base_consumption, costs, budget_years):
    """
    Оптимальне програмування (Bitmask DP):
    Мінімізує сумарне споживання за 10 років, суворо дотримуючись бюджету.
    """
    years = 10
    num_buildings = len(base_consumption)
    num_measures = len(measures_eff)
    total_slots = num_buildings * num_measures 
    num_states = 1 << total_slots  # 2^15 станів

    # 1. Попередній розрахунок ціни та споживання для кожного стану (маски)
    mask_yearly_cons = np.zeros(num_states)
    mask_cost = np.zeros(num_states)
    
    for mask in range(num_states):
        c_cost, c_total_cons = 0.0, 0.0
        for b_idx in range(num_buildings):
            building_final_cons = base_consumption[b_idx]
            for m_idx in range(num_measures):
                if (mask >> (b_idx * num_measures + m_idx)) & 1:
                    c_cost += costs[m_idx]
                    building_final_cons *= (1 - measures_eff[m_idx])
            c_total_cons += building_final_cons
        mask_cost[mask], mask_yearly_cons[mask] = c_cost, c_total_cons

    # dp[year][mask] = мінімальне накопичене споживання
    dp = np.full((years + 1, num_states), float('inf'))
    parent = np.full((years + 1, num_states), -1, dtype=int)
    
    dp[0][0] = 0
    cumulative_budget = np.cumsum(budget_years)

    for y in range(1, years + 1):
        limit = cumulative_budget[y-1]
        
        # Крок А: Перехід з минулого року (стан не змінився)
        for mask in range(num_states):
            if dp[y-1][mask] != float('inf'):
                val = dp[y-1][mask] + mask_yearly_cons[mask]
                if val < dp[y][mask]:
                    dp[y][mask] = val
                    parent[y][mask] = mask

        # Крок Б: Оновлення всередині року (купівля нових заходів)
        # Використовуємо логіку рюкзака, щоб за один рік можна було купити декілька речей
        for j in range(total_slots):
            for mask in range(num_states):
                if (mask >> j) & 1:
                    prev_mask = mask ^ (1 << j)
                    # ГАРАНТІЯ БЮДЖЕТУ: сумарна вартість маски не може перевищити ліміт
                    if mask_cost[mask] <= limit and dp[y][prev_mask] != float('inf'):
                        # Розраховуємо різницю споживання при додаванні нового заходу
                        new_val = dp[y][prev_mask] - mask_yearly_cons[prev_mask] + mask_yearly_cons[mask]
                        if new_val < dp[y][mask]:
                            dp[y][mask] = new_val
                            # parent залишаємо той самий, що в Кроці А, 
                            # щоб знати, з якого стану ми ПРИЙШЛИ в цей рік.

    # 2. Відновлення історії споживання по роках
    best_final_state = np.argmin(dp[years])
    history = []
    curr = best_final_state
    for y in range(years, 0, -1):
        history.append(mask_yearly_cons[curr])
        curr = parent[y][curr]
    
    history.append(sum(base_consumption)) # Рік 0
    return history[::-1]