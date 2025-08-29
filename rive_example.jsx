import React, { useEffect, useRef, useState } from 'react';
import { Rive } from '@rive-app/canvas';

const RiveExample = () => {
  const canvasRef = useRef(null);
  const riveRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentAnimation, setCurrentAnimation] = useState('idle');

  useEffect(() => {
    if (canvasRef.current) {
      // Exemplo de animação Rive (você pode substituir por um arquivo .rive real)
      const rive = new Rive({
        src: 'https://cdn.rive.app/animations/vehicles.riv', // Exemplo de animação pública
        canvas: canvasRef.current,
        autoplay: true,
        onLoad: () => {
          console.log('Rive carregado com sucesso!');
          riveRef.current = rive;
          
          // Listar animações disponíveis
          const animations = rive.animationNames;
          console.log('Animações disponíveis:', animations);
          
          if (animations.length > 0) {
            setCurrentAnimation(animations[0]);
          }
        },
        onError: (error) => {
          console.error('Erro ao carregar Rive:', error);
        }
      });
    }

    return () => {
      if (riveRef.current) {
        riveRef.current.stop();
      }
    };
  }, []);

  const playAnimation = (animationName) => {
    if (riveRef.current) {
      riveRef.current.play(animationName);
      setCurrentAnimation(animationName);
      setIsPlaying(true);
    }
  };

  const pauseAnimation = () => {
    if (riveRef.current) {
      riveRef.current.pause();
      setIsPlaying(false);
    }
  };

  const stopAnimation = () => {
    if (riveRef.current) {
      riveRef.current.stop();
      setIsPlaying(false);
    }
  };

  return (
    <div style={{ 
      padding: '2rem', 
      fontFamily: 'Arial, sans-serif',
      maxWidth: '800px',
      margin: '0 auto'
    }}>
      <h1 style={{ color: '#333', textAlign: 'center' }}>🎨 Exemplo Rive com React</h1>
      
      <div style={{ 
        textAlign: 'center', 
        marginBottom: '2rem',
        padding: '1rem',
        backgroundColor: '#f5f5f5',
        borderRadius: '8px'
      }}>
        <p>Este é um exemplo de como usar o Rive em um projeto React.</p>
        <p>Status: <strong>{isPlaying ? 'Reproduzindo' : 'Pausado'}</strong></p>
        <p>Animação atual: <strong>{currentAnimation}</strong></p>
      </div>

      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        marginBottom: '2rem' 
      }}>
        <canvas
          ref={canvasRef}
          style={{
            width: '400px',
            height: '300px',
            border: '2px solid #ddd',
            borderRadius: '8px',
            backgroundColor: '#fff'
          }}
        />
      </div>

      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        gap: '1rem',
        flexWrap: 'wrap'
      }}>
        <button
          onClick={() => playAnimation('idle')}
          style={{
            padding: '0.5rem 1rem',
            backgroundColor: '#4CAF50',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          ▶️ Play Idle
        </button>
        
        <button
          onClick={() => playAnimation('drive')}
          style={{
            padding: '0.5rem 1rem',
            backgroundColor: '#2196F3',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          🚗 Drive
        </button>
        
        <button
          onClick={pauseAnimation}
          style={{
            padding: '0.5rem 1rem',
            backgroundColor: '#FF9800',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          ⏸️ Pause
        </button>
        
        <button
          onClick={stopAnimation}
          style={{
            padding: '0.5rem 1rem',
            backgroundColor: '#F44336',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          ⏹️ Stop
        </button>
      </div>

      <div style={{ 
        marginTop: '2rem',
        padding: '1rem',
        backgroundColor: '#e3f2fd',
        borderRadius: '8px'
      }}>
        <h3>📚 Como usar:</h3>
        <ol style={{ textAlign: 'left' }}>
          <li>Instale os pacotes: <code>npm install @rive-app/canvas @rive-app/react-canvas</code></li>
          <li>Importe o Rive: <code>import { Rive } from '@rive-app/canvas'</code></li>
          <li>Crie um canvas e inicialize o Rive com um arquivo .rive</li>
          <li>Use os métodos play(), pause(), stop() para controlar as animações</li>
          <li>Adicione event listeners para onLoad, onError, etc.</li>
        </ol>
      </div>

      <div style={{ 
        marginTop: '2rem',
        padding: '1rem',
        backgroundColor: '#fff3e0',
        borderRadius: '8px'
      }}>
        <h3>🔧 Funcionalidades principais:</h3>
        <ul style={{ textAlign: 'left' }}>
          <li><strong>Autoplay:</strong> Reproduz automaticamente ao carregar</li>
          <li><strong>Controle de estado:</strong> Play, pause, stop</li>
          <li><strong>Múltiplas animações:</strong> Troque entre diferentes animações</li>
          <li><strong>Eventos:</strong> onLoad, onError, onStateChange</li>
          <li><strong>Responsivo:</strong> Funciona em qualquer tamanho de tela</li>
        </ul>
      </div>
    </div>
  );
};

export default RiveExample;
