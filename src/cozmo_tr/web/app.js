const token = document.querySelector('meta[name="cozmo-token"]').content;
const $ = (selector) => document.querySelector(selector);
const controls = () => document.querySelectorAll('[data-command], #command-input, .send');
let connected = false;
let busy = false;

async function api(path, payload) {
  const response = await fetch(path, {
    method: 'POST',
    headers: {'Content-Type': 'application/json', 'X-Cozmo-Token': token},
    body: JSON.stringify(payload || {}),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.message || 'İşlem tamamlanamadı.');
  return data;
}

function setConnected(value) {
  connected = value;
  $('#connection-pill').classList.toggle('online', value);
  $('#connection-pill b').textContent = value ? 'Cozmo bağlı' : 'Bağlı değil';
  $('#display-label').textContent = value ? 'HAZIR' : 'BEKLİYOR';
  $('#connect-button').disabled = value || busy;
  $('#disconnect-button').disabled = !value || busy;
  $('#stop-button').disabled = !value || busy;
  controls().forEach((control) => { control.disabled = !value || busy; });
}

function setBusy(value, message) {
  busy = value;
  document.body.classList.toggle('is-busy', value);
  if (message) showFeedback(message, 'working');
  setConnected(connected);
}

function showFeedback(message, state = 'neutral') {
  const feedback = $('#feedback');
  feedback.textContent = message;
  feedback.dataset.state = state;
}

function addLog(message) {
  const item = document.createElement('li');
  const time = document.createElement('time');
  const text = document.createElement('span');
  time.textContent = new Date().toLocaleTimeString('tr-TR', {hour: '2-digit', minute: '2-digit'});
  text.textContent = message;
  item.append(time, text);
  $('#activity-log').prepend(item);
  while ($('#activity-log').children.length > 6) $('#activity-log').lastElementChild.remove();
}

async function connectRobot() {
  setBusy(true, 'Cozmo’ya bağlanılıyor…');
  try {
    await api('/api/connect');
    setConnected(true);
    showFeedback('Cozmo hazır. Bir komut seç.', 'success');
    addLog('Cozmo bağlantısı kuruldu.');
  } catch (error) { handleError(error); }
  finally { setBusy(false); }
}

async function disconnectRobot() {
  setBusy(true, 'Bağlantı güvenle kapatılıyor…');
  try {
    await api('/api/disconnect');
    setConnected(false);
    showFeedback('Cozmo bağlantısı kapatıldı.');
    addLog('Cozmo bağlantısı kapatıldı.');
  } catch (error) { handleError(error); }
  finally { setBusy(false); }
}

async function executeCommand(text, refreshPhoto = false) {
  if (!text.trim() || !connected || busy) return;
  setBusy(true, `Uygulanıyor: ${text}`);
  try {
    const result = await api('/api/execute', {text});
    showFeedback(result.message, 'success');
    addLog(`“${text}” — ${result.message}`);
    if (refreshPhoto) showLatestPhoto();
  } catch (error) { handleError(error); }
  finally { setBusy(false); }
}

async function listen() {
  if (!connected || busy) return;
  setBusy(true, 'Dinliyorum… Şimdi konuş.');
  $('#listen-button').classList.add('recording');
  try {
    const result = await api('/api/listen', {seconds: 4});
    showFeedback(`“${result.transcript}” — ${result.message}`, 'success');
    addLog(`Duydum: “${result.transcript}”`);
  } catch (error) { handleError(error); }
  finally { $('#listen-button').classList.remove('recording'); setBusy(false); }
}

function showLatestPhoto() {
  const image = $('#camera-preview');
  image.onload = () => { image.hidden = false; $('#camera-empty').hidden = true; };
  image.src = `/api/photo/latest?token=${encodeURIComponent(token)}&t=${Date.now()}`;
}

function handleError(error) {
  const message = error instanceof Error ? error.message : 'Beklenmeyen hata.';
  showFeedback(message, 'error');
  addLog(`Hata: ${message}`);
}

async function loadCapabilities() {
  try {
    const response = await fetch('/api/capabilities');
    const data = await response.json();
    const list = $('#capability-list');
    data.capabilities.forEach((item) => list.append(capabilityCard(item)));
  } catch (error) { handleError(error); }
}

function capabilityCard(item) {
  const card = document.createElement('article');
  const state = document.createElement('span');
  const label = document.createElement('b');
  state.className = `state ${item.state}`;
  state.textContent = item.state === 'hardware_pending' ? 'Donanım testi' : 'Deneysel';
  label.textContent = item.label;
  card.append(label, state);
  return card;
}

function bindControls() {
  $('#connect-button').addEventListener('click', connectRobot);
  $('#disconnect-button').addEventListener('click', disconnectRobot);
  $('#stop-button').addEventListener('click', () => executeCommand('dur'));
  $('#listen-button').addEventListener('click', listen);
  $('#command-form').addEventListener('submit', (event) => {
    event.preventDefault();
    executeCommand($('#command-input').value);
  });
  document.querySelectorAll('[data-command]').forEach((button) => {
    button.addEventListener('click', () => executeCommand(button.dataset.command, button.dataset.photo === 'true'));
  });
}

bindControls();
loadCapabilities();
setConnected(false);
