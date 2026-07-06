const form = document.querySelector("#analyze-form");
const fileInput = document.querySelector("#audio-file");
const selectedFile = document.querySelector("#selected-file");
const loading = document.querySelector("#loading");
const errorMessage = document.querySelector("#error-message");
const submitButton = document.querySelector("#submit-button");
const results = document.querySelector("#results");
const rawJsonWrapper = document.querySelector("#raw-json-wrapper");

const startRecordingButton = document.querySelector("#start-recording");
const stopRecordingButton = document.querySelector("#stop-recording");
const clearRecordingButton = document.querySelector("#clear-recording");
const recordingStatus = document.querySelector("#recording-status");
const recordingTimer = document.querySelector("#recording-timer");
const recordingMime = document.querySelector("#recording-mime");
const recordingDetails = document.querySelector("#recording-details");
const recordedAudioPlayer = document.querySelector("#recorded-audio-player");
const downloadRecording = document.querySelector("#download-recording");
const recordedFileName = document.querySelector("#recorded-file-name");
const recordedFileType = document.querySelector("#recorded-file-type");
const recordedFileSize = document.querySelector("#recorded-file-size");
const recordedFileDuration = document.querySelector("#recorded-file-duration");

const preferredMimeTypes = [
  "audio/webm;codecs=opus",
  "audio/webm",
  "audio/ogg;codecs=opus",
  "audio/ogg",
];

let safeConfig = null;
let mediaRecorder = null;
let mediaStream = null;
let recordedChunks = [];
let recordedFile = null;
let recordedObjectUrl = null;
let recordingTimerInterval = null;
let recordingStartedAt = 0;
let recordingDurationSeconds = null;
let selectedRecorderMimeType = "";

function isPlainObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function humanizeKey(key) {
  return String(key).replaceAll("_", " ");
}

function formatValue(value) {
  if (value === null || value === undefined || value === "") {
    return "Não informado";
  }
  if (typeof value === "string") {
    return value;
  }
  if (typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }
  if (Array.isArray(value)) {
    return formatList(value);
  }
  if (isPlainObject(value)) {
    return formatObject(value);
  }
  return String(value);
}

function formatList(value) {
  if (!Array.isArray(value)) {
    return formatValue(value);
  }
  if (!value.length) {
    return "Não informado";
  }
  return value.map((item) => `- ${formatValue(item)}`).join("\n");
}

function formatObject(value) {
  if (!isPlainObject(value)) {
    return formatValue(value);
  }

  const entries = Object.entries(value).filter(([, item]) => item !== null && item !== undefined);
  if (!entries.length) {
    return "Não informado";
  }

  return entries.map(([key, item]) => `${humanizeKey(key)}: ${formatValue(item)}`).join("\n");
}

function formatAnnotatedTranscription(value) {
  if (typeof value === "string") {
    return value;
  }
  if (isPlainObject(value) && typeof value.text === "string") {
    return value.text;
  }
  return formatValue(value);
}

function formatRecommendedContext(value) {
  if (typeof value === "string") {
    return value;
  }
  if (!isPlainObject(value)) {
    return formatValue(value);
  }

  const preferredKeys = ["response_strategy", "emotional_alignment", "key_phrases_to_use"];
  const keys = [
    ...preferredKeys.filter((key) => Object.prototype.hasOwnProperty.call(value, key)),
    ...Object.keys(value).filter((key) => !preferredKeys.includes(key)),
  ];

  return keys.map((key) => `${humanizeKey(key)}: ${formatValue(value[key])}`).join("\n");
}

function setText(selector, value, formatter = formatValue) {
  document.querySelector(selector).textContent = formatter(value);
}

function showError(message) {
  errorMessage.textContent = message;
  errorMessage.hidden = false;
}

function clearError() {
  errorMessage.textContent = "";
  errorMessage.hidden = true;
}

function renderList(element, value) {
  element.innerHTML = "";

  if (Array.isArray(value) && value.length) {
    value.forEach((item) => {
      const li = document.createElement("li");
      li.textContent = formatValue(item);
      element.appendChild(li);
    });
    return;
  }

  if (isPlainObject(value)) {
    Object.entries(value).forEach(([key, item]) => {
      const li = document.createElement("li");
      li.textContent = `${humanizeKey(key)}: ${formatValue(item)}`;
      element.appendChild(li);
    });
    return;
  }

  const li = document.createElement("li");
  li.textContent = formatValue(value);
  element.appendChild(li);
}

function renderSummaryItem(label, value) {
  const div = document.createElement("div");
  div.className = "summary-item";

  const labelEl = document.createElement("span");
  labelEl.textContent = label;
  div.appendChild(labelEl);

  const valueEl = document.createElement("strong");
  valueEl.textContent = formatValue(value);
  div.appendChild(valueEl);

  return div;
}

function padNumber(value) {
  return String(value).padStart(2, "0");
}

function formatBytes(bytes) {
  if (!Number.isFinite(bytes) || bytes <= 0) {
    return "0 KB";
  }
  const kilobytes = bytes / 1024;
  if (kilobytes < 1024) {
    return `${kilobytes.toFixed(1)} KB`;
  }
  return `${(kilobytes / 1024).toFixed(2)} MB`;
}

function formatDuration(seconds) {
  if (!Number.isFinite(seconds) || seconds <= 0) {
    return "Não informado";
  }
  const roundedSeconds = Math.max(1, Math.round(seconds));
  const minutes = Math.floor(roundedSeconds / 60);
  const remainingSeconds = roundedSeconds % 60;
  return `${padNumber(minutes)}:${padNumber(remainingSeconds)}`;
}

function timestampForFileName() {
  const now = new Date();
  return [
    now.getFullYear(),
    padNumber(now.getMonth() + 1),
    padNumber(now.getDate()),
    "-",
    padNumber(now.getHours()),
    padNumber(now.getMinutes()),
    padNumber(now.getSeconds()),
  ].join("");
}

function extensionForMimeType(mimeType) {
  return mimeType.includes("ogg") ? "ogg" : "webm";
}

function chooseRecorderMimeType() {
  if (!window.MediaRecorder || typeof MediaRecorder.isTypeSupported !== "function") {
    return "";
  }
  return preferredMimeTypes.find((mimeType) => MediaRecorder.isTypeSupported(mimeType)) || "";
}

function stopMediaStream() {
  if (mediaStream) {
    mediaStream.getTracks().forEach((track) => track.stop());
    mediaStream = null;
  }
}

function revokeRecordedObjectUrl() {
  if (recordedObjectUrl) {
    URL.revokeObjectURL(recordedObjectUrl);
    recordedObjectUrl = null;
  }
}

function stopRecordingTimer(reset = false) {
  if (recordingTimerInterval) {
    clearInterval(recordingTimerInterval);
    recordingTimerInterval = null;
  }
  if (reset) {
    recordingTimer.textContent = "00:00";
  }
}

function startRecordingTimer() {
  recordingStartedAt = Date.now();
  stopRecordingTimer(true);
  recordingTimerInterval = setInterval(() => {
    const elapsedSeconds = (Date.now() - recordingStartedAt) / 1000;
    recordingTimer.textContent = formatDuration(elapsedSeconds);
  }, 250);
}

function resetRecordingPreview() {
  revokeRecordedObjectUrl();
  recordedAudioPlayer.removeAttribute("src");
  recordedAudioPlayer.load();
  recordedAudioPlayer.hidden = true;
  downloadRecording.href = "#";
  downloadRecording.removeAttribute("download");
  downloadRecording.hidden = true;
  recordingDetails.hidden = true;
  recordedFileName.textContent = "Não informado";
  recordedFileType.textContent = "Não informado";
  recordedFileSize.textContent = "Não informado";
  recordedFileDuration.textContent = "Não informado";
  recordingMime.textContent = "MIME ainda não definido";
  recordingDurationSeconds = null;
}

function updateSelectedFileLabel() {
  if (recordedFile) {
    selectedFile.textContent = `${recordedFile.name} (${formatBytes(recordedFile.size)})`;
    return;
  }

  const uploadFile = fileInput.files?.[0];
  selectedFile.textContent = uploadFile
    ? `${uploadFile.name} (${formatBytes(uploadFile.size)})`
    : "Nenhum arquivo selecionado.";
}

function clearRecording(options = {}) {
  const {
    clearUpload = false,
    clearResults = false,
    statusMessage = "Gravação removida.",
  } = options;

  stopRecordingTimer(true);
  stopMediaStream();
  recordedChunks = [];
  recordedFile = null;
  selectedRecorderMimeType = "";
  resetRecordingPreview();

  if (clearUpload) {
    fileInput.value = "";
  }
  updateSelectedFileLabel();

  recordingStatus.textContent = statusMessage;
  startRecordingButton.disabled = false;
  stopRecordingButton.disabled = true;
  clearRecordingButton.disabled = !fileInput.files?.[0];

  if (clearResults) {
    results.hidden = true;
  }
}

async function getAudioStream() {
  const preferredConstraints = {
    audio: {
      echoCancellation: true,
      noiseSuppression: true,
      autoGainControl: true,
      channelCount: 1,
    },
  };

  try {
    return await navigator.mediaDevices.getUserMedia(preferredConstraints);
  } catch (error) {
    if (["OverconstrainedError", "ConstraintNotSatisfiedError"].includes(error.name)) {
      return navigator.mediaDevices.getUserMedia({ audio: true });
    }
    throw error;
  }
}

function finishRecording() {
  stopRecordingTimer(false);
  stopMediaStream();

  const mimeType = mediaRecorder?.mimeType || selectedRecorderMimeType || "audio/webm";
  const blob = new Blob(recordedChunks, { type: mimeType });
  const durationSeconds = recordingStartedAt ? (Date.now() - recordingStartedAt) / 1000 : null;

  if (!recordedChunks.length || blob.size <= 0) {
    clearRecording({
      clearUpload: true,
      statusMessage: "Gravação vazia. Grave novamente antes de enviar.",
    });
    showError("A gravação ficou vazia. Grave novamente e fale perto do microfone.");
    return;
  }

  const extension = extensionForMimeType(mimeType);
  const filename = `browser-recording-${timestampForFileName()}.${extension}`;
  recordedFile = new File([blob], filename, { type: mimeType });
  recordedObjectUrl = URL.createObjectURL(blob);
  recordingDurationSeconds = durationSeconds;

  recordedAudioPlayer.src = recordedObjectUrl;
  recordedAudioPlayer.hidden = false;
  recordedAudioPlayer.onloadedmetadata = () => {
    if (Number.isFinite(recordedAudioPlayer.duration) && recordedAudioPlayer.duration > 0) {
      recordingDurationSeconds = recordedAudioPlayer.duration;
      recordedFileDuration.textContent = formatDuration(recordingDurationSeconds);
    }
  };

  downloadRecording.href = recordedObjectUrl;
  downloadRecording.download = filename;
  downloadRecording.hidden = false;

  recordingDetails.hidden = false;
  recordedFileName.textContent = filename;
  recordedFileType.textContent = mimeType || "Padrão do navegador";
  recordedFileSize.textContent = formatBytes(blob.size);
  recordedFileDuration.textContent = formatDuration(durationSeconds);
  recordingMime.textContent = `MIME usado: ${mimeType || "Padrão do navegador"}`;

  fileInput.value = "";
  updateSelectedFileLabel();
  recordingStatus.textContent = "Gravação pronta para envio.";
  startRecordingButton.disabled = false;
  stopRecordingButton.disabled = true;
  clearRecordingButton.disabled = false;
}

async function loadStatus() {
  try {
    const [configResponse, statusResponse, healthResponse] = await Promise.all([
      fetch("/demo/config"),
      fetch("/demo/status"),
      fetch("/health"),
    ]);

    safeConfig = await configResponse.json();
    const status = await statusResponse.json();
    const health = await healthResponse.json();

    document.querySelector("#app-status").textContent = `${health.status} ${health.version}`;
    document.querySelector("#api-status").textContent =
      status.audio_emotion_api_key_configured
        ? `${status.audio_emotion_api_base_url} configurada`
        : `${status.audio_emotion_api_base_url} sem API key`;
    document.querySelector("#llm-status").textContent = status.cohere_configured
      ? `${status.llm_provider} configurada`
      : status.llm_enabled
        ? `${status.llm_provider} sem chave, fallback local`
        : "desativada, fallback local";

    if (safeConfig.default_assistant_profile) {
      document.querySelector("#assistant-profile").value = safeConfig.default_assistant_profile;
    }
  } catch (error) {
    document.querySelector("#app-status").textContent = "erro";
    document.querySelector("#api-status").textContent = "não foi possível carregar";
    document.querySelector("#llm-status").textContent = "desconhecido";
  }
}

fileInput.addEventListener("change", () => {
  clearError();
  recordedFile = null;
  recordedChunks = [];
  resetRecordingPreview();
  updateSelectedFileLabel();
  recordingStatus.textContent = fileInput.files?.[0]
    ? "Arquivo selecionado para envio."
    : "Disponível se o navegador permitir microfone.";
  clearRecordingButton.disabled = !fileInput.files?.[0];
});

function getSelectedAudioFile() {
  if (recordedFile) {
    return recordedFile;
  }
  return fileInput.files?.[0] || null;
}

function renderResult(data) {
  const audioResult = data.audio_emotion_result || {};
  const status = audioResult.status || {};
  const transcription = audioResult.transcription || {};
  const summary = audioResult.emotion_summary || {};

  const summaryGrid = document.querySelector("#emotion-summary");
  summaryGrid.innerHTML = "";
  [
    ["Analysis ID", audioResult.analysis_id],
    ["Transcription status", status.transcription_status],
    ["Emotion status", status.emotion_status],
    ["Fonte da emoção", status.emotion_source || audioResult.emotion_source],
    ["Emoção primária", summary.primary_emotion],
    ["Emoções secundárias", summary.secondary_emotions],
    ["Tom emocional", summary.emotional_tone || summary.tone],
    ["Intenção", summary.intention],
    ["Urgência", summary.urgency_level || summary.urgency],
    ["Calma", summary.calmness_level || summary.calmness],
    ["Confidence score", summary.confidence_score || summary.confidence],
  ].forEach(([label, value]) => summaryGrid.appendChild(renderSummaryItem(label, value)));

  setText("#transcription", transcription.text);
  setText("#annotated-transcription", audioResult.annotated_transcription, formatAnnotatedTranscription);
  setText("#recommended-context", audioResult.recommended_context_for_ai_agent, formatRecommendedContext);
  renderList(document.querySelector("#important-observations"), audioResult.important_observations);

  document.querySelector("#raw-json").textContent = JSON.stringify(audioResult, null, 2);
  rawJsonWrapper.hidden = safeConfig && safeConfig.show_raw_json === false;

  document.querySelector("#llm-prompt").textContent = data.llm_prompt || "";
  document.querySelector("#final-llm-status").textContent =
    data.llm_status || data.llm_response?.status || "Não informado";
  document.querySelector("#llm-response").textContent = formatValue(data.llm_response?.text);

  const warnings = data.warnings || data.llm_response?.warnings || [];
  const warningsWrapper = document.querySelector("#warnings-wrapper");
  renderList(document.querySelector("#warnings"), warnings);
  warningsWrapper.hidden = !warnings.length;

  results.hidden = false;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearError();

  const audioFile = getSelectedAudioFile();
  if (!audioFile) {
    showError("Selecione ou grave um arquivo de áudio antes de enviar.");
    return;
  }

  if (!audioFile.size || audioFile.size <= 0) {
    showError("O áudio selecionado parece vazio. Grave ou selecione outro arquivo.");
    return;
  }

  const formData = new FormData();
  formData.append("file", audioFile);
  formData.append("assistant_profile", document.querySelector("#assistant-profile").value);
  formData.append("user_instruction", document.querySelector("#user-instruction").value);

  loading.hidden = false;
  submitButton.disabled = true;

  try {
    const response = await fetch("/demo/analyze-and-respond", {
      method: "POST",
      body: formData,
    });
    const payload = await response.json();

    if (!response.ok) {
      showError(payload.detail || "Não foi possível analisar o áudio.");
      return;
    }

    renderResult(payload);
  } catch (error) {
    showError("Erro de comunicação com o app demo. Verifique se o servidor está rodando.");
  } finally {
    loading.hidden = true;
    submitButton.disabled = false;
  }
});

async function startRecording() {
  clearError();
  if (!navigator.mediaDevices || !window.MediaRecorder) {
    showError("Este navegador não suporta gravação de áudio com MediaRecorder.");
    return;
  }

  try {
    clearRecording({
      clearUpload: true,
      clearResults: true,
      statusMessage: "Preparando microfone...",
    });

    mediaStream = await getAudioStream();
    selectedRecorderMimeType = chooseRecorderMimeType();

    try {
      mediaRecorder = selectedRecorderMimeType
        ? new MediaRecorder(mediaStream, { mimeType: selectedRecorderMimeType })
        : new MediaRecorder(mediaStream);
    } catch (error) {
      mediaRecorder = new MediaRecorder(mediaStream);
      selectedRecorderMimeType = mediaRecorder.mimeType || "";
    }

    recordedChunks = [];
    recordingMime.textContent = `MIME usado: ${
      mediaRecorder.mimeType || selectedRecorderMimeType || "Padrão do navegador"
    }`;

    mediaRecorder.addEventListener("dataavailable", (event) => {
      if (event.data && event.data.size > 0) {
        recordedChunks.push(event.data);
      }
    });

    mediaRecorder.addEventListener("stop", finishRecording, { once: true });

    mediaRecorder.start(1000);
    startRecordingTimer();
    recordingStatus.textContent = "Gravando...";
    startRecordingButton.disabled = true;
    stopRecordingButton.disabled = false;
    clearRecordingButton.disabled = true;
  } catch (error) {
    stopMediaStream();
    stopRecordingTimer(true);
    startRecordingButton.disabled = false;
    stopRecordingButton.disabled = true;
    clearRecordingButton.disabled = !fileInput.files?.[0];
    recordingStatus.textContent = "Não foi possível iniciar a gravação.";
    showError("Não foi possível acessar o microfone.");
  }
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state !== "inactive") {
    if (typeof mediaRecorder.requestData === "function") {
      mediaRecorder.requestData();
    }
    mediaRecorder.stop();
  }
  startRecordingButton.disabled = false;
  stopRecordingButton.disabled = true;
}

startRecordingButton.addEventListener("click", startRecording);
stopRecordingButton.addEventListener("click", stopRecording);
clearRecordingButton.addEventListener("click", () =>
  clearRecording({ clearUpload: true, clearResults: true })
);

loadStatus();
