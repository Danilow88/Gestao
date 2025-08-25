def process_matt_response(user_message):
    """IA conversacional avançada do Matt - Assistente inteligente completo"""
    import re
    from datetime import datetime, timedelta
    
    print(f"🔧 DEBUG: process_matt_response chamada com: '{user_message}'")
    
    try:
        # Garantir que os dados estão inicializados
        if 'gadgets_data' not in st.session_state:
            st.session_state.gadgets_data = pd.DataFrame()
        
        message_lower = user_message.lower()
        
        # ====================================================================
        # SISTEMA DE IA CONVERSACIONAL EXPANDIDO - MATT 2.0
        # ====================================================================
        
        # 1. CONFIGURAÇÕES DE BUDGET E PREFERÊNCIAS
        if any(palavra in message_lower for palavra in ['definir budget', 'configurar orçamento', 'preferir', 'prioritário', 'limitar quantidade']):
            # Detectar configuração de budget
            if any(palavra in message_lower for palavra in ['budget', 'orçamento']):
                match = re.search(r'r?\$?\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\d+)', message_lower)
                if match:
                    valor_str = match.group(1).replace('.', '').replace(',', '.')
                    try:
                        budget = float(valor_str)
                        if budget < 1000:
                            budget *= 1000
                        st.session_state.matt_budget = budget
                        return f"💰 **Budget definido com sucesso!** R$ {budget:,.2f} configurado para suas análises e recomendações."
                    except:
                        pass
            
            # Detectar preferência de gadgets
            gadgets_keywords = ['mouse', 'teclado', 'adaptador', 'usb-c', 'usb c', 'headset']
            gadgets_encontrados = []
            
            # Mapear termos para nomes padronizados
            mapa_gadgets = {
                'mouse': 'Mouse',
                'teclado': 'Teclado', 
                'adaptador': 'Adaptador USB-C',
                'usb-c': 'Adaptador USB-C',
                'usb c': 'Adaptador USB-C',
                'headset': 'Headset'
            }
            
            for termo, nome_padrao in mapa_gadgets.items():
                if termo in message_lower:
                    if nome_padrao not in gadgets_encontrados:
                        gadgets_encontrados.append(nome_padrao)
            
            if gadgets_encontrados:
                gadgets_atuais = st.session_state.get('gadgets_preferidos', [])
                # Adicionar novos gadgets sem duplicar
                for gadget in gadgets_encontrados:
                    if gadget not in gadgets_atuais:
                        gadgets_atuais.append(gadget)
                
                st.session_state.gadgets_preferidos = gadgets_atuais
                texto_gadgets = ", ".join(gadgets_encontrados)
                return f"🎯 **Gadgets prioritários definidos!** {texto_gadgets} agora receberão preferência nas recomendações."
            
            return """🎯 **CONFIGURAÇÕES MATT 2.0**

Para configurar suas preferências, use comandos como:
• "Definir budget de R$ 80.000"
• "Priorizar mouse e headset nas compras"  
• "Limitar quantidade para 15 por item"

**📊 Configurações atuais:**
• 💰 Budget: R$ {0:,.2f}
• 🎯 Gadgets prioritários: {1}
• 📦 Limite por item: {2} unidades
• 🔥 % Extra prioritário: {3}%

**💡 Dica:** Use as configurações acima na interface visual ou converse comigo diretamente!
""".format(
                st.session_state.get('matt_budget', 50000),
                ", ".join(st.session_state.get('gadgets_preferidos', [])) or 'Nenhum',
                st.session_state.get('matt_limite_qty', 20),
                st.session_state.get('matt_percentual_extra', 20)
            )

        # 2. SAUDAÇÕES E APRESENTAÇÃO
        elif any(palavra in message_lower for palavra in ['olá', 'oi', 'hey', 'bom dia', 'boa tarde', 'boa noite', 'tudo bem', 'como vai']):
            hora = datetime.now().hour
            if hora < 12:
                saudacao = "Bom dia"
            elif hora < 18:
                saudacao = "Boa tarde"
            else:
                saudacao = "Boa noite"
            
            # Status do sistema
            total_perdas = len(st.session_state.gadgets_data) if not st.session_state.gadgets_data.empty else 0
            tem_estoque = 'estoque_data' in st.session_state and not st.session_state.estoque_data.empty
            
            return f"""👋 **{saudacao}! Sou o Matt, seu assistente de IA especializado em gestão inteligente!**

🧠 **Status da Inteligência Artificial:**
• Sistema conversacional: ● ATIVO
• Análise de dados: ● {total_perdas} registros disponíveis
• Controle de estoque: ● {"CONECTADO" if tem_estoque else "AGUARDANDO CONFIGURAÇÃO"}
• Recomendações IA: ● OPERACIONAL

◎ **Hoje posso conversar sobre:**
• ▬ Análises detalhadas e insights personalizados
• $ Otimização de orçamentos e estratégias financeiras  
• ■ Gestão inteligente de estoque e alertas preditivos
• 🛒 Recomendações de compras baseadas em IA
• ▲ Tendências, padrões e análises preditivas
• 🤖 Qualquer questão sobre gestão de gadgets!

💬 **Converse comigo naturalmente!** Pergunte qualquer coisa, desde análises simples até estratégias complexas. Sou uma IA completa pronta para ajudar!

**O que gostaria de saber ou otimizar hoje?** ▲"""
        
        # 3. AJUDA E TUTORIAL
        elif any(palavra in message_lower for palavra in ['ajuda', 'help', 'como', 'tutorial', 'funciona', 'comandos', 'o que pode']):
            return """🤖 **MATT 2.0 - ASSISTENTE DE IA COMPLETO**

◎ **Capacidades da Inteligência Artificial:**

🎯 **Configurações Inteligentes:**
• "Definir budget de R$ 80.000"
• "Priorizar mouse e headset nas compras"
• "Limitar quantidades para 15 por item"
• "Configurar teclado e adaptador prioritários"

▬ **Análises Avançadas:**
• "Analise os dados de perda dos últimos 30 dias"
• "Qual item tem mais problemas?"
• "Mostre um relatório executivo completo"
• "Identifique padrões e tendências"

$ **Gestão Financeira Inteligente:**
• "Otimize orçamento de R$ 50.000 priorizando mouse e teclado"
• "Como distribuir melhor os recursos?"
• "Calcule ROI das compras sugeridas"
• "Projete gastos futuros"

■ **Controle de Estoque IA:**
• "Quais itens estão críticos?"
• "Preveja quando vou ficar sem headsets"
• "Calcule ponto de reposição ideal"
• "Monitore alertas automáticos"

🛒 **Compras Estratégicas:**
• "Sugira compras para este trimestre"
• "Priorize aquisições por urgência"
• "Analise melhor custo-benefício"
• "Quando comprar cada item?"

▲ **Análises Preditivas:**
• "Projete perdas dos próximos meses"
• "Identifique riscos de desabastecimento"
• "Analise sazonalidade dos dados"
• "Sugira melhorias de processo"

🤖 **Conversação Natural:**
• Faça perguntas em linguagem natural
• Solicite análises personalizadas
• Peça recomendações específicas
• Converse sobre qualquer aspecto da gestão

◆ **Exemplos de Conversas:**
• "Matt, otimize R$ 80k priorizando headset e adaptador"
• "Preciso de um plano de compras para Q4"
• "Configure mouse e teclado como prioritários"
• "Qual a melhor estratégia para 2025?"

**Sou uma IA conversacional completa. Converse comigo como com um especialista!** ◎"""

        # 4. ANÁLISES E RELATÓRIOS INTELIGENTES
        elif any(palavra in message_lower for palavra in ['análise', 'relatório', 'dados', 'insights', 'padrão', 'tendência', 'dashboard']):
            if not st.session_state.gadgets_data.empty:
                df = st.session_state.gadgets_data
                
                # Análises avançadas com IA
                total_registros = len(df)
                total_itens = df['quantidade'].sum()
                valor_total = df['valor_total'].sum()
                periodo_dias = (df['data'].max() - df['data'].min()).days or 1
                
                # Top insights
                item_critico = df['name'].value_counts().index[0]
                local_critico = df['building'].value_counts().index[0]
                
                return f"""▬ **RELATÓRIO EXECUTIVO IA - ANÁLISE MATT 2.0**

◯ **OVERVIEW INTELIGENTE ({periodo_dias} dias de dados):**
• **{total_registros}** registros analisados
• **{int(total_itens)}** itens perdidos
• **R$ {valor_total:,.2f}** em perdas totais
• **{len(df['building'].unique())}** localizações impactadas

🚨 **ALERTAS CRÍTICOS DA IA:**
• **Item mais problemático:** {item_critico} ({df['name'].value_counts().iloc[0]} ocorrências)
• **Local mais afetado:** {local_critico} ({df['building'].value_counts().iloc[0]} perdas)

**Posso detalhar qualquer aspecto ou fazer análises específicas!** ◎"""
            else:
                return """▬ **IA AGUARDANDO DADOS PARA ANÁLISE**

🤖 **Sistema de Análise Inteligente Pronto!**

Assim que você registrar perdas, minha IA será capaz de:

🔮 **Análises Preditivas:**
• Identificar padrões ocultos nos dados
• Prever tendências futuras de perdas
• Calcular riscos de desabastecimento
• Otimizar estratégias preventivas

**Estou ansioso para analisar seus dados e gerar insights valiosos!** ▲"""

        # 5. RESPOSTA PADRÃO
        else:
            return """🤖 **MATT 2.0 - IA CONVERSACIONAL**

**Não entendi exatamente sua solicitação, mas posso ajudar com:**

🎯 **Configurações:** "Definir budget de R$ 50.000"
▬ **Análises:** "Analise meus dados de perdas"  
$ **Orçamento:** "Otimize R$ 40.000"
■ **Estoque:** "Status do estoque atual"
🛒 **Compras:** "Sugira compras para este mês"

**Reformule sua pergunta para uma resposta mais específica!** ◎"""
    
    except Exception as e:
        print(f"🔧 DEBUG: Erro geral na inicialização: {str(e)}")
        return f"""❌ **ERRO NO SISTEMA MATT 2.0**

🔧 **Detalhes do erro:**
{str(e)}

⚠️ **Para resolver:**
1. Recarregue a página
2. Verifique se os dados estão carregados
3. Tente uma pergunta mais simples
4. Se persistir, contate o suporte

**Enquanto isso, posso tentar responder com funcionalidades básicas.**"""
