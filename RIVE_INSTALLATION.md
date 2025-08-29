# 🎨 Instalação e Configuração do Rive

## ✅ Status da Instalação

O Rive foi instalado com sucesso no seu projeto! Os seguintes pacotes estão disponíveis:

- **@rive-app/canvas**: v2.31.2 - Runtime principal do Rive
- **@rive-app/react-canvas**: v4.23.1 - Wrapper React para o Rive

## 🚀 Como Usar

### 1. Importação Básica

```javascript
import { Rive } from '@rive-app/canvas';
```

### 2. Inicialização Simples

```javascript
const rive = new Rive({
  src: 'caminho/para/arquivo.rive',
  canvas: canvasElement,
  autoplay: true,
  onLoad: () => console.log('Rive carregado!'),
  onError: (error) => console.error('Erro:', error)
});
```

### 3. Controles de Animação

```javascript
// Reproduzir animação
rive.play('nome_da_animacao');

// Pausar
rive.pause();

// Parar
rive.stop();

// Verificar se está reproduzindo
rive.isPlaying;

// Listar animações disponíveis
rive.animationNames;
```

## 📁 Arquivos de Exemplo

### `test_rive.html`
- Teste básico do Rive funcionando
- Verifica se os pacotes estão instalados corretamente
- Interface visual para testar funcionalidades

### `rive_example.jsx`
- Exemplo completo em React
- Demonstra controles de animação
- Interface de usuário funcional

## 🔧 Configurações Avançadas

### Opções de Inicialização

```javascript
const rive = new Rive({
  src: 'arquivo.rive',
  canvas: canvas,
  autoplay: true,
  loop: true,
  fit: 'cover', // 'contain', 'cover', 'fill', 'none'
  alignment: 'center', // 'top-left', 'top', 'top-right', etc.
  onLoad: () => {},
  onError: (error) => {},
  onStateChange: (event) => {},
  onPlay: () => {},
  onPause: () => {},
  onStop: () => {},
  onLoop: () => {}
});
```

### Manipulação de Estados

```javascript
// Verificar estados disponíveis
rive.stateMachineNames;

// Ativar máquina de estados
rive.fire('nome_do_estado');

// Definir entrada numérica
rive.scrub('nome_entrada', valor);
```

## 🎯 Casos de Uso Comuns

### 1. Loading Animations
```javascript
const loadingRive = new Rive({
  src: 'loading.rive',
  canvas: loadingCanvas,
  autoplay: true,
  loop: true
});
```

### 2. Interactive Animations
```javascript
const interactiveRive = new Rive({
  src: 'interactive.rive',
  canvas: interactiveCanvas,
  autoplay: false,
  onStateChange: (event) => {
    if (event.data === 'clicked') {
      // Responder ao clique
    }
  }
});
```

### 3. Responsive Animations
```javascript
const responsiveRive = new Rive({
  src: 'responsive.rive',
  canvas: responsiveCanvas,
  fit: 'cover',
  alignment: 'center'
});

// Redimensionar quando a janela mudar
window.addEventListener('resize', () => {
  responsiveRive.resizeDrawingSurfaceToCanvas();
});
```

## 🛠️ Ferramentas de Desenvolvimento

### Rive Editor (Desktop)
Para criar animações .rive, baixe o Rive Editor:
- **Windows**: https://rive.app/download
- **macOS**: https://rive.app/download  
- **Linux**: https://rive.app/download

### Recursos Online
- **Documentação**: https://rive.app/docs
- **Exemplos**: https://rive.app/examples
- **Comunidade**: https://rive.app/community

## 📱 Suporte a Plataformas

- ✅ **Web** (Chrome, Firefox, Safari, Edge)
- ✅ **React** (via @rive-app/react-canvas)
- ✅ **React Native** (via rive-react-native)
- ✅ **Vue.js** (via @rive-app/vue)
- ✅ **Angular** (via ng-rive)
- ✅ **Flutter** (via rive_flutter)

## 🚨 Solução de Problemas

### Erro: "Module not found"
```bash
npm install @rive-app/canvas @rive-app/react-canvas
```

### Erro: "Canvas not supported"
- Verifique se o navegador suporta Canvas
- Use fallback para navegadores antigos

### Erro: "File not found"
- Verifique o caminho do arquivo .rive
- Use caminhos absolutos ou URLs completas

### Performance Lenta
- Otimize o arquivo .rive (reduza complexidade)
- Use `fit: 'contain'` para melhor performance
- Considere usar `rive-canvas-lite` para dispositivos móveis

## 🎉 Próximos Passos

1. **Teste** o arquivo `test_rive.html` no navegador
2. **Explore** o exemplo React em `rive_example.jsx`
3. **Crie** suas próprias animações no Rive Editor
4. **Integre** o Rive no seu projeto finance-vibes

## 📞 Suporte

Se encontrar problemas:
1. Verifique a documentação oficial: https://rive.app/docs
2. Consulte a comunidade: https://rive.app/community
3. Abra uma issue no GitHub do Rive

---

**Rive instalado com sucesso! 🎨✨**
