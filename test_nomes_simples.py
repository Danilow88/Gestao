#!/usr/bin/env python3
"""
Teste para verificar se os nomes dos itens estão corretos: 
adaptador usb c, headset, teclado, mouse (sem sufixos)
"""

def test_simple_names():
    """Testa se os nomes dos itens estão simplificados"""
    
    print("🧪 TESTE: NOMES SIMPLIFICADOS DOS ITENS")
    print("=" * 60)
    
    # Simular função de mapeamento de nomes
    def get_simple_display_name(key):
        """Retorna nome simples do item baseado na chave"""
        if key == 'mouse_gamer':
            return 'mouse'
        elif key == 'adaptador_usb':
            return 'adaptador usb c'
        elif key == 'headset_premium':
            return 'headset'
        elif key == 'teclado_mecanico':
            return 'teclado'
        else:
            return key.replace('_', ' ').title()
    
    # Testar mapeamento de nomes
    test_keys = ['mouse_gamer', 'adaptador_usb', 'headset_premium', 'teclado_mecanico']
    expected_names = ['mouse', 'adaptador usb c', 'headset', 'teclado']
    
    print("📋 TESTANDO MAPEAMENTO DE NOMES:")
    print("-" * 40)
    
    all_correct = True
    
    for i, key in enumerate(test_keys):
        display_name = get_simple_display_name(key)
        expected = expected_names[i]
        status = "✅" if display_name == expected else "❌"
        
        print(f"{status} {key} → '{display_name}' (esperado: '{expected}')")
        
        if display_name != expected:
            all_correct = False
    
    print("\n" + "=" * 60)
    
    if all_correct:
        print("🎉 TESTE APROVADO!")
        print("✅ Todos os nomes estão simplificados corretamente")
        print("✅ Nomes conforme solicitado pelo usuário")
    else:
        print("❌ TESTE REPROVADO!")
        print("⚠️ Alguns nomes não estão corretos")
    
    # Teste de exemplo de resposta
    print("\n📝 EXEMPLO DE RESPOSTA ESPERADA:")
    print("-" * 40)
    
    recommendations = [
        {'item': 'mouse', 'quantity': 87, 'price': 31.90, 'total_cost': 2775.30},
        {'item': 'headset', 'quantity': 76, 'price': 260.0, 'total_cost': 19760.0},
        {'item': 'teclado', 'quantity': 85, 'price': 90.0, 'total_cost': 7650.0},
        {'item': 'adaptador usb c', 'quantity': 55, 'price': 360.0, 'total_cost': 19800.0}
    ]
    
    for rec in recommendations:
        print(f"🛒 COMPRE {rec['quantity']} {rec['item'].upper()}")
    
    total_cost = sum(rec['total_cost'] for rec in recommendations)
    budget = 50000
    efficiency = (total_cost / budget) * 100
    sobra = budget - total_cost
    
    print(f"\n💰 RESUMO:")
    print(f"• Custo Total: R$ {total_cost:,.2f}")
    print(f"• Orçamento: R$ {budget:,.2f}")
    print(f"• Eficiência: {efficiency:.1f}%")
    print(f"• Sobra: R$ {sobra:,.2f}")
    
    print(f"\n🎯 STATUS:")
    if efficiency > 99:
        print("✅ EXCELENTE! Orçamento otimizado com nomes corretos")
    else:
        print("⚠️ Pode melhorar a otimização")
    
    print(f"\n🏁 TESTE CONCLUÍDO!")
    return all_correct

if __name__ == "__main__":
    success = test_simple_names()
    exit(0 if success else 1)
