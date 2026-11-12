# Jarvis – assistente de voz com detecção de movimento

Comandos de voz em português para abrir o navegador/apps/sites e ativar a câmera
para detectar movimentos (caixas verdes + fotos salvas em `capturas/`).

## Instalação (Windows)
Recomendado **Python 3.11 ou 3.12** (o PyAudio ainda pode não ter pacote pronto para versões mais novas).
Dê dois cliques em `iniciar.bat` (cria o ambiente, instala tudo e roda) ou, no PowerShell:
```powershell
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
- Se `pip install PyAudio` falhar: `pip install pipwin` e depois `pipwin install pyaudio`, ou use Python 3.12.
- Permita o acesso ao microfone e à câmera em *Configurações > Privacidade e segurança*.
- A voz falada usa o SAPI5 do Windows; para voz em português instale o idioma em *Configurações > Hora e idioma > Voz*.
- O reconhecimento usa o serviço gratuito do Google (precisa de internet).
- Linux/macOS também funcionam (PyAudio precisa do PortAudio).

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
