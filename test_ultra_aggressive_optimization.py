#!/usr/bin/env python3
"""
Teste ULTRA-AGRESSIVO para verificar se o algoritmo ELIMINA qualquer sobra significativa
Objetivo: Usar 99,9%+ do orçamento, deixar menos de R$ 50 de sobra
"""

def optimize_budget_consumption_ultra(budget, real_prices, base_quantities):
    """Algoritmo ULTRA AGRESSIVO - 4 FASES para eliminar QUALQUER sobra"""
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
    
    # Algoritmo de otimização de orçamento ULTRA AGRESSIVO para usar 100% do budget
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
    
    # FASE 2: Distribuir orçamento restante de forma ULTRA inteligente
    max_iterations = 500  # Muito mais iterações para garantir uso total
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
                
                # Limite dinâmico ULTRA AGRESSIVO para consumir TODO o orçamento SEM SOBRAS
                max_reasonable = min(
                    int(budget * 1.0 / price),  # SEM LIMITE PERCENTUAL - pode usar todo orçamento!
                    int(budget / price)  # Máximo possível baseado no orçamento total
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
    
    # FASE 3: FORÇA BRUTA TOTAL - ELIMINAR QUALQUER SOBRA (modo ultra agressivo)
    force_iterations = 0
    while remaining_budget > 0 and force_iterations < 10:  # Múltiplas tentativas
        force_iterations += 1
        
        # Ordenar itens por preço (do mais barato ao mais caro) para maximizar uso
        available_items_by_price = sorted(available_items, key=lambda x: x['price'])
        
        budget_consumed_this_round = False
        
        # Tentar usar TODO orçamento restante com QUALQUER item
        for item_data in available_items_by_price:
            if remaining_budget <= 0:
                break
                
            item = item_data['item'] 
            price = item_data['price']
            
            if price <= remaining_budget:
                # Adicionar MÁXIMO possível deste item
                max_qty_possible = int(remaining_budget / price)
                
                if max_qty_possible > 0:
                    if item in optimized_quantities:
                        optimized_quantities[item] += max_qty_possible
                    else:
                        optimized_quantities[item] = max_qty_possible
                    
                    remaining_budget -= max_qty_possible * price
                    budget_consumed_this_round = True
        
        # Se não conseguiu usar nada nesta rodada, parar
        if not budget_consumed_this_round:
            break
    
    # FASE 4: ÚLTIMA TENTATIVA - FORÇA TOTAL NO ITEM MAIS BARATO
    if remaining_budget > 0:
        cheapest_item = min(available_items, key=lambda x: x['price'])
        if cheapest_item['price'] <= remaining_budget:
            item = cheapest_item['item']
            price = cheapest_item['price'] 
            final_qty = int(remaining_budget / price)
            
            if final_qty > 0:
                if item in optimized_quantities:
                    optimized_quantities[item] += final_qty
                else:
                    optimized_quantities[item] = final_qty
                remaining_budget -= final_qty * price
    
    return optimized_quantities, remaining_budget

def test_ultra_aggressive_budget():
    """Testa se o algoritmo ULTRA agressivo elimina sobras significativas"""
    
    print("🚀 TESTE: ALGORITMO ULTRA-AGRESSIVO PARA ZERO SOBRAS")
    print("=" * 70)
    
    # Dados de teste baseados nos valores reais
    real_prices = {
        'headset_premium': 260.0,   # Preço real do CSV
        'adaptador_usb': 112.0,     # Preço mostrado no exemplo do usuário
        'mouse_gamer': 31.90,       # Preço real do CSV
        'teclado_mecanico': 90.0    # Preço real do CSV
    }
    
    # Quantidades base
    base_quantities = {
        'headset_premium': 5,
        'adaptador_usb': 10, 
        'mouse_gamer': 8,
        'teclado_mecanico': 6
    }
    
    budget = 50000  # Orçamento do usuário
    
    print(f"💰 ORÇAMENTO TESTE: R$ {budget:,.2f}")
    print(f"🎯 META: Sobra < R$ 50,00 (99,9%+ aproveitamento)")
    print("-" * 50)
    
    # Testar algoritmo ultra-agressivo
    optimized_qty, remaining = optimize_budget_consumption_ultra(budget, real_prices, base_quantities)
    
    if optimized_qty:
        total_cost = sum(qty * real_prices[item] for item, qty in optimized_qty.items())
        efficiency = (total_cost / budget) * 100
        
        print("✅ RESULTADO DO ALGORITMO ULTRA-AGRESSIVO:")
        print(f"   • Custo Total: R$ {total_cost:,.2f}")
        print(f"   • Orçamento: R$ {budget:,.2f}")
        print(f"   • Aproveitamento: {efficiency:.2f}%")
        print(f"   • Sobra: R$ {remaining:,.2f}")
        
        print(f"\n📦 QUANTIDADES ULTRA-OTIMIZADAS:")
        for item, qty in optimized_qty.items():
            item_name = item.replace('_premium', '').replace('_gamer', '').replace('_mecanico', '').replace('_usb', ' usb c').replace('_', ' ').strip().title()
            item_cost = qty * real_prices[item]
            print(f"   • {item_name}: {qty}x - R$ {item_cost:,.2f}")
        
        print(f"\n🎯 AVALIAÇÃO DA SOBRA:")
        if remaining < 10:
            print("🎉 PERFEITO! Sobra < R$ 10,00 - ORÇAMENTO TOTALMENTE CONSUMIDO!")
            status = "PERFEITO"
        elif remaining < 50:
            print("✅ EXCELENTE! Sobra < R$ 50,00 - Meta atingida!")
            status = "EXCELENTE"
        elif remaining < 100:
            print("⚠️ BOM! Sobra < R$ 100,00 - Aceitável")
            status = "BOM"
        else:
            print(f"❌ AINDA SOBRA MUITO! R$ {remaining:,.2f} - Precisa melhorar")
            status = "RUIM"
            
        print(f"\n🛒 COMANDOS FINAIS:")
        for item, qty in optimized_qty.items():
            item_name = item.replace('_premium', '').replace('_gamer', '').replace('_mecanico', '').replace('_usb', ' usb c').replace('_', ' ').strip().upper()
            print(f"🛒 COMPRE {qty} {item_name}")
        
        print(f"\n📊 RESULTADO:")
        if remaining < 50:
            print(f"✅ {status} - Sobra aceitável: R$ {remaining:.2f}")
            print("✅ ORÇAMENTO PRATICAMENTE 100% CONSUMIDO!")
        else:
            print(f"❌ {status} - Sobra excessiva: R$ {remaining:.2f}")
            print("⚠️ ALGORITMO PRECISA SER MAIS AGRESSIVO!")
        
        return remaining < 50  # Aprovar se sobra for menor que R$ 50
    
    else:
        print("❌ ERRO: Não foi possível otimizar o orçamento")
        return False

if __name__ == "__main__":
    success = test_ultra_aggressive_budget()
    print(f"\n🏁 TESTE {'APROVADO' if success else 'REPROVADO'}!")
    exit(0 if success else 1)
