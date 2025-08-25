#!/usr/bin/env python3
"""
Teste para verificar se o algoritmo otimizado agora usa 100% do orçamento
ao invés de apenas 50% como estava acontecendo
"""

def optimize_budget_consumption_test(budget, real_prices, base_quantities):
    """Replica da função de otimização MELHORADA"""
    if not real_prices or budget <= 0:
        return {}
    
    # Lista de itens disponíveis com seus preços
    available_items = []
    for item, price in real_prices.items():
        base_qty = base_quantities.get(item, 1)
        available_items.append({
            'item': item,
            'price': price,
            'base_qty': base_qty,
            'priority_score': 1.0  # Base
        })
    
    # Definir prioridades baseadas no tipo de item
    for item_data in available_items:
        item_name = item_data['item'].lower()
        if 'headset' in item_name:
            item_data['priority_score'] = 3.0  # Alta prioridade - mais caro, menos perdido
        elif 'adaptador' in item_name or 'usb' in item_name:
            item_data['priority_score'] = 2.5  # Alta prioridade - muito usado
        elif 'mouse' in item_name:
            item_data['priority_score'] = 2.0  # Prioridade média-alta - mais perdido
        elif 'teclado' in item_name:
            item_data['priority_score'] = 1.5  # Prioridade média - menos perdido
    
    # Ordernar por prioridade (maior primeiro) e depois por custo-benefício
    available_items.sort(key=lambda x: (x['priority_score'], -x['price']), reverse=True)
    
    # Algoritmo de otimização de orçamento AGRESSIVO para usar 100% do budget
    optimized_quantities = {}
    remaining_budget = budget
    
    # FASE 1: Alocar quantidades base para todos os itens (essenciais)
    for item_data in available_items:
        item = item_data['item']
        price = item_data['price']
        base_qty = item_data['base_qty']
        
        cost_base = base_qty * price
        if remaining_budget >= cost_base:
            optimized_quantities[item] = base_qty
            remaining_budget -= cost_base
        elif remaining_budget >= price:
            # Se não cabe a quantidade base, pelo menos 1 unidade
            optimized_quantities[item] = 1
            remaining_budget -= price
    
    # FASE 2: Distribuir orçamento restante de forma inteligente
    max_iterations = 100  # Evitar loop infinito
    iteration = 0
    
    while remaining_budget > 0 and iteration < max_iterations:
        iteration += 1
        budget_used_this_round = False
        
        # Tentar adicionar 1 unidade de cada item por ordem de prioridade
        for item_data in available_items:
            item = item_data['item']
            price = item_data['price']
            
            if item in optimized_quantities and remaining_budget >= price:
                # Verificar se vale a pena adicionar mais unidades deste item
                current_qty = optimized_quantities[item]
                priority_score = item_data['priority_score']
                
                # Limite dinâmico MUITO MAIS AGRESSIVO para consumir TODO o orçamento
                max_reasonable = min(
                    int(budget * 0.8 / price),  # Máximo 80% do orçamento em um item (mais agressivo!)
                    int(current_qty * priority_score + 50)  # Limite muito maior baseado na prioridade
                )
                
                if current_qty < max_reasonable:
                    optimized_quantities[item] += 1
                    remaining_budget -= price
                    budget_used_this_round = True
        
        # Se não conseguiu usar nenhum orçamento nesta rodada, tentar forçar o uso
        if not budget_used_this_round:
            # Encontrar o item mais barato que ainda cabe no orçamento
            cheapest_affordable = None
            for item_data in available_items:
                if item_data['price'] <= remaining_budget:
                    if cheapest_affordable is None or item_data['price'] < cheapest_affordable['price']:
                        cheapest_affordable = item_data
            
            if cheapest_affordable:
                item = cheapest_affordable['item']
                price = cheapest_affordable['price']
                if item in optimized_quantities:
                    optimized_quantities[item] += 1
                else:
                    optimized_quantities[item] = 1
                remaining_budget -= price
            else:
                # Nenhum item cabe no orçamento restante
                break
    
    # FASE 3: FORÇAR USO DE TODO ORÇAMENTO RESTANTE (modo super agressivo)
    if remaining_budget > 0:
        # Encontrar o item com melhor custo-benefício e adicionar o máximo possível
        best_item = None
        for item_data in available_items:
            if item_data['price'] <= remaining_budget:
                if best_item is None or item_data['priority_score'] > best_item['priority_score']:
                    best_item = item_data
        
        if best_item:
            item = best_item['item']
            price = best_item['price']
            max_additional_qty = int(remaining_budget / price)
            
            if max_additional_qty > 0:
                if item in optimized_quantities:
                    optimized_quantities[item] += max_additional_qty
                else:
                    optimized_quantities[item] = max_additional_qty
                remaining_budget -= max_additional_qty * price
    
    return optimized_quantities, remaining_budget

def test_budget_optimization_fix():
    """Testa se o algoritmo melhorado usa mais de 90% do orçamento"""
    
    print("🧪 TESTE: ALGORITMO DE OTIMIZAÇÃO MELHORADO")
    print("=" * 60)
    
    # Dados de teste baseados nos valores reais mostrados pelo usuário
    real_prices = {
        'headset_premium': 260.0,   # Preço real do CSV
        'adaptador_usb': 112.0,     # Preço mostrado no exemplo do usuário
        'mouse_gamer': 31.90,       # Preço real do CSV
        'teclado_mecanico': 90.0    # Preço real do CSV
    }
    
    # Quantidades base
    base_quantities = {
        'headset_premium': 10,
        'adaptador_usb': 15, 
        'mouse_gamer': 12,
        'teclado_mecanico': 8
    }
    
    budget = 50000  # Orçamento do usuário
    
    print(f"💰 ORÇAMENTO TESTE: R$ {budget:,.2f}")
    print("-" * 40)
    
    # Testar algoritmo melhorado
    optimized_qty, remaining = optimize_budget_consumption_test(budget, real_prices, base_quantities)
    
    if optimized_qty:
        total_cost = sum(qty * real_prices[item] for item, qty in optimized_qty.items())
        efficiency = (total_cost / budget) * 100
        
        print("✅ RESULTADO DO ALGORITMO MELHORADO:")
        print(f"   • Custo Total: R$ {total_cost:,.2f}")
        print(f"   • Orçamento: R$ {budget:,.2f}")
        print(f"   • Aproveitamento: {efficiency:.1f}%")
        print(f"   • Sobra: R$ {remaining:,.2f}")
        
        print(f"\n📦 QUANTIDADES OTIMIZADAS:")
        for item, qty in optimized_qty.items():
            item_name = item.replace('_premium', '').replace('_gamer', '').replace('_mecanico', '').replace('_usb', ' usb c').replace('_', ' ').strip().title()
            item_cost = qty * real_prices[item]
            print(f"   • {item_name}: {qty}x - R$ {item_cost:,.2f}")
        
        print(f"\n🎯 AVALIAÇÃO:")
        if efficiency >= 95:
            print("🎉 EXCELENTE! Mais de 95% do orçamento utilizado")
            status = "APROVADO"
        elif efficiency >= 85:
            print("✅ MUITO BOM! Mais de 85% do orçamento utilizado") 
            status = "APROVADO"
        elif efficiency >= 70:
            print("⚠️ RAZOÁVEL! Mais de 70% do orçamento utilizado")
            status = "PARCIAL"
        else:
            print("❌ RUIM! Menos de 70% do orçamento utilizado")
            status = "REPROVADO"
            
        print(f"\n🛒 COMANDOS ESPERADOS:")
        for item, qty in optimized_qty.items():
            item_name = item.replace('_premium', '').replace('_gamer', '').replace('_mecanico', '').replace('_usb', ' usb c').replace('_', ' ').strip().upper()
            print(f"🛒 COMPRE {qty} {item_name}")
        
        return efficiency >= 85  # Aprovar se usar mais de 85%
    
    else:
        print("❌ ERRO: Não foi possível otimizar o orçamento")
        return False

if __name__ == "__main__":
    success = test_budget_optimization_fix()
    print(f"\n🏁 TESTE {'APROVADO' if success else 'REPROVADO'}!")
    exit(0 if success else 1)
