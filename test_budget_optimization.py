#!/usr/bin/env python3
"""
Teste para verificar se a otimização de orçamento consome TODO o budget disponível
SEM deixar sobras e SEM usar quantidades mínimas fixas
"""

def optimize_budget_consumption_test(budget, real_prices, base_quantities):
    """Replica da função de otimização para teste"""
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
    
    # Algoritmo de otimização de orçamento
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
                
                # Limite dinâmico baseado na prioridade e orçamento restante
                max_reasonable = min(
                    int(budget * 0.4 / price),  # Máximo 40% do orçamento em um item
                    int(current_qty * priority_score + 5)  # Baseado na prioridade
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
    
    return optimized_quantities, remaining_budget

def test_budget_optimization():
    """Testa se o sistema usa TODO o orçamento disponível"""
    
    print("🧪 TESTE: OTIMIZAÇÃO DE ORÇAMENTO - USO TOTAL SEM SOBRAS")
    print("=" * 70)
    
    # Dados de teste baseados em valores reais do CSV
    real_prices = {
        'mouse_gamer': 31.90,
        'headset_premium': 260.00,
        'teclado_mecanico': 90.00,
        'adaptador_usb': 360.00
    }
    
    # Quantidades base baseadas em perdas (sem mínimo de 5)
    base_quantities = {
        'mouse_gamer': 3,      # Baseado em perdas reais
        'headset_premium': 2,  # Menos perdido
        'teclado_mecanico': 4, # Perdas médias
        'adaptador_usb': 5     # Muito usado
    }
    
    # Testes com diferentes orçamentos
    budgets_to_test = [1000, 5000, 10000, 25000, 50000]
    
    for budget in budgets_to_test:
        print(f"\n📊 TESTANDO COM ORÇAMENTO: R$ {budget:,.2f}")
        print("-" * 50)
        
        # ANTES (sistema antigo - mínimo de 5)
        print("❌ SISTEMA ANTIGO (mínimo 5x):")
        old_quantities = {key: 5 for key in real_prices.keys()}
        old_total_cost = sum(qty * real_prices[item] for item, qty in old_quantities.items())
        old_sobra = budget - old_total_cost
        print(f"   • Custo: R$ {old_total_cost:,.2f}")
        print(f"   • Sobra: R$ {old_sobra:,.2f}")
        print(f"   • Eficiência: {(old_total_cost/budget)*100:.1f}%")
        
        if old_total_cost > budget:
            print(f"   • ⚠️ ORÇAMENTO INSUFICIENTE")
            continue
        
        # AGORA (sistema otimizado)
        print("\n✅ SISTEMA OTIMIZADO:")
        optimized_qty, remaining = optimize_budget_consumption_test(budget, real_prices, base_quantities)
        
        if optimized_qty:
            total_cost = sum(qty * real_prices[item] for item, qty in optimized_qty.items())
            efficiency = (total_cost / budget) * 100
            
            print(f"   • Custo: R$ {total_cost:,.2f}")
            print(f"   • Sobra: R$ {remaining:,.2f}")
            print(f"   • Eficiência: {efficiency:.1f}%")
            
            print(f"\n   📦 QUANTIDADES OTIMIZADAS:")
            for item, qty in optimized_qty.items():
                item_name = item.replace('_', ' ').title()
                item_cost = qty * real_prices[item]
                print(f"   • {item_name}: {qty}x - R$ {item_cost:,.2f}")
            
            # Comparação
            improvement = total_cost - old_total_cost
            if improvement > 0:
                print(f"\n   🎯 MELHORIA: +R$ {improvement:,.2f} de compras")
                print(f"   🎯 SOBRA REDUZIDA: R$ {old_sobra - remaining:,.2f}")
            
            if remaining <= min(real_prices.values()):
                print(f"   ✅ ÓTIMO! Sobra menor que item mais barato")
            
        else:
            print(f"   • ❌ Orçamento insuficiente para otimização")
    
    print(f"\n" + "=" * 70)
    print("🎉 CONCLUSÃO DO TESTE:")
    
    # Teste específico de eficiência
    budget_test = 50000
    optimized_qty, remaining = optimize_budget_consumption_test(budget_test, real_prices, base_quantities)
    
    if optimized_qty:
        total_cost = sum(qty * real_prices[item] for item, qty in optimized_qty.items())
        efficiency = (total_cost / budget_test) * 100
        
        print(f"✅ ORÇAMENTO R$ {budget_test:,.2f} - EFICIÊNCIA {efficiency:.1f}%")
        print(f"✅ SOBRA: R$ {remaining:,.2f} ({(remaining/budget_test)*100:.1f}% do orçamento)")
        
        if efficiency > 95:
            print("🎯 EXCELENTE! Mais de 95% do orçamento utilizado")
        elif efficiency > 90:
            print("✅ MUITO BOM! Mais de 90% do orçamento utilizado") 
        else:
            print("⚠️ PODE MELHORAR: Menos de 90% do orçamento utilizado")
            
        print("\n🛒 RECOMENDAÇÕES FINAIS:")
        for item, qty in sorted(optimized_qty.items()):
            item_name = item.replace('_', ' ').title()
            print(f"🛒 COMPRE {qty} {item_name.upper()}")
        
        return efficiency > 90  # Considera sucesso se usa mais de 90% do orçamento
    
    return False

if __name__ == "__main__":
    success = test_budget_optimization()
    print(f"\n🏁 TESTE {'APROVADO' if success else 'REPROVADO'}!")
    exit(0 if success else 1)
