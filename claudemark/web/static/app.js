/**
 * ClaudeMark — Web Dashboard, TrueFocus, Specular Button & DotGrid Physics
 * Author: Karthik R Shet (https://github.com/karthikrshet/ClaudeMark)
 */

(function () {
  'use strict';

  /* ==========================================================================
     1. Interactive DotGrid Physics Canvas Engine
     ========================================================================== */

  function hexToRgb(hex) {
    const m = hex.match(/^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i);
    if (!m) return { r: 51, g: 65, b: 85 };
    return {
      r: parseInt(m[1], 16),
      g: parseInt(m[2], 16),
      b: parseInt(m[3], 16),
    };
  }

  function initDotGrid() {
    const canvas = document.getElementById('dotGridCanvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const config = {
      dotSize: 3,
      gap: 28,
      baseColor: '#162036',
      activeColor: '#5227ff',
      proximity: 140,
      speedTrigger: 80,
      shockRadius: 220,
      shockStrength: 18,
      maxSpeed: 4000,
      resistance: 0.92,
      springStiffness: 0.08,
      dampening: 0.85,
    };

    const baseRgb = hexToRgb(config.baseColor);
    const activeRgb = hexToRgb(config.activeColor);

    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    let dots = [];
    const pointer = {
      x: -1000,
      y: -1000,
      vx: 0,
      vy: 0,
      speed: 0,
      lastTime: performance.now(),
      lastX: -1000,
      lastY: -1000,
    };

    function buildGrid() {
      const dpr = window.devicePixelRatio || 1;
      width = window.innerWidth;
      height = window.innerHeight;

      canvas.width = width * dpr;
      canvas.height = height * dpr;
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;
      ctx.scale(dpr, dpr);

      const cell = config.dotSize + config.gap;
      const cols = Math.floor((width + config.gap) / cell);
      const rows = Math.floor((height + config.gap) / cell);

      const gridW = cell * cols - config.gap;
      const gridH = cell * rows - config.gap;
      const startX = (width - gridW) / 2 + config.dotSize / 2;
      const startY = (height - gridH) / 2 + config.dotSize / 2;

      dots = [];
      for (let y = 0; y < rows; y++) {
        for (let x = 0; x < cols; x++) {
          dots.push({
            cx: startX + x * cell,
            cy: startY + y * cell,
            xOffset: 0,
            yOffset: 0,
            vx: 0,
            vy: 0,
          });
        }
      }
    }

    buildGrid();
    window.addEventListener('resize', buildGrid);

    window.addEventListener('mousemove', (e) => {
      const now = performance.now();
      const dt = Math.max(1, now - pointer.lastTime);
      const dx = e.clientX - pointer.lastX;
      const dy = e.clientY - pointer.lastY;

      let vx = (dx / dt) * 1000;
      let vy = (dy / dt) * 1000;
      let speed = Math.hypot(vx, vy);

      if (speed > config.maxSpeed) {
        const scale = config.maxSpeed / speed;
        vx *= scale;
        vy *= scale;
        speed = config.maxSpeed;
      }

      pointer.lastTime = now;
      pointer.lastX = e.clientX;
      pointer.lastY = e.clientY;
      pointer.x = e.clientX;
      pointer.y = e.clientY;
      pointer.vx = vx;
      pointer.vy = vy;
      pointer.speed = speed;

      for (let i = 0; i < dots.length; i++) {
        const dot = dots[i];
        const dist = Math.hypot(dot.cx - pointer.x, dot.cy - pointer.y);
        if (speed > config.speedTrigger && dist < config.proximity) {
          const pushFactor = (1 - dist / config.proximity) * 0.35;
          dot.vx += (dot.cx - pointer.x) * pushFactor + vx * 0.008;
          dot.vy += (dot.cy - pointer.y) * pushFactor + vy * 0.008;
        }
      }
    }, { passive: true });

    window.addEventListener('click', (e) => {
      const cx = e.clientX;
      const cy = e.clientY;
      for (let i = 0; i < dots.length; i++) {
        const dot = dots[i];
        const dist = Math.hypot(dot.cx - cx, dot.cy - cy);
        if (dist < config.shockRadius && dist > 0) {
          const falloff = 1 - dist / config.shockRadius;
          const force = config.shockStrength * falloff;
          const angle = Math.atan2(dot.cy - cy, dot.cx - cx);
          dot.vx += Math.cos(angle) * force * 4;
          dot.vy += Math.sin(angle) * force * 4;
        }
      }
    });

    const proxSq = config.proximity * config.proximity;
    function render() {
      ctx.clearRect(0, 0, width, height);

      const px = pointer.x;
      const py = pointer.y;

      for (let i = 0; i < dots.length; i++) {
        const dot = dots[i];

        const springX = -dot.xOffset * config.springStiffness;
        const springY = -dot.yOffset * config.springStiffness;
        dot.vx = (dot.vx + springX) * config.dampening;
        dot.vy = (dot.vy + springY) * config.dampening;
        dot.xOffset += dot.vx;
        dot.yOffset += dot.vy;

        const ox = dot.cx + dot.xOffset;
        const oy = dot.cy + dot.yOffset;

        const dx = dot.cx - px;
        const dy = dot.cy - py;
        const dsq = dx * dx + dy * dy;

        let fillStyle = config.baseColor;
        if (dsq <= proxSq) {
          const t = 1 - Math.sqrt(dsq) / config.proximity;
          const r = Math.round(baseRgb.r + (activeRgb.r - baseRgb.r) * t);
          const g = Math.round(baseRgb.g + (activeRgb.g - baseRgb.g) * t);
          const b = Math.round(baseRgb.b + (activeRgb.b - baseRgb.b) * t);
          fillStyle = `rgb(${r},${g},${b})`;
        }

        ctx.beginPath();
        ctx.arc(ox, oy, config.dotSize / 2, 0, Math.PI * 2);
        ctx.fillStyle = fillStyle;
        ctx.fill();
      }

      requestAnimationFrame(render);
    }

    requestAnimationFrame(render);
  }

  /* ==========================================================================
     2. TrueFocus Headline Focus Animation
     ========================================================================== */

  function initTrueFocus() {
    const container = document.getElementById('trueFocusContainer');
    const frame = document.getElementById('trueFocusFrame');
    if (!container || !frame) return;

    const words = container.querySelectorAll('.focus-word');
    if (!words.length) return;

    let currentIndex = 0;
    let isHovered = false;

    function updateFrame(index) {
      if (index < 0 || index >= words.length) return;
      const targetWord = words[index];
      const parentRect = container.getBoundingClientRect();
      const wordRect = targetWord.getBoundingClientRect();

      const x = wordRect.left - parentRect.left;
      const y = wordRect.top - parentRect.top;

      frame.style.transform = `translate(${x}px, ${y}px)`;
      frame.style.width = `${wordRect.width}px`;
      frame.style.height = `${wordRect.height}px`;
      frame.style.opacity = '1';

      words.forEach((w, idx) => {
        if (idx === index) {
          w.style.filter = 'blur(0px)';
          w.style.opacity = '1';
        } else {
          w.style.filter = 'blur(3px)';
          w.style.opacity = '0.55';
        }
      });
    }

    // Auto-cycle through words
    const interval = setInterval(() => {
      if (!isHovered) {
        currentIndex = (currentIndex + 1) % words.length;
        updateFrame(currentIndex);
      }
    }, 2200);

    words.forEach((w, idx) => {
      w.addEventListener('mouseenter', () => {
        isHovered = true;
        currentIndex = idx;
        updateFrame(idx);
      });
      w.addEventListener('mouseleave', () => {
        isHovered = false;
      });
    });

    // Initial position
    setTimeout(() => updateFrame(0), 100);
    window.addEventListener('resize', () => updateFrame(currentIndex));
  }

  /* ==========================================================================
     3. Specular Button Pointer Rim Glow Effect
     ========================================================================== */

  function initSpecularButtons() {
    const buttons = document.querySelectorAll('.btn-primary, .btn-specular');
    buttons.forEach((btn) => {
      btn.addEventListener('mousemove', (e) => {
        const rect = btn.getBoundingClientRect();
        const x = ((e.clientX - rect.left) / rect.width) * 100;
        const y = ((e.clientY - rect.top) / rect.height) * 100;
        btn.style.boxShadow = `0 4px 20px rgba(82, 39, 255, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.25)`;
      });
      btn.addEventListener('mouseleave', () => {
        btn.style.boxShadow = '';
      });
    });
  }

  /* ==========================================================================
     4. Tab Controller
     ========================================================================== */

  function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanels = document.querySelectorAll('.tab-panel');

    tabBtns.forEach((btn) => {
      btn.addEventListener('click', () => {
        const targetId = btn.getAttribute('data-tab');
        tabBtns.forEach((b) => b.classList.remove('active'));
        tabPanels.forEach((p) => p.classList.remove('active'));

        btn.classList.add('active');
        const targetPanel = document.getElementById(targetId);
        if (targetPanel) targetPanel.classList.add('active');
      });
    });
  }

  /* ==========================================================================
     5. Text Analyzer & Results Rendering
     ========================================================================== */

  function initTextAnalyzer() {
    const textInput = document.getElementById('textInput');
    const btnAnalyze = document.getElementById('btnAnalyze');
    const btnClear = document.getElementById('btnClear');
    const btnLoadFile = document.getElementById('fileLoader');
    const btnLoadFileTrigger = document.getElementById('btnLoadFile');
    const liveCharCount = document.getElementById('liveCharCount');
    const liveWordCount = document.getElementById('liveWordCount');
    const resultsDashboard = document.getElementById('resultsDashboard');

    const presetClean = document.getElementById('presetClean');
    const presetHidden = document.getElementById('presetHidden');
    const presetAI = document.getElementById('presetAI');

    if (textInput && liveCharCount && liveWordCount) {
      const updateCounts = () => {
        const val = textInput.value;
        liveCharCount.textContent = `${val.length.toLocaleString()} characters`;
        const words = val.trim() ? val.trim().split(/\s+/).length : 0;
        liveWordCount.textContent = `${words.toLocaleString()} words`;
      };
      textInput.addEventListener('input', updateCounts);

      if (presetClean) {
        presetClean.addEventListener('click', () => {
          textInput.value = "The exploration of distributed cryptographic architectures requires a rigorous understanding of consensus bounds and zero-knowledge verification.";
          updateCounts();
        });
      }
      if (presetHidden) {
        presetHidden.addEventListener('click', () => {
          textInput.value = "This\u200b sentence\u200c contains\u200d invisible\uFEFF zero-width\u2060 watermark\u200B steganography tokens embedded throughout.";
          updateCounts();
        });
      }
      if (presetAI) {
        presetAI.addEventListener('click', () => {
          textInput.value = "It is important to note that delving into the multifaceted intricacies of artificial intelligence requires a comprehensive approach. Furthermore, one must consider the delicate tapestry of statistical distributions.";
          updateCounts();
        });
      }
    }

    if (btnLoadFileTrigger && btnLoadFile) {
      btnLoadFileTrigger.addEventListener('click', () => btnLoadFile.click());
      btnLoadFile.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
          const reader = new FileReader();
          reader.onload = (evt) => {
            textInput.value = evt.target.result;
            if (textInput.oninput) textInput.oninput();
          };
          reader.readAsText(file);
        }
      });
    }

    if (btnClear && textInput) {
      btnClear.addEventListener('click', () => {
        textInput.value = '';
        if (textInput.oninput) textInput.oninput();
        if (resultsDashboard) resultsDashboard.style.display = 'none';
      });
    }

    if (btnAnalyze && textInput) {
      btnAnalyze.addEventListener('click', async () => {
        const text = textInput.value.trim();
        if (!text) return alert('Please enter or load text to analyze.');

        const algSelect = document.getElementById('algorithmSelect');
        const alg = algSelect ? algSelect.value : 'claude';

        btnAnalyze.disabled = true;
        btnAnalyze.textContent = 'Analyzing...';

        try {
          const resp = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, algorithm: alg }),
          });
          const data = await resp.json();
          renderAnalysisResults(data);
        } catch (err) {
          alert(`Analysis error: ${err.message}`);
        } finally {
          btnAnalyze.disabled = false;
          btnAnalyze.textContent = 'Analyze Text';
        }
      });
    }
  }

  function renderAnalysisResults(data) {
    const dashboard = document.getElementById('resultsDashboard');
    if (!dashboard) return;
    dashboard.style.display = 'flex';

    const wm = data.watermark_analysis || {};
    const uni = data.unicode_forensics || {};
    const stats = data.text_statistics || {};

    const scoreElem = document.getElementById('statScoreValue');
    const pillElem = document.getElementById('statusPill');
    const confElem = document.getElementById('confidenceLevel');
    const uCountElem = document.getElementById('unicodeAnomaliesCount');
    const entropyElem = document.getElementById('entropyValue');
    const burstElem = document.getElementById('burstinessValue');

    if (scoreElem) scoreElem.textContent = Number(wm.score || 0).toFixed(2);
    if (confElem) confElem.textContent = wm.confidence || 'LOW';
    if (uCountElem) uCountElem.textContent = uni.total_anomalies || 0;
    if (entropyElem) entropyElem.textContent = Number(stats.entropy || 0).toFixed(2);
    if (burstElem) burstElem.textContent = Number(stats.burstiness || 0).toFixed(2);

    if (pillElem) {
      if (wm.is_watermarked || (uni.total_anomalies && uni.total_anomalies > 0)) {
        pillElem.className = 'status-pill status-danger';
        pillElem.textContent = 'Detected Anomaly';
      } else {
        pillElem.className = 'status-pill status-clean';
        pillElem.textContent = 'Clean / Low Signal';
      }
    }
  }

  /* ==========================================================================
     6. Unicode Visualizer & Cleaner
     ========================================================================== */

  function initUnicodeVisualizer() {
    const btnVisualize = document.getElementById('btnVisualizeUnicode');
    const btnCleanUnicode = document.getElementById('btnCleanUnicode');
    const uniInput = document.getElementById('unicodeInput');
    const uniOutput = document.getElementById('unicodeOutput');

    if (btnVisualize && uniInput && uniOutput) {
      btnVisualize.addEventListener('click', async () => {
        const text = uniInput.value;
        if (!text) return;
        try {
          const resp = await fetch('/api/unicode/visualize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text }),
          });
          const data = await resp.json();
          const safeEscaped = data.visualized
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/&lt;(ZWSP|ZWNJ|ZWJ|BOM|RLO|LRO|PDF|WJ|SHY|NBSP|NNBSP|MMSP)&gt;/g, '<span class="unicode-tag">&lt;$1&gt;</span>');
          uniOutput.innerHTML = safeEscaped;
        } catch (err) {
          alert(`Visualization error: ${err.message}`);
        }
      });
    }

    if (btnCleanUnicode && uniInput && uniOutput) {
      btnCleanUnicode.addEventListener('click', async () => {
        const text = uniInput.value;
        if (!text) return;
        try {
          const resp = await fetch('/api/normalize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, strip_zero_width: true }),
          });
          const data = await resp.json();
          uniOutput.textContent = data.normalized_text;
        } catch (err) {
          alert(`Clean error: ${err.message}`);
        }
      });
    }
  }

  /* ==========================================================================
     7. File Inspector & Provenance Cleaner
     ========================================================================== */

  function initFileCleaner() {
    const dropZone = document.getElementById('cleanerDropZone');
    const fileInput = document.getElementById('cleanerFileInput');
    const cleanResults = document.getElementById('cleanerResults');

    if (!dropZone || !fileInput) return;

    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropZone.classList.add('dragover');
    });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropZone.classList.remove('dragover');
      if (e.dataTransfer.files.length) handleFileClean(e.dataTransfer.files[0]);
    });

    fileInput.addEventListener('change', (e) => {
      if (e.target.files.length) handleFileClean(e.target.files[0]);
    });

    async function handleFileClean(file) {
      const reader = new FileReader();
      reader.onload = async (evt) => {
        const base64Data = evt.target.result.split(',')[1];
        try {
          const resp = await fetch('/clean', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: file.name, file: base64Data }),
          });
          const res = await resp.json();
          if (cleanResults) {
            cleanResults.style.display = 'block';
            cleanResults.innerHTML = `
              <div class="card" style="margin-top: 1rem;">
                <h3>File Cleaning Report: ${file.name}</h3>
                <div class="metric-grid" style="margin-top: 0.75rem;">
                  <div class="metric-box"><span class="metric-title">Original Size</span><span class="metric-value">${(file.size / 1024).toFixed(1)} KB</span></div>
                  <div class="metric-box"><span class="metric-title">Cleaned Size</span><span class="metric-value">${((res.cleaned_size_bytes || file.size) / 1024).toFixed(1)} KB</span></div>
                  <div class="metric-box"><span class="metric-title">Status</span><span class="metric-value" style="color:var(--color-success)">Cleaned</span></div>
                </div>
                <div style="margin-top: 1.25rem;">
                  <a href="data:application/octet-stream;base64,${res.cleaned_file_base64}" download="clean_${file.name}" class="btn btn-primary btn-specular">Download Cleaned File</a>
                </div>
              </div>
            `;
          }
        } catch (err) {
          alert(`File cleaning error: ${err.message}`);
        }
      };
      reader.readAsDataURL(file);
    }
  }

  /* ==========================================================================
     8. Forensic Diff & Audit Handlers
     ========================================================================== */

  function initDiffHandler() {
    const btnDiff = document.getElementById('btnComputeDiff');
    const origInput = document.getElementById('diffOriginal');
    const procInput = document.getElementById('diffProcessed');
    const outContainer = document.getElementById('diffOutputContainer');

    if (btnDiff && origInput && procInput && outContainer) {
      btnDiff.addEventListener('click', async () => {
        const original = origInput.value;
        const processed = procInput.value;
        if (!original || !processed) return alert('Please provide both original and processed text.');

        btnDiff.disabled = true;
        btnDiff.textContent = 'Computing...';
        try {
          const resp = await fetch('/api/diff', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ original, processed }),
          });
          const data = await resp.json();
          const d = data.diff || {};
          outContainer.style.display = 'block';
          outContainer.innerHTML = `
            <div class="metric-grid">
              <div class="metric-box"><span class="metric-title">Similarity Ratio</span><span class="metric-value">${(d.visible_similarity_ratio * 100).toFixed(1)}%</span></div>
              <div class="metric-box"><span class="metric-title">Anomalies Removed</span><span class="metric-value" style="color:var(--color-success)">${d.anomalies_removed || 0}</span></div>
              <div class="metric-box"><span class="metric-title">Character Delta</span><span class="metric-value">${d.char_delta >= 0 ? '+' : ''}${d.char_delta}</span></div>
              <div class="metric-box"><span class="metric-title">Word Delta</span><span class="metric-value">${d.word_delta >= 0 ? '+' : ''}${d.word_delta}</span></div>
            </div>
            <div class="visual-tag-box" style="margin-top: 1rem;">
              <pre>${d.summary || 'Forensic comparison completed.'}</pre>
            </div>
          `;
        } catch (err) {
          alert(`Diff error: ${err.message}`);
        } finally {
          btnDiff.disabled = false;
          btnDiff.textContent = 'Compute Forensic Diff';
        }
      });
    }
  }

  function initAuditHandler() {
    const btnAudit = document.getElementById('btnRunAudit');
    const pathInput = document.getElementById('auditPathInput');
    const outElem = document.getElementById('auditReportOutput');

    if (btnAudit && pathInput && outElem) {
      btnAudit.addEventListener('click', async () => {
        const targetPath = pathInput.value.trim() || '.';
        btnAudit.disabled = true;
        btnAudit.textContent = 'Auditing...';
        try {
          const resp = await fetch('/api/agent/exec', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              tool_name: 'audit_directory',
              arguments: { path: targetPath },
            }),
          });
          const res = await resp.json();
          outElem.style.display = 'block';
          if (res.ok && res.result) {
            const r = res.result;
            outElem.innerHTML = `
              <div class="metric-grid">
                <div class="metric-box"><span class="metric-title">Files Scanned</span><span class="metric-value">${r.total_files_scanned || 0}</span></div>
                <div class="metric-box"><span class="metric-title">Suspicious Files</span><span class="metric-value" style="color:${(r.total_suspicious_files || 0) > 0 ? 'var(--color-danger)' : 'var(--color-success)'}">${r.total_suspicious_files || 0}</span></div>
                <div class="metric-box"><span class="metric-title">Unicode Marks</span><span class="metric-value">${r.total_unicode_anomalies || 0}</span></div>
                <div class="metric-box"><span class="metric-title">C2PA Manifests</span><span class="metric-value">${r.total_c2pa_manifests || 0}</span></div>
              </div>
            `;
          } else {
            outElem.innerHTML = `<div class="threat-item"><div class="threat-title">Audit Notice</div><div class="threat-desc">${res.error || 'Audit completed.'}</div></div>`;
          }
        } catch (err) {
          alert(`Audit error: ${err.message}`);
        } finally {
          btnAudit.disabled = false;
          btnAudit.textContent = 'Run Recursive Audit';
        }
      });
    }
  }

  /* ==========================================================================
     9. Bootstrap Initialization
     ========================================================================== */

  document.addEventListener('DOMContentLoaded', () => {
    initDotGrid();
    initTrueFocus();
    initSpecularButtons();
    initTabs();
    initTextAnalyzer();
    initUnicodeVisualizer();
    initFileCleaner();
    initDiffHandler();
    initAuditHandler();
  });
})();
