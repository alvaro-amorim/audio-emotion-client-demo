# Audio Emotion Client Demo

App local de demonstração que consome a **[Audio Emotion API](https://github.com/alvaro-amorim/emotion-api)**, transforma áudio em contexto emocional estruturado e usa esse contexto para gerar uma resposta com LLM.

> Este projeto é um cliente demonstrativo. Ele não transcreve, não calcula emoção e não processa áudio localmente. Toda a análise de áudio acontece na Audio Emotion API principal.

## Projetos relacionados

Este repositório faz parte de um ecossistema com dois projetos:

- **[emotion-api](https://github.com/alvaro-amorim/emotion-api)** — API principal. Recebe áudio, calcula métricas acústicas, transcreve, interpreta sinais emocionais e retorna um JSON pronto para agentes de IA.
- **audio-emotion-client-demo** — este repositório. App cliente que envia áudio para a API principal, recebe o contexto emocional e monta um prompt para uma LLM responder considerando emoção, tom e intenção.

Fluxo completo:

```txt
Usuário grava ou envia áudio
        ↓
audio-emotion-client-demo
        ↓  X-API-Key + multipart/form-data
emotion-api
        ↓
Transcrição + métricas + análise emocional
        ↓
audio-emotion-client-demo
        ↓
Prompt emocionalmente contextualizado
        ↓
LLM ou fallback local
        ↓
Resposta final ao usuário
```

## Propósito do projeto

Este app foi criado para validar um cenário real de consumo da **Audio Emotion API** por outro produto.

A ideia é demonstrar como uma aplicação externa pode usar a API de emoção para enriquecer uma resposta de IA. Em vez de enviar apenas a transcrição crua para uma LLM, o app envia também sinais como:

- emoção principal provável;
- tom emocional;
- intenção do usuário;
- urgência;
- calma;
- observações importantes;
- contexto recomendado para outro agente de IA;
- transcrição comentada.

Isso permite que a resposta final seja mais sensível ao estado provável do usuário.

## O que este app faz

- Recebe upload de áudio em `.mp3`, `.wav`, `.m4a`, `.webm` ou `.ogg`.
- Permite gravação pelo navegador com `MediaRecorder`.
- Permite ouvir e baixar o áudio gravado antes de enviar.
- Envia o áudio para a Audio Emotion API usando `X-API-Key`.
- Recebe o JSON emocional da API principal.
- Monta um prompt para LLM com transcrição, emoção, intenção e contexto recomendado.
- Chama Cohere quando configurada.
- Usa fallback local quando a LLM está desativada, sem chave ou indisponível.
- Mostra na interface:
  - resultado da Audio Emotion API;
  - prompt enviado para a LLM;
  - resposta final da LLM/fallback;
  - JSON bruto expansível.

## O que este app não faz

- Não transcreve áudio.
- Não calcula métricas acústicas.
- Não interpreta emoção diretamente.
- Não usa FFmpeg.
- Não usa Whisper/faster-whisper.
- Não salva dados em banco.
- Não possui login, dashboard, billing ou histórico persistente.

Essas responsabilidades pertencem à **[Audio Emotion API](https://github.com/alvaro-amorim/emotion-api)**.

## Stack

- Python 3.11+
- FastAPI
- Uvicorn
- httpx
- python-dotenv / configuração por `.env`
- Cohere SDK opcional
- HTML, CSS e JavaScript puro
- pytest

## Arquitetura

```txt
POST /demo/analyze-and-respond
        ↓
Recebe áudio no app cliente
        ↓
Chama emotion-api em /v1/analyze-audio
        ↓
Extrai transcrição, emoção e contexto recomendado
        ↓
Monta prompt com prompt_builder.py
        ↓
Chama llm_service.py
        ↓
Cohere ou fallback local
        ↓
Retorna resultado para a interface
```

## Pré-requisitos

- Python 3.11+
- Repositório **emotion-api** rodando localmente
- Opcional: chave Cohere para resposta real de LLM

## Configuração

Crie um `.env` a partir do exemplo:

```powershell
Copy-Item .env.example .env
```

Variáveis principais:

```env
APP_NAME=Audio Emotion Client Demo
APP_ENV=development
APP_VERSION=0.1.0
HOST=127.0.0.1
PORT=8020

AUDIO_EMOTION_API_BASE_URL=http://127.0.0.1:8014
AUDIO_EMOTION_API_KEY=dev-local-key-change-me
AUDIO_EMOTION_API_KEY_HEADER_NAME=X-API-Key
AUDIO_EMOTION_API_TIMEOUT_SECONDS=300

USE_LLM=true
LLM_PROVIDER=cohere
COHERE_API_KEY=
COHERE_CHAT_MODEL=command-a-03-2025

DEFAULT_ASSISTANT_PROFILE=support
SHOW_RAW_JSON=true
```

As chaves ficam apenas no backend. O frontend nunca recebe `AUDIO_EMOTION_API_KEY` nem `COHERE_API_KEY`.

Para usar sem LLM real:

```env
USE_LLM=false
```

Nesse modo, o app gera uma resposta local simples a partir do contexto emocional retornado pela API principal.

## Instalação

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Rodar a Audio Emotion API principal

No repositório **emotion-api**:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8014
```

A API principal deve estar disponível em:

```txt
http://127.0.0.1:8014
```

## Rodar o app cliente

No repositório **audio-emotion-client-demo**:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8020
```

Abra:

```txt
http://127.0.0.1:8020
```

## Como usar

1. Deixe a **Audio Emotion API** rodando em `http://127.0.0.1:8014`.
2. Deixe este app rodando em `http://127.0.0.1:8020`.
3. Selecione um arquivo de áudio ou grave pelo navegador.
4. Se gravar, ouça o áudio no player antes de enviar.
5. Opcionalmente, baixe o áudio gravado para comparar testes.
6. Escolha o perfil do assistente:
   - suporte técnico;
   - atendimento ao cliente;
   - professor;
   - assistente empático;
   - livre.
7. Adicione uma instrução extra para a LLM, se quiser.
8. Clique em `Analisar áudio e gerar resposta`.
9. Veja:
   - análise emocional;
   - prompt enviado para a LLM;
   - resposta final.

## Gravação pelo navegador

A gravação usa `MediaRecorder` e tenta escolher o melhor formato suportado pelo navegador nesta ordem:

```txt
audio/webm;codecs=opus
audio/webm
audio/ogg;codecs=opus
audio/ogg
```

Após parar a gravação, a interface mostra:

- player `<audio controls>`;
- botão para baixar o áudio gravado;
- tipo MIME usado;
- nome do arquivo;
- tamanho;
- duração aproximada.

Nome padrão do arquivo:

```txt
browser-recording-YYYYMMDD-HHMMSS.webm
```

## Dicas para melhorar a captação

- Fale perto do microfone, sem encostar nele.
- Evite música, ruído e eco.
- Não fale baixo demais.
- Não grite ou estoure o volume.
- Use microfone externo ou fone com microfone quando possível.
- Grave frases completas.
- Evite pausas excessivamente longas quando estiver testando transcrição.

## Prompt enviado para a LLM

O prompt é montado com base no retorno da API principal e inclui:

- transcrição real;
- transcrição comentada;
- emoção primária;
- emoções secundárias;
- tom emocional;
- intenção;
- urgência;
- calma;
- score de confiança;
- observações importantes;
- contexto recomendado para outro agente de IA;
- perfil escolhido do assistente;
- instrução extra do usuário.

O objetivo é fazer a LLM responder considerando não apenas o conteúdo literal da fala, mas também o estado emocional inferido.

## Perfis de resposta

- `support`: suporte técnico objetivo e acolhedor.
- `customer_service`: atendimento ao cliente.
- `teacher`: professor didático e paciente.
- `empathetic`: assistente empático.
- `free`: segue a instrução livre do usuário.

## Cohere e fallback local

Para usar Cohere:

```env
USE_LLM=true
LLM_PROVIDER=cohere
COHERE_API_KEY=sua-chave
COHERE_CHAT_MODEL=command-a-03-2025
```

Se a chave estiver vazia, `USE_LLM=false` ou a chamada falhar, o app usa fallback local e retorna um warning. Isso mantém o fluxo funcionando mesmo sem LLM externa.

## Endpoints do app cliente

```txt
GET  /
GET  /health
GET  /demo/config
GET  /demo/status
POST /demo/analyze-and-respond
```

`/demo/config` retorna apenas configuração segura para o frontend e não expõe chaves.

## Testes

Os testes usam mocks e não dependem da Audio Emotion API real, internet ou Cohere real.

```powershell
python -m pytest
```

## Teste manual recomendado

1. Rode a Audio Emotion API:

```powershell
cd C:\Users\Álvaro Amorim\Desktop\emotion-api
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8014
```

2. Rode este app:

```powershell
cd C:\Users\Álvaro Amorim\Desktop\audio-emotion-client-demo
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8020
```

3. Abra `http://127.0.0.1:8020`.
4. Grave ou envie um áudio.
5. Confira se aparecem:
   - transcrição;
   - emoção;
   - intenção;
   - contexto recomendado;
   - prompt para LLM;
   - resposta final.

## Testar erros manualmente

API principal desligada:

1. Pare o servidor em `http://127.0.0.1:8014`.
2. Envie um áudio pelo app cliente.
3. O app deve mostrar erro claro de API indisponível.

API Key errada:

1. Altere `AUDIO_EMOTION_API_KEY` no `.env`.
2. Reinicie o app cliente.
3. Envie um áudio.
4. O app deve mostrar erro claro de chave rejeitada.

## Segurança

- `.env` fica fora do Git.
- Nenhuma chave é enviada para o frontend.
- A chamada para a Audio Emotion API é feita pelo backend.
- A chamada para Cohere também é feita pelo backend.
- O app não persiste áudio, histórico ou respostas em banco.

## Limitações atuais

- Demo local, não produto em produção.
- Sem login, usuários ou autenticação própria.
- Sem histórico persistente.
- Sem fila, rate limit, cobrança ou dashboard.
- Depende da Audio Emotion API principal para toda análise de áudio.
- A qualidade da resposta final depende da qualidade da transcrição e da análise emocional retornadas pela API principal.

## Roadmap possível

- Script de smoke E2E para testar `client-demo → emotion-api → LLM/fallback`.
- Histórico temporário de análises no app cliente.
- Perfis de prompt mais personalizáveis.
- Melhor UI para comparar resposta com e sem contexto emocional.
- Deploy demonstrativo controlado.

## Aviso

Este app foi criado para validar a integração entre uma API de análise emocional de áudio e uma aplicação consumidora. A análise emocional continua sendo interpretativa/probabilística e deve ser usada como contexto auxiliar, não como diagnóstico.
