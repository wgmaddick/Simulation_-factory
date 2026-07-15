(() => {
  const els = {
    productName: document.getElementById('productName'),
    creditValue: document.getElementById('creditValue'),
    resetCredits: document.getElementById('resetCredits'),
    nodeSelect: document.getElementById('nodeSelect'),
    nodeDesc: document.getElementById('nodeDesc'),
    speechInput: document.getElementById('speechInput'),
    micBtn: document.getElementById('micBtn'),
    micHint: document.getElementById('micHint'),
    sendBtn: document.getElementById('sendBtn'),
    cameraFeed: document.getElementById('cameraFeed'),
    videoStatus: document.getElementById('videoStatus'),
    results: document.getElementById('results'),
    expertVerdict: document.getElementById('expertVerdict'),
    laymanSummary: document.getElementById('laymanSummary'),
    sentinelPanel: document.getElementById('sentinelPanel'),
    anomalyTitle: document.getElementById('anomalyTitle'),
    anomalyLocation: document.getElementById('anomalyLocation'),
    anomalyDescription: document.getElementById('anomalyDescription'),
    anomalyTimeline: document.getElementById('anomalyTimeline'),
    statusLine: document.getElementById('statusLine'),
  };

  let nodes = [];
  let recognition = null;
  let listening = false;

  function setCredits(value) {
    els.creditValue.textContent = String(value);
    els.creditValue.classList.remove('pulse');
    // Force reflow for pulse restart
    void els.creditValue.offsetWidth;
    els.creditValue.classList.add('pulse');
  }

  function selectedNode() {
    return nodes.find((n) => n.id === els.nodeSelect.value) || null;
  }

  function updateNodeDesc() {
    const node = selectedNode();
    els.nodeDesc.textContent = node
      ? `${node.description} · Cost ${node.credit_cost} credits`
      : '';
  }

  async function loadConfig() {
    const res = await fetch('/api/config');
    if (!res.ok) throw new Error('Failed to load config');
    const data = await res.json();
    if (data.product_name) {
      els.productName.textContent = data.product_name;
      document.title = `${data.product_name}`;
    }
    nodes = Array.isArray(data.research_nodes) ? data.research_nodes : [];
    els.nodeSelect.innerHTML = nodes
      .map((n) => `<option value="${n.id}">${n.label}</option>`)
      .join('');
    setCredits(data.initial_credits ?? '—');
    updateNodeDesc();
  }

  async function initCamera() {
    if (!navigator.mediaDevices?.getUserMedia) {
      els.videoStatus.textContent = 'Camera API unavailable — analysis still runs on Talk + Send.';
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user' },
        audio: false,
      });
      els.cameraFeed.srcObject = stream;
      els.cameraFeed.classList.add('live');
      els.videoStatus.textContent = 'Live capture · spatial tracking ready';
    } catch {
      els.videoStatus.textContent = 'Camera denied — continue with Talk + Send.';
    }
  }

  function setupSpeech() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      els.micBtn.disabled = true;
      els.micHint.textContent = 'Speech recognition not supported — type your query.';
      return;
    }

    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onresult = (event) => {
      let transcript = '';
      for (let i = 0; i < event.results.length; i += 1) {
        transcript += event.results[i][0].transcript;
      }
      els.speechInput.value = transcript.trim();
    };

    recognition.onerror = () => {
      listening = false;
      els.micBtn.setAttribute('aria-pressed', 'false');
      els.micBtn.textContent = 'Hold to talk';
    };

    recognition.onend = () => {
      listening = false;
      els.micBtn.setAttribute('aria-pressed', 'false');
      els.micBtn.textContent = 'Hold to talk';
    };

    const start = () => {
      if (listening) return;
      try {
        recognition.start();
        listening = true;
        els.micBtn.setAttribute('aria-pressed', 'true');
        els.micBtn.textContent = 'Listening…';
      } catch {
        /* already started */
      }
    };

    const stop = () => {
      if (!listening) return;
      recognition.stop();
    };

    els.micBtn.addEventListener('mousedown', start);
    els.micBtn.addEventListener('mouseup', stop);
    els.micBtn.addEventListener('mouseleave', stop);
    els.micBtn.addEventListener('touchstart', (e) => {
      e.preventDefault();
      start();
    });
    els.micBtn.addEventListener('touchend', (e) => {
      e.preventDefault();
      stop();
    });
  }

  function renderResult(data) {
    els.results.hidden = false;
    els.expertVerdict.textContent = data.expertVerdict || '';
    els.laymanSummary.textContent = data.laymanSummary || '';

    if (typeof data.creditsRemaining === 'number') {
      setCredits(data.creditsRemaining);
    }

    if (data.sentinelOverride && data.anomalyData) {
      const a = data.anomalyData;
      els.sentinelPanel.hidden = false;
      els.anomalyTitle.textContent = a.title || 'Anomaly';
      els.anomalyLocation.textContent = a.location || '—';
      els.anomalyDescription.textContent = a.description || '—';
      els.anomalyTimeline.textContent = a.timeline || '—';
      els.statusLine.hidden = true;
    } else {
      els.sentinelPanel.hidden = true;
      els.statusLine.hidden = false;
      els.statusLine.textContent = 'No sentinel override on this pass — pathway within prompted scope.';
    }
  }

  async function sendAnalysis() {
    const node = selectedNode();
    if (!node) return;

    els.sendBtn.disabled = true;
    els.sendBtn.textContent = 'Processing…';
    els.statusLine.hidden = true;

    try {
      const res = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nodeId: node.id,
          userSpeech: els.speechInput.value,
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        els.results.hidden = false;
        els.sentinelPanel.hidden = true;
        els.expertVerdict.textContent = '';
        els.laymanSummary.textContent = '';
        els.statusLine.hidden = false;
        els.statusLine.textContent = data.error || `Request failed (${res.status})`;
        return;
      }
      renderResult(data);
    } catch (err) {
      els.results.hidden = false;
      els.statusLine.hidden = false;
      els.statusLine.textContent = err.message || 'Network error';
    } finally {
      els.sendBtn.disabled = false;
      els.sendBtn.textContent = 'Send analysis';
    }
  }

  els.nodeSelect.addEventListener('change', updateNodeDesc);
  els.sendBtn.addEventListener('click', sendAnalysis);
  els.resetCredits.addEventListener('click', async () => {
    const res = await fetch('/api/reset-credits', { method: 'POST' });
    if (!res.ok) return;
    const data = await res.json();
    setCredits(data.creditsRemaining);
  });

  Promise.all([loadConfig(), initCamera()]).catch((err) => {
    els.videoStatus.textContent = err.message || 'Startup failed';
  });
  setupSpeech();
})();
