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
| abrir navegador / youtube / gmail / spotify / discord / word / excel / calculadora / vs code | abre o programa ou site |
| abrir pasta downloads / documentos / imagens | abre a pasta |
| fechar spotify / fechar chrome / fechar word | fecha o programa (ele ainda pergunta se quer salvar) |
| pesquisar gatos fofos | busca no Google |
| pesquisar música relaxante no youtube | busca no YouTube |
| aumentar volume / diminuir volume / silenciar | controla o som |
| pausar música / continuar / próxima música / música anterior | controla a mídia |
| minimizar tudo / tirar print | mostra a área de trabalho / captura a tela |
| bloquear computador | bloqueia o Windows |
| desligar computador / reiniciar computador | agenda para 30 s; **cancelar desligamento** desfaz |
| **ativar câmera** / iniciar detecção de movimento | liga a câmera e detecta movimento |
| **contar dedos** | liga a câmera e conta os dedos que você mostra (até 2 mãos) |
| **quantos dedos estou mostrando** | responde por voz o que está vendo |
| **contar rostos** / **contar pessoas** / **contar objetos** | conta rostos, pessoas ou objetos (copo, celular, livro...) |
| **quantas pessoas** / **quantos objetos você vê** | responde por voz |
| ativar câmera (de novo) | volta para o modo movimento |
| **parar câmera** (ou tecla `q` na janela) | desliga a câmera |
| que horas são / ajuda | informações |
| sair / tchau | encerra |

## Adicionar seus próprios programas
Edite `comandos.json` (bloco de notas) — não precisa mexer em código:
```json
"apps":  { "obs": {"abrir": "C:\\Program Files\\obs-studio\\bin\\64bit\\obs64.exe", "processo": ["obs64.exe"]} },
"sites": { "instagram": "https://www.instagram.com" },
"pastas": { "projetos": "C:\\Users\\Voce\\Projetos" }
```
Depois diga "Jarvis, abrir obs". O campo `abrir` aceita nome do programa, caminho completo, URL ou protocolo (`spotify:`).
`processo` é o nome do `.exe` no Gerenciador de Tarefas e só é necessário para o "fechar".

Para aceitar frases sem "Jarvis", ponha `PALAVRA_DE_ATIVACAO = ""` em `main.py`.
Sensibilidade da câmera: `area_minima` em `jarvis/movimento.py`.

Na primeira vez que usar a contagem, o Jarvis baixa os modelos de IA do MediaPipe (poucos MB) para a pasta `modelos/` — precisa de internet só nessa vez.

Teste do interpretador sem hardware: `python tests_comandos.py`.
