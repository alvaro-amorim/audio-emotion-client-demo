# Audio Emotion Client Demo

App local de demonstração em FastAPI + HTML/CSS/JavaScript puro que consome a Audio Emotion API principal e usa a análise emocional retornada para montar um prompt para uma LLM.

Este app não transcreve áudio, não calcula emoção, não processa áudio localmente, não usa FFmpeg, Whisper, banco de dados ou frontend framework. Ele apenas recebe o arquivo, envia para a Audio Emotion API pelo backend e mostra o resultado.

## Relação com a Audio Emotion API

A API principal deve estar rodando em outro repositório, normalmente em:

```txt
http://127.0.0.1:8014
```

O app cliente chama:

```txt
POST http://127.0.0.1:8014/v1/analyze-audio
Header: X-API-Key: AUDIO_EMOTION_API_KEY
Body: multipart/form-data com file=<audio>
```

A chave fica apenas no backend. O navegador nunca recebe `AUDIO_EMOTION_API_KEY` nem `COHERE_API_KEY`.

## Pré-requisitos

- Python 3.11+
- Audio Emotion API principal rodando localmente
- Opcional: chave da Cohere para resposta real de LLM

## Configuração

Crie um `.env` a partir do exemplo:

```powershell
Copy-Item .env.example .env
```

Variáveis principais:

```env
AUDIO_EMOTION_API_BASE_URL=http://127.0.0.1:8014
AUDIO_EMOTION_API_KEY=dev-local-key-change-me
AUDIO_EMOTION_API_KEY_HEADER_NAME=X-API-Key
USE_LLM=true
COHERE_API_KEY=
```

Para usar sem LLM real, deixe `COHERE_API_KEY` vazia ou defina:

```env
USE_LLM=false
```

Nesse caso o app retorna uma resposta local simples baseada no contexto emocional.

## Instalação

No repositório `audio-emotion-client-demo`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Rodar a Audio Emotion API principal

No repositório `emotion-api`:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8014
```

## Rodar o app cliente

No repositório `audio-emotion-client-demo`:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8020
```

Abra:

```txt
http://127.0.0.1:8020
```

## Uso

1. Selecione ou grave um áudio `.mp3`, `.wav`, `.m4a`, `.webm` ou `.ogg`.
2. Escolha o perfil do assistente.
3. Opcionalmente informe uma instrução extra para a LLM.
4. Clique em `Analisar áudio e gerar resposta`.
5. Veja o resultado da Audio Emotion API, o prompt enviado para a LLM e a resposta final.

## Gravação pelo navegador

A seção `Gravação pelo navegador` permite captar áudio direto do microfone usando `MediaRecorder`.

Fluxo:

1. Clique em `Gravar`.
2. Fale perto do microfone.
3. Clique em `Parar`.
4. O app mostra um player `<audio controls>` para ouvir a gravação antes de enviar.
5. O app mostra nome do arquivo, tipo MIME usado, tamanho e duração aproximada.
6. Use `Baixar áudio gravado` para salvar o arquivo localmente.
7. Clique em `Analisar áudio e gerar resposta` para enviar o áudio ao backend.

O arquivo gravado recebe nome no formato:

```txt
browser-recording-YYYYMMDD-HHMMSS.webm
```

O navegador usa o primeiro MIME suportado nesta ordem:

```txt
audio/webm;codecs=opus
audio/webm
audio/ogg;codecs=opus
audio/ogg
```

## Dicas para melhorar a captação

- Fale perto do microfone.
- Evite música, ruído de fundo e conversas paralelas.
- Não fale muito baixo.
- Não deixe o volume estourar ou distorcer.
- Use fone ou microfone externo se possível.
- Grave frases completas e evite pausas longas demais.

## Cohere

Para usar Cohere:

```env
USE_LLM=true
LLM_PROVIDER=cohere
COHERE_API_KEY=sua-chave
COHERE_CHAT_MODEL=command-a-03-2025
```

Se a chamada falhar ou a chave estiver ausente, o app usa fallback local e retorna um warning.

## Testes

Os testes usam mocks. Eles não dependem da Audio Emotion API real, internet ou Cohere real.

```powershell
python -m pytest
```

## Testar erros manualmente

API principal desligada:

1. Pare o servidor em `http://127.0.0.1:8014`.
2. Envie um áudio pelo app cliente.
3. O app deve mostrar erro claro de API indisponível.

API key errada:

1. Altere `AUDIO_EMOTION_API_KEY` no `.env`.
2. Reinicie o app cliente.
3. Envie um áudio.
4. O app deve mostrar erro claro de chave rejeitada.

## Limitações

- Demo local sem login.
- Sem banco de dados ou histórico.
- Sem fila, rate limit, cobrança ou dashboard.
- Não persiste áudios.
- Depende da Audio Emotion API principal para toda análise de áudio.
