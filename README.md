# Jarvis – assistente de voz com detecção de movimento

Comandos de voz em português para abrir o navegador/apps/sites e ativar a câmera
para detectar movimentos (caixas verdes + fotos salvas em `capturas/`).

## Instalação
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
- **PyAudio** precisa de PortAudio: Linux `sudo apt install portaudio19-dev`, macOS `brew install portaudio`.
- O reconhecimento usa o serviço gratuito do Google (precisa de internet).

## Comandos (diga "Jarvis, ...")
| Fala | Ação |
|---|---|
| abrir navegador / abrir youtube / abrir gmail | abre no navegador |
| pesquisar gatos fofos | busca no Google |
| abrir calculadora / bloco de notas / terminal | abre o app |
| **ativar câmera** / iniciar detecção de movimento | liga a câmera e detecta movimento |
| **parar câmera** (ou tecla `q` na janela) | desliga a câmera |
| que horas são / ajuda | informações |
| sair / tchau | encerra |

Para aceitar frases sem "Jarvis", ponha `PALAVRA_DE_ATIVACAO = ""` em `main.py`.
Novos comandos: edite `jarvis/comandos.py`. Sensibilidade: `area_minima` em `jarvis/movimento.py`.

Teste do interpretador sem hardware: `python tests_comandos.py`.
