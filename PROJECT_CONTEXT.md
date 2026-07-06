# PROJECT_CONTEXT — Audio Emotion Client Demo

## 1. Nome do projeto

**Audio Emotion Client Demo**

Este projeto é um app cliente de demonstração que consome a **Audio Emotion API** local já existente e usa o retorno emocional da API para montar um contexto enriquecido para uma LLM.

O objetivo deste app NÃO é substituir a Audio Emotion API.

O objetivo é provar, na prática, como outro sistema poderia usar a Audio Emotion API como serviço externo/local para receber um áudio, obter transcrição emocional enriquecida e usar esse contexto para melhorar a resposta de uma IA.

---

## 2. Estado da API principal que será consumida

A API principal já está rodando localmente no projeto separado `emotion-api`.

URL local esperada:

```txt
http://127.0.0.1:8014
```

Endpoint principal:

```txt
POST /v1/analyze-audio
```

Autenticação local:

```txt
Header: X-API-Key: dev-local-key-change-me
```

A API principal já foi validada por smoke test e retornou:

```txt
status_code: 201
transcription_status: real
emotion_status: fallback_local
primary_emotion: calma
recommended_context_for_ai_agent: Responder em tom tranquilo e direto. O usuário parece aberto a explicações claras e sem pressa.
```

Portanto, para este app cliente, a Audio Emotion API deve ser tratada como uma API externa já funcional.

---

## 3. Objetivo do app cliente

O app cliente deve permitir que o usuário:

1. Envie ou grave um áudio.
2. O app cliente envie esse áudio para a Audio Emotion API usando API Key.
3. Receba da Audio Emotion API:
   - transcrição real;
   - transcrição comentada;
   - métricas acústicas reais;
   - emoção principal;
   - emoções secundárias;
   - tom emocional;
   - intenção;
   - urgência;
   - calma;
   - nível de confiança;
   - contexto recomendado para outro agente de IA.
4. Monte um prompt para uma LLM usando esse contexto emocional.
5. Envie o prompt para uma LLM, preferencialmente Cohere, se configurada.
6. Mostre na tela:
   - resultado retornado pela Audio Emotion API;
   - prompt/contexto enviado para a LLM;
   - resposta final da LLM.

Esse app deve demonstrar a utilidade prática da Audio Emotion API como camada intermediária entre áudio humano e agentes de IA.

---

## 4. O que este app NÃO deve fazer

Este app cliente NÃO deve:

- transcrever áudio por conta própria;
- calcular emoção por conta própria;
- calcular métricas acústicas localmente;
- usar FFmpeg;
- usar Whisper, faster-whisper ou WhisperX;
- usar banco de dados;
- criar login;
- criar autenticação comercial;
- criar API keys próprias;
- implementar embeddings;
- implementar RAG;
- treinar modelo;
- alterar o projeto `emotion-api`;
- guardar permanentemente os áudios enviados;
- expor chaves no frontend.

Toda análise de áudio deve vir da Audio Emotion API.

---

## 5. Stack obrigatória

Usar:

```txt
Python 3.11+
FastAPI
Uvicorn
HTML
CSS
JavaScript puro
python-dotenv
httpx
pytest
Cohere SDK opcional
```

Não usar:

```txt
React
Vite
Next.js
Vue
Angular
Banco de dados
Docker
Whisper
faster-whisper
FFmpeg
Torch
Transformers
```

---

## 6. Estrutura de pastas esperada

Criar a seguinte estrutura:

```txt
audio-emotion-client-demo/
│
├── app/
│   ├── main.py
│   │
│   ├── core/
│   │   └── config.py
│   │
│   ├── services/
│   │   ├── audio_emotion_api_client.py
│   │   ├── llm_service.py
│   │   └── prompt_builder.py
│   │
│   └── web/
│       ├── index.html
│       ├── styles.css
│       └── app.js
│
├── tests/
│   ├── test_health.py
│   ├── test_web_interface.py
│   ├── test_prompt_builder.py
│   ├── test_audio_emotion_api_client.py
│   └── test_llm_service.py
│
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── PROJECT_CONTEXT.md
```

---

## 7. Variáveis de ambiente

Criar `.env.example` com:

```env
APP_NAME=Audio Emotion Client Demo
APP_ENV=development
APP_VERSION=0.1.0
DEBUG=true
HOST=127.0.0.1
PORT=8020

# Audio Emotion API principal
AUDIO_EMOTION_API_BASE_URL=http://127.0.0.1:8014
AUDIO_EMOTION_API_KEY=dev-local-key-change-me
AUDIO_EMOTION_API_KEY_HEADER_NAME=X-API-Key
AUDIO_EMOTION_API_TIMEOUT_SECONDS=300

# LLM
USE_LLM=true
LLM_PROVIDER=cohere
COHERE_API_KEY=
COHERE_CHAT_MODEL=command-a-03-2025

# Comportamento da demo
DEFAULT_ASSISTANT_PROFILE=support
SHOW_RAW_JSON=true
MAX_UPLOAD_SIZE_MB=100
ALLOWED_AUDIO_EXTENSIONS=mp3,wav,m4a,webm,ogg
```

O Codex deve criar `.env.example`, mas **não deve criar `.env` com chave real**.

No ambiente local do usuário, o `.env` real deverá conter pelo menos:

```env
AUDIO_EMOTION_API_BASE_URL=http://127.0.0.1:8014
AUDIO_EMOTION_API_KEY=dev-local-key-change-me
AUDIO_EMOTION_API_KEY_HEADER_NAME=X-API-Key
USE_LLM=true
COHERE_API_KEY=SUA_CHAVE_REAL_AQUI
```

Se `COHERE_API_KEY` estiver vazio, o app deve funcionar com fallback local de resposta.

---

## 8. Portas do sistema

A separação de portas deve ser:

```txt
Audio Emotion API principal: http://127.0.0.1:8014
Audio Emotion Client Demo:   http://127.0.0.1:8020
```

O app cliente deve assumir que a API principal está rodando em `8014`, mas permitir alterar via `.env`.

---

## 9. Contrato esperado da Audio Emotion API

O app cliente deve chamar:

```txt
POST {AUDIO_EMOTION_API_BASE_URL}/v1/analyze-audio
```

Com header:

```txt
X-API-Key: {AUDIO_EMOTION_API_KEY}
```

Body:

```txt
multipart/form-data
file=<arquivo de áudio>
```

O retorno esperado pode conter campos como:

```json
{
  "analysis_id": "uuid",
  "status": {
    "acoustic_metrics_status": "real",
    "transcription_status": "real",
    "emotion_status": "real"
  },
  "transcription": {
    "text": "texto transcrito",
    "segments": [],
    "words": []
  },
  "annotated_transcription": "texto com comentários emocionais entre colchetes",
  "emotion_summary": {
    "primary_emotion": "calma",
    "secondary_emotions": [],
    "implicit_emotion": "...",
    "emotional_tone": "...",
    "intention": "...",
    "urgency_level": "...",
    "calmness_level": "...",
    "confidence_score": 0.75
  },
  "important_observations": [],
  "recommended_context_for_ai_agent": "texto orientando outro agente de IA",
  "acoustic_metrics": {},
  "emotion_debug": {},
  "emotion_comparison": {}
}
```

O app cliente deve ser tolerante caso alguns campos venham ausentes.

Ele deve extrair o máximo possível, sem quebrar.

---

## 10. Endpoints do app cliente

### 10.1 GET /

Servir a interface web.

---

### 10.2 GET /health

Retornar:

```json
{
  "status": "ok",
  "app": "Audio Emotion Client Demo",
  "version": "0.1.0",
  "environment": "development"
}
```

---

### 10.3 GET /demo/status

Retornar status da configuração do app cliente:

```json
{
  "status": "ok",
  "audio_emotion_api_base_url": "http://127.0.0.1:8014",
  "audio_emotion_api_key_configured": true,
  "llm_enabled": true,
  "llm_provider": "cohere",
  "cohere_configured": false
}
```

Não retornar chaves.

---

### 10.4 POST /demo/analyze-and-respond

Recebe:

- arquivo de áudio;
- `assistant_profile` opcional;
- `user_instruction` opcional.

Fluxo:

```txt
arquivo recebido
↓
validação simples de extensão/tamanho
↓
envia para Audio Emotion API
↓
recebe análise emocional
↓
monta prompt para LLM
↓
chama Cohere se configurada
↓
usa fallback local se LLM estiver desligada ou sem chave
↓
retorna resultado completo ao frontend
```

Retorno esperado:

```json
{
  "status": "ok",
  "audio_emotion_result": {},
  "llm_prompt": "...",
  "llm_response": {
    "status": "cohere",
    "text": "resposta final"
  },
  "warnings": []
}
```

Se a Audio Emotion API estiver fora do ar:

```json
{
  "status": "error",
  "detail": "Audio Emotion API is unavailable. Make sure it is running at http://127.0.0.1:8014."
}
```

Se a API Key estiver errada:

```json
{
  "status": "error",
  "detail": "Audio Emotion API rejected the request. Check AUDIO_EMOTION_API_KEY."
}
```

---

## 11. Serviço cliente da Audio Emotion API

Criar:

```txt
app/services/audio_emotion_api_client.py
```

Responsabilidades:

- ler base URL;
- ler API key;
- ler nome do header;
- enviar `multipart/form-data`;
- tratar timeout;
- tratar erro 401;
- tratar API fora do ar;
- retornar JSON estruturado;
- nunca imprimir a API key.

Usar `httpx`.

Interface sugerida:

```python
class AudioEmotionApiClient:
    async def analyze_audio(self, filename: str, content: bytes, content_type: str) -> dict:
        ...
```

---

## 12. Serviço de LLM

Criar:

```txt
app/services/llm_service.py
```

Responsabilidades:

- chamar Cohere quando `USE_LLM=true` e `COHERE_API_KEY` estiver configurada;
- usar fallback local quando LLM estiver desativada;
- usar fallback local quando Cohere falhar;
- nunca expor `COHERE_API_KEY`;
- retornar status claro.

Possíveis statuses:

```txt
cohere
fallback_local
llm_disabled
llm_error
```

---

## 13. Prompt builder

Criar:

```txt
app/services/prompt_builder.py
```

Ele deve montar um prompt claro para a LLM.

O prompt deve conter:

- papel da LLM;
- perfil escolhido pelo usuário;
- transcrição real;
- transcrição comentada;
- resumo emocional;
- emoção primária;
- emoções secundárias;
- tom emocional;
- intenção;
- urgência;
- calma;
- confiança;
- observações importantes;
- contexto recomendado pela Audio Emotion API;
- instrução extra do usuário.

Exemplo conceitual:

```txt
Você é um assistente que deve responder ao usuário considerando não apenas o texto transcrito, mas também o contexto emocional inferido.

Perfil do assistente: suporte técnico.

Transcrição:
...

Transcrição comentada:
...

Resumo emocional:
- Emoção principal: ...
- Tom: ...
- Intenção: ...
- Urgência: ...
- Calma: ...
- Confiança da análise: ...

Contexto recomendado pela Audio Emotion API:
...

Instrução extra:
...

Responda de forma adequada ao estado emocional do usuário.
Se houver frustração, seja acolhedor e objetivo.
Se houver urgência, seja direto.
Se houver insegurança, explique com calma.
Não afirme que a emoção detectada é uma verdade absoluta.
```

---

## 14. Perfis de assistente

A interface deve oferecer estes perfis:

```txt
support — suporte técnico
customer_service — atendimento ao cliente
teacher — professor/tutor
empathetic — assistente empático
general — assistente geral
custom — instrução livre
```

O perfil deve influenciar o prompt.

Exemplo:

- `support`: resposta objetiva, passo a passo, clara.
- `teacher`: resposta didática, explicando conceitos.
- `empathetic`: resposta mais acolhedora.
- `customer_service`: resposta cordial e profissional.
- `general`: resposta equilibrada.
- `custom`: usar mais fortemente a instrução extra.

---

## 15. Interface web

Criar interface simples em:

```txt
app/web/index.html
app/web/styles.css
app/web/app.js
```

A interface deve ter:

### Cabeçalho

- título: **Audio Emotion Client Demo**
- subtítulo: “Demonstração de consumo da Audio Emotion API por outro app.”
- status do app cliente;
- status da conexão/configuração com Audio Emotion API.

### Entrada de áudio

- input para upload de áudio;
- aceitar `.mp3`, `.wav`, `.m4a`, `.webm`, `.ogg`;
- mostrar nome do arquivo selecionado;
- opcional: gravação pelo navegador com `MediaRecorder`.

### Configuração da resposta

- select de perfil do assistente;
- textarea para instrução extra à LLM.

### Ação

- botão: “Analisar áudio e gerar resposta”;
- loading claro.

### Resultado 1 — Audio Emotion API

Mostrar:

- analysis_id;
- transcription_status;
- emotion_status;
- transcrição;
- transcrição comentada;
- emoção primária;
- emoções secundárias;
- tom emocional;
- intenção;
- urgência;
- calma;
- confidence_score;
- contexto recomendado para IA;
- observações importantes;
- JSON bruto expansível.

### Resultado 2 — Prompt enviado à LLM

Mostrar o prompt completo ou em área expansível.

### Resultado 3 — Resposta da LLM

Mostrar:

- status da LLM;
- resposta final;
- warnings.

---

## 16. UX esperada

- Layout limpo.
- Responsivo.
- Fundo neutro ou escuro.
- Cartões separados.
- Erros claros.
- Loading visível.
- Não expor chaves.
- Não depender de Swagger.

Mensagens de erro úteis:

- “Audio Emotion API indisponível. Verifique se ela está rodando em 8014.”
- “API Key rejeitada pela Audio Emotion API.”
- “LLM desativada ou sem chave. Usando fallback local.”
- “Arquivo inválido ou extensão não permitida.”

---

## 17. Fallback local da LLM

Se `USE_LLM=false`, se `COHERE_API_KEY` estiver vazia ou se Cohere falhar, o app deve retornar uma resposta local simples.

Exemplo:

```txt
Com base na análise emocional, o usuário parece demonstrar calma e abertura para explicações. Uma resposta adequada seria responder de forma clara, tranquila e direta, evitando excesso de complexidade.
```

Esse fallback deve ser marcado como:

```json
{
  "status": "fallback_local",
  "text": "..."
}
```

---

## 18. Segurança

Regras obrigatórias:

- Não expor `AUDIO_EMOTION_API_KEY` no HTML/JS.
- Não expor `COHERE_API_KEY` no HTML/JS.
- Não imprimir chaves em logs.
- Não retornar chaves em `/health` ou `/demo/status`.
- `.env` deve estar no `.gitignore`.
- `.env.example` pode conter placeholders.

As chamadas para a Audio Emotion API devem ser feitas pelo backend FastAPI do app demo, não diretamente pelo navegador, para não expor a chave.

---

## 19. Requirements

Criar `requirements.txt` com:

```txt
fastapi>=0.115,<1.0
uvicorn[standard]>=0.30,<1.0
python-multipart>=0.0.9,<1.0
python-dotenv>=1.0,<2.0
pydantic>=2.0,<3.0
pydantic-settings>=2.0,<3.0
httpx>=0.27,<1.0
cohere>=5.0,<6.0
pytest>=8.0,<9.0
```

Se alguma dependência for desnecessária, pode ajustar, mas não adicionar bibliotecas pesadas.

---

## 20. Testes

Criar testes que NÃO dependam da Audio Emotion API real rodando e NÃO dependam da Cohere real.

Testes obrigatórios:

1. `GET /health` retorna ok.
2. `GET /` retorna HTML.
3. `build_llm_prompt` inclui transcrição e emoção.
4. Cliente da Audio Emotion API envia header `X-API-Key`, usando mock.
5. Cliente trata erro 401 da Audio Emotion API.
6. Cliente trata API fora do ar.
7. LLM service usa fallback quando `USE_LLM=false`.
8. LLM service usa fallback quando `COHERE_API_KEY` está vazia.
9. Endpoint `POST /demo/analyze-and-respond` funciona com mocks.
10. Nenhuma chave aparece nos retornos de status.

Usar mocks/monkeypatch.

---

## 21. README

Criar `README.md` explicando:

- o que é o app;
- como ele se conecta à Audio Emotion API;
- como criar `.env`;
- como instalar dependências;
- como rodar testes;
- como rodar o app;
- como rodar a Audio Emotion API principal;
- como configurar API key;
- como usar com Cohere;
- como usar sem LLM real;
- limitações.

Comandos esperados:

### Rodar a Audio Emotion API principal

No repositório `emotion-api`:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8014
```

### Rodar o app cliente

No repositório `audio-emotion-client-demo`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8020
```

Abrir:

```txt
http://127.0.0.1:8020
```

---

## 22. `.gitignore`

Criar `.gitignore` com:

```gitignore
.venv/
__pycache__/
*.pyc
.env
.pytest_cache/
.DS_Store
```

---

## 23. Critérios de aceite

Ao final da implementação, o projeto deve cumprir:

- `pytest` passando;
- app roda em `http://127.0.0.1:8020`;
- backend chama a Audio Emotion API em `http://127.0.0.1:8014`;
- backend envia `X-API-Key`;
- backend trata erro 401;
- backend trata API indisponível;
- backend monta prompt para LLM;
- backend chama Cohere se configurada;
- backend usa fallback se LLM estiver desativada ou sem chave;
- frontend mostra análise emocional;
- frontend mostra prompt enviado à LLM;
- frontend mostra resposta final da LLM;
- nenhuma chave é exposta no frontend;
- README completo.

---

## 24. Validação manual esperada

Após implementar:

1. Deixar a Audio Emotion API rodando em:

```txt
http://127.0.0.1:8014
```

2. Rodar o app cliente em:

```txt
http://127.0.0.1:8020
```

3. Enviar um áudio `.m4a`, `.mp3`, `.wav`, `.webm` ou `.ogg`.

4. Confirmar que aparece:

- transcrição real;
- emoção detectada;
- contexto recomendado;
- prompt da LLM;
- resposta da LLM ou fallback local.

5. Testar com a Audio Emotion API desligada.

Resultado esperado:

```txt
Erro claro informando que a Audio Emotion API está indisponível.
```

6. Testar com API Key errada.

Resultado esperado:

```txt
Erro claro informando que a chave foi rejeitada.
```

---

## 25. Prompt final para o Codex usar após ler este MD

Quando este arquivo estiver na raiz do repositório novo, o Codex deve executar:

```txt
Leia integralmente o PROJECT_CONTEXT.md na raiz do repositório.

Implemente o projeto Audio Emotion Client Demo exatamente conforme o documento.

O objetivo é criar um app demo local em FastAPI + HTML/CSS/JS puro que consome a Audio Emotion API já existente em http://127.0.0.1:8014 usando X-API-Key, recebe análise emocional de áudio, monta um prompt para uma LLM e exibe a resposta final.

Não implemente processamento de áudio local, transcrição local, FFmpeg, Whisper, banco de dados, embeddings ou autenticação complexa.

Crie todos os arquivos necessários:
- app/main.py
- app/core/config.py
- app/services/audio_emotion_api_client.py
- app/services/llm_service.py
- app/services/prompt_builder.py
- app/web/index.html
- app/web/styles.css
- app/web/app.js
- tests/
- .env.example
- .gitignore
- requirements.txt
- README.md

Garanta que:
- pytest passe;
- o app rode em http://127.0.0.1:8020;
- as chamadas para a Audio Emotion API sejam feitas pelo backend;
- X-API-Key seja enviado pelo backend;
- chaves não sejam expostas no frontend;
- a LLM use Cohere se configurada;
- fallback local funcione se Cohere estiver ausente/desativada;
- erros de API offline e API Key inválida sejam tratados claramente.

Ao final, rode:
python -m pip install -r requirements.txt
python -m pytest
uvicorn app.main:app --reload --host 127.0.0.1 --port 8020

Depois me entregue um resumo com:
- arquivos criados;
- como rodar;
- como configurar .env;
- como testar com a Audio Emotion API;
- resultado dos testes;
- limitações restantes.
```

---

## 26. Limitações conhecidas do app demo

Este app é apenas uma prova de consumo.

Ele ainda não terá:

- login;
- banco;
- histórico;
- deploy;
- multiusuário;
- cobrança;
- rate limit;
- fila de processamento;
- gerenciamento de chaves;
- dashboard completo.

Essas coisas pertencem a uma etapa futura se a Audio Emotion API virar produto/SaaS.

