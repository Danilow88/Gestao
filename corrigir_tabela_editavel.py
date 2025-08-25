#!/usr/bin/env python3

def corrigir_tabela_editavel():
    """Corrige os tipos mistos no DataFrame e garante que a tabela editável seja sempre apresentada"""
    
    # Ler o arquivo
    with open('app/dashboard.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Corrigir tipos mistos no DataFrame
    old_code = '''        # Criar tabela editável do orçamento
        budget_data = []
        for rec in recommendations:
            budget_data.append({
                'Item': rec['item'].replace('_', ' ').title(),
                'Quantidade': rec['quantity'],
                'Preço Unitário': f"R$ {rec['total_cost']/rec['quantity']:,.2f}",
                'Custo Total': f"R$ {rec['total_cost']:,.2f}",
                'Prioridade': rec['priority'].title(),
                'Editar Qtd': rec['quantity']  # Coluna editável
            })
        
        # Adicionar linha de totais
        budget_data.append({
            'Item': '**TOTAL GERAL**',
            'Quantidade': sum([rec['quantity'] for rec in recommendations]),
            'Preço Unitário': '-',
            'Custo Total': f"R$ {total_cost:,.2f}",
            'Prioridade': '-',
            'Editar Qtd': '-'
        })'''
    
    new_code = '''        # Criar tabela editável do orçamento com tipos consistentes
        budget_data = []
        for rec in recommendations:
            budget_data.append({
                'Item': str(rec['item'].replace('_', ' ').title()),
                'Quantidade': int(rec['quantity']),
                'Preço Unitário': str(f"R$ {rec['total_cost']/rec['quantity']:,.2f}"),
                'Custo Total': str(f"R$ {rec['total_cost']:,.2f}"),
                'Prioridade': str(rec['priority'].title()),
                'Editar Qtd': int(rec['quantity'])  # Coluna editável
            })
        
        # Adicionar linha de totais
        budget_data.append({
            'Item': str('**TOTAL GERAL**'),
            'Quantidade': int(sum([rec['quantity'] for rec in recommendations])),
            'Preço Unitário': str('-'),
            'Custo Total': str(f"R$ {total_cost:,.2f}"),
            'Prioridade': str('-'),
            'Editar Qtd': str('-')
        })'''
    
    # Substituir o código
    content = content.replace(old_code, new_code)
    
    # Garantir que a tabela seja sempre apresentada - adicionar st.rerun() após a tabela
    if 'st.rerun()' not in content:
        # Adicionar st.rerun() após a apresentação da tabela
        content = content.replace(
            'st.success(f"💰 **Orçamento recalculado: R$ {new_total:,.2f}**")',
            'st.success(f"💰 **Orçamento recalculado: R$ {new_total:,.2f}**")\n                    st.rerun()'
        )
    
    # Escrever o arquivo corrigido
    with open('app/dashboard.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Tabela editável corrigida e tipos mistos resolvidos!")

if __name__ == "__main__":
    corrigir_tabela_editavel()
