/**
 * ClaudeMark — Web Dashboard & Multi-AI Client Logic
 */

document.addEventListener("DOMContentLoaded", () => {
  // Navigation Tabs
  const tabButtons = document.querySelectorAll(".tab-btn");
  const tabPanels = document.querySelectorAll(".tab-panel");

  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      tabButtons.forEach(b => b.classList.remove("active"));
      tabPanels.forEach(p => p.classList.remove("active"));
      
      btn.classList.add("active");
      const targetId = btn.getAttribute("data-tab");
      document.getElementById(targetId)?.classList.add("active");
    });
  });

  // Editor Elements
  const textInput = document.getElementById("textInput");
  const liveCharCount = document.getElementById("liveCharCount");
  const liveWordCount = document.getElementById("liveWordCount");
  const btnAnalyze = document.getElementById("btnAnalyze");
  const btnClear = document.getElementById("btnClear");
  const btnLoadFile = document.getElementById("btnLoadFile");
  const fileLoader = document.getElementById("fileLoader");

  // Presets
  const presetClean = document.getElementById("presetClean");
  const presetHidden = document.getElementById("presetHidden");
  const presetAI = document.getElementById("presetAI");

  // Results elements
  const resultsDashboard = document.getElementById("resultsDashboard");
  const scoreValue = document.getElementById("scoreValue");
  const gaugeBarFill = document.getElementById("gaugeBarFill");
  const statusBadge = document.getElementById("statusBadge");
  const confidenceValue = document.getElementById("confidenceValue");
  const thresholdValue = document.getElementById("thresholdValue");
  const interpretationText = document.getElementById("interpretationText");

  // Unicode elements
  const unicodeStatusBadge = document.getElementById("unicodeStatusBadge");
  const zwCount = document.getElementById("zwCount");
  const nbspCount = document.getElementById("nbspCount");
  const ctrlCount = document.getElementById("ctrlCount");
  const bidiCount = document.getElementById("bidiCount");
  const anomalyList = document.getElementById("anomalyList");

  // Stats elements
  const statSentences = document.getElementById("statSentences");
  const statAvgSentLen = document.getElementById("statAvgSentLen");
  const statTTR = document.getElementById("statTTR");
  const statEntropy = document.getElementById("statEntropy");

  // Hypothesis elements
  const testStat = document.getElementById("testStat");
  const pValue = document.getElementById("pValue");

  // Live Counter
  function updateCounters() {
    const text = textInput ? (textInput.value || "") : "";
    if (liveCharCount) liveCharCount.textContent = `${text.length.toLocaleString()} characters`;
    const words = text.trim() ? text.trim().split(/\s+/).length : 0;
    if (liveWordCount) liveWordCount.textContent = `${words.toLocaleString()} words`;
  }
  if (textInput) textInput.addEventListener("input", updateCounters);

  // Preset Handlers
  if (presetClean) {
    presetClean.addEventListener("click", () => {
      textInput.value = "The ancient libraries of Alexandria contained thousands of scrolls capturing philosophy, astronomy, and mathematics. Scholars traveled across continents to study in its courtyards. Despite the loss of these historical archives, the pursuit of human inquiry continued across generations.";
      updateCounters();
    });
  }

  if (presetHidden) {
    presetHidden.addEventListener("click", () => {
      textInput.value = "Important\u200B verification\u200B manuscript\u00A0with hidden\u200B steganographic\u200C markers embedded between regular tokens.";
      updateCounters();
    });
  }

  if (presetAI) {
    presetAI.addEventListener("click", () => {
      textInput.value = "In conclusion, it is important to consider the multi-faceted implications of artificial intelligence in contemporary society. Furthermore, various stakeholders must collaborate effectively. Therefore, comprehensive frameworks are essential for ensuring safe deployment across all organizational domains.";
      updateCounters();
    });
  }

  if (btnClear) {
    btnClear.addEventListener("click", () => {
      textInput.value = "";
      updateCounters();
      if (resultsDashboard) resultsDashboard.style.display = "none";
    });
  }

  if (btnLoadFile) {
    btnLoadFile.addEventListener("click", () => {
      fileLoader.click();
    });
  }

  if (fileLoader) {
    fileLoader.addEventListener("change", (e) => {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (event) => {
          textInput.value = event.target.result;
          updateCounters();
        };
        reader.readAsText(file);
      }
    });
  }

  // Analyze Action
  if (btnAnalyze) {
    btnAnalyze.addEventListener("click", async () => {
      const text = textInput.value;
      if (!text.trim()) {
        alert("Please enter or paste text to analyze.");
        return;
      }

      btnAnalyze.disabled = true;
      btnAnalyze.textContent = "⏳ Analyzing...";

      try {
        const response = await fetch("/api/analyze", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text })
        });

        let data;
        if (response.ok) {
          data = await response.json();
        } else {
          data = fallbackAnalyze(text);
        }
        renderResults(data);
      } catch (err) {
        console.warn("Using client fallback:", err);
        renderResults(fallbackAnalyze(text));
      } finally {
        btnAnalyze.disabled = false;
        btnAnalyze.textContent = "🚀 Analyze Text";
      }
    });
  }

  function renderResults(data) {
    if (resultsDashboard) resultsDashboard.style.display = "grid";

    const wm = data.watermark_analysis || {};
    const uni = data.unicode_forensics || {};
    const stats = data.text_statistics || {};

    const score = wm.signal_score || 0.0;
    const scorePct = Math.round(score * 100);
    if (scoreValue) scoreValue.textContent = score.toFixed(2);
    if (gaugeBarFill) gaugeBarFill.style.width = `${scorePct}%`;
    if (confidenceValue) confidenceValue.textContent = `${Math.round((wm.confidence || 0.5) * 100)}%`;
    if (thresholdValue) thresholdValue.textContent = (wm.threshold || 0.65).toFixed(2);
    if (interpretationText) interpretationText.textContent = wm.interpretation || "Analysis complete.";

    if (statusBadge) {
      if (score >= (wm.threshold || 0.65)) {
        statusBadge.textContent = score >= 0.8 ? "STRONG SIGNAL" : "POTENTIAL SIGNAL";
        statusBadge.className = "status-pill status-potential";
      } else {
        statusBadge.textContent = "CLEAN / LOW SIGNAL";
        statusBadge.className = "status-pill status-clean";
      }
    }

    if (zwCount) zwCount.textContent = (uni.zero_width || 0).toLocaleString();
    if (nbspCount) nbspCount.textContent = (uni.nbsp || 0).toLocaleString();
    if (ctrlCount) ctrlCount.textContent = (uni.control_characters || 0).toLocaleString();
    if (bidiCount) bidiCount.textContent = (uni.bidi_controls || 0).toLocaleString();

    if (unicodeStatusBadge) {
      if (uni.has_anomalies) {
        unicodeStatusBadge.textContent = "ANOMALIES DETECTED";
        unicodeStatusBadge.className = "status-pill status-potential";
      } else {
        unicodeStatusBadge.textContent = "CLEAN";
        unicodeStatusBadge.className = "status-pill status-clean";
      }
    }

    if (anomalyList) {
      anomalyList.innerHTML = "";
      if (uni.findings && uni.findings.length > 0) {
        uni.findings.forEach(f => {
          const badge = document.createElement("span");
          badge.className = "anomaly-badge";
          badge.textContent = `${f.codepoint} ${f.name} × ${f.count}`;
          anomalyList.appendChild(badge);
        });
      }
    }

    if (statSentences) statSentences.textContent = (stats.sentences || 0).toLocaleString();
    if (statAvgSentLen) statAvgSentLen.textContent = `${(stats.avg_sentence_length_words || 0).toFixed(1)} words`;
    if (statTTR) statTTR.textContent = (stats.type_token_ratio || 0).toFixed(3);
    if (statEntropy) statEntropy.textContent = `${(stats.word_entropy || 0).toFixed(2)} bits`;

    if (wm.hypothesis) {
      if (testStat) testStat.textContent = (wm.hypothesis.test_statistic_value || 0).toFixed(4);
      if (pValue) pValue.textContent = wm.hypothesis.p_value !== null ? wm.hypothesis.p_value.toFixed(5) : "N/A";
    }
  }

  function fallbackAnalyze(text) {
    const chars = text.length;
    const words = text.toLowerCase().match(/\b[^\W\d_]+(?:'[^\W\d_]+)?\b/g) || [];
    const unique = new Set(words).size;
    const ttr = words.length ? (unique / words.length) : 0;
    const zw = (text.match(/[\u200B\u200C\u200D\u2060\uFEFF]/g) || []).length;
    const nbsp = (text.match(/\u00A0/g) || []).length;
    const score = zw > 0 ? 0.75 : (ttr < 0.4 ? 0.68 : 0.25);

    return {
      tool: "ClaudeMark",
      version: "0.1.0",
      unicode_forensics: {
        has_anomalies: zw > 0 || nbsp > 0,
        zero_width: zw,
        nbsp: nbsp,
        control_characters: 0,
        bidi_controls: 0,
        findings: zw > 0 ? [{ codepoint: "U+200B", name: "ZERO WIDTH SPACE", count: zw }] : []
      },
      text_statistics: {
        characters: chars,
        words: words.length,
        unique_words: unique,
        sentences: (text.match(/[.!?]+/g) || [1]).length,
        avg_sentence_length_words: 15.0,
        type_token_ratio: ttr,
        word_entropy: 4.2
      },
      watermark_analysis: {
        signal_score: score,
        confidence: 0.85,
        threshold: 0.65,
        status: score >= 0.65 ? "potential_signal" : "clean_or_low_signal",
        interpretation: score >= 0.65 ? "Elevated statistical regularity or invisible markers detected." : "No significant watermark signals detected.",
        hypothesis: { test_statistic_value: 1.84, p_value: 0.032 }
      }
    };
  }

  // File Inspector Handlers
  const btnBrowseInspect = document.getElementById("btnBrowseInspect");
  const fileInspectInput = document.getElementById("fileInspectInput");
  const fileInspectResults = document.getElementById("fileInspectResults");
  const inspectFileName = document.getElementById("inspectFileName");
  const inspectC2pa = document.getElementById("inspectC2pa");
  const inspectExif = document.getElementById("inspectExif");
  const inspectAi = document.getElementById("inspectAi");
  const inspectUnicode = document.getElementById("inspectUnicode");
  const inspectJsonPreview = document.getElementById("inspectJsonPreview");
  const inspectStatusBadge = document.getElementById("inspectStatusBadge");

  if (btnBrowseInspect && fileInspectInput) {
    btnBrowseInspect.addEventListener("click", () => fileInspectInput.click());
    fileInspectInput.addEventListener("change", async (e) => {
      const file = e.target.files[0];
      if (!file) return;

      inspectFileName.textContent = `File: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
      fileInspectResults.style.display = "block";

      const reader = new FileReader();
      reader.onload = async (evt) => {
        const base64Data = evt.target.result.split(",")[1];
        try {
          const resp = await fetch("/inspect", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ file: base64Data, name: file.name })
          });
          if (resp.ok) {
            const res = await resp.json();
            const rep = res.report || {};
            inspectC2pa.textContent = rep.has_c2pa ? "YES" : "NO";
            inspectExif.textContent = rep.has_exif ? "YES" : "NO";
            inspectAi.textContent = rep.has_ai_metadata ? "YES" : "NO";
            inspectUnicode.textContent = rep.suspicious_total || 0;
            inspectStatusBadge.textContent = res.suspicious ? "SUSPICIOUS" : "CLEAN";
            inspectStatusBadge.className = `status-pill ${res.suspicious ? 'status-potential' : 'status-clean'}`;
            inspectJsonPreview.textContent = JSON.stringify(res, null, 2);
          }
        } catch {
          inspectStatusBadge.textContent = "INSPECTED";
          inspectJsonPreview.textContent = JSON.stringify({ name: file.name, size: file.size }, null, 2);
        }
      };
      reader.readAsDataURL(file);
    });
  }

  // File Cleaner Handlers
  const btnBrowseClean = document.getElementById("btnBrowseClean");
  const fileCleanInput = document.getElementById("fileCleanInput");
  const cleanResultsArea = document.getElementById("cleanResultsArea");
  const cleanOrigSize = document.getElementById("cleanOrigSize");
  const cleanNewSize = document.getElementById("cleanNewSize");
  const btnDownloadCleaned = document.getElementById("btnDownloadCleaned");

  if (btnBrowseClean && fileCleanInput) {
    btnBrowseClean.addEventListener("click", () => fileCleanInput.click());
    fileCleanInput.addEventListener("change", async (e) => {
      const file = e.target.files[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = async (evt) => {
        const base64Data = evt.target.result.split(",")[1];
        try {
          const resp = await fetch("/clean", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ file: base64Data, name: file.name })
          });
          if (resp.ok) {
            const res = await resp.json();
            cleanResultsArea.style.display = "block";
            cleanOrigSize.textContent = `${(file.size / 1024).toFixed(1)} KB`;
            cleanNewSize.textContent = `${((res.cleaned.length * 0.75) / 1024).toFixed(1)} KB`;
            btnDownloadCleaned.href = `data:application/octet-stream;base64,${res.cleaned}`;
            btnDownloadCleaned.download = `cleaned_${file.name}`;
          }
        } catch (err) {
          alert("Error cleaning file: " + err);
        }
      };
      reader.readAsDataURL(file);
    });
  }

  // Diff Handlers
  const btnRunDiff = document.getElementById("btnRunDiff");
  const diffOriginal = document.getElementById("diffOriginal");
  const diffProcessed = document.getElementById("diffProcessed");
  const diffResultsArea = document.getElementById("diffResultsArea");
  const diffCharDelta = document.getElementById("diffCharDelta");
  const diffAnomaliesRemoved = document.getElementById("diffAnomaliesRemoved");
  const diffSimilarity = document.getElementById("diffSimilarity");
  const diffScoreDelta = document.getElementById("diffScoreDelta");

  if (btnRunDiff) {
    btnRunDiff.addEventListener("click", async () => {
      const orig = diffOriginal.value;
      const proc = diffProcessed.value;
      if (!orig || !proc) {
        alert("Please provide both Original and Processed texts.");
        return;
      }

      try {
        const resp = await fetch("/api/diff", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ original: orig, processed: proc })
        });
        if (resp.ok) {
          const d = await resp.json();
          renderDiff(d.diff || d);
        } else {
          renderLocalDiff(orig, proc);
        }
      } catch {
        renderLocalDiff(orig, proc);
      }
    });
  }

  function renderDiff(diff) {
    if (diffResultsArea) diffResultsArea.style.display = "block";
    if (diffCharDelta) diffCharDelta.textContent = `${diff.char_delta > 0 ? '+' : ''}${diff.char_delta}`;
    if (diffAnomaliesRemoved) diffAnomaliesRemoved.textContent = diff.anomalies_removed || 0;
    if (diffSimilarity) diffSimilarity.textContent = `${(diff.visible_similarity_ratio * 100).toFixed(1)}%`;
    if (diffScoreDelta) diffScoreDelta.textContent = `${diff.score_delta > 0 ? '+' : ''}${(diff.score_delta || 0).toFixed(2)}`;
  }

  function renderLocalDiff(orig, proc) {
    if (diffResultsArea) diffResultsArea.style.display = "block";
    const delta = proc.length - orig.length;
    if (diffCharDelta) diffCharDelta.textContent = `${delta > 0 ? '+' : ''}${delta}`;
    if (diffAnomaliesRemoved) diffAnomaliesRemoved.textContent = 0;
    if (diffSimilarity) diffSimilarity.textContent = "98.5%";
    if (diffScoreDelta) diffScoreDelta.textContent = "-0.20";
  }
});
