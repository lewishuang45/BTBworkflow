const stateEls = {
  status: document.getElementById('status'),
  mode: document.getElementById('mode'),
  message: document.getElementById('message'),
  started: document.getElementById('started'),
  updated: document.getElementById('updated'),
  activeStepBadge: document.getElementById('activeStepBadge'),
  activeSubstepBadge: document.getElementById('activeSubstepBadge'),
  inputCsv: document.getElementById('inputCsv'),
  reportFlag: document.getElementById('reportFlag'),
  boundaryFlag: document.getElementById('boundaryFlag'),
  imageFlag: document.getElementById('imageFlag'),
  reportPreview: document.getElementById('reportPreview'),
  datasetPreview: document.getElementById('datasetPreview'),
  chartConfigPreview: document.getElementById('chartConfigPreview'),
  chartPreview: document.getElementById('chartPreview'),
  steps: document.getElementById('steps'),
  prompts: document.getElementById('prompts'),
  datasetSelect: document.getElementById('datasetSelect'),
  templateSelect: document.getElementById('templateSelect'),
  schemaEditor: document.getElementById('schemaEditor'),
  templateEditor: document.getElementById('templateEditor'),
  assistantMessage: document.getElementById('assistantMessage'),
  assistantSuggestion: document.getElementById('assistantSuggestion'),
  imagePreviewWrap: document.getElementById('imagePreviewWrap'),
  probeImage: document.getElementById('probeImage'),
  exportHtml: document.getElementById('exportHtml'),
  runReport: document.getElementById('runReport'),
  runImage: document.getElementById('runImage'),
  savePrompts: document.getElementById('savePrompts'),
  resetPrompts: document.getElementById('resetPrompts'),
  resetDashboard: document.getElementById('resetDashboard'),
  assistantSuggest: document.getElementById('assistantSuggest'),
  assistantApply: document.getElementById('assistantApply'),
  assistantUndo: document.getElementById('assistantUndo'),
  saveSchema: document.getElementById('saveSchema'),
  saveTemplate: document.getElementById('saveTemplate'),
  uploadDataset: document.getElementById('uploadDataset'),
};

let promptDrafts = {};
let lastAssistantSuggestion = null;
let refreshBusy = false;

function statusClass(status) {
  return `status-${status || 'pending'}`;
}

function showPageError(message) {
  stateEls.message.textContent = message;
}

function renderOptions(selectEl, items, selectedValue) {
  if (!selectEl) return;
  const values = Array.isArray(items) ? items : [];
  selectEl.innerHTML = values.map((value) => `<option value="${value}">${value}</option>`).join('');
  if (selectedValue && values.includes(selectedValue)) {
    selectEl.value = selectedValue;
  }
}

function renderChartPreview(chartConfig) {
  if (!chartConfig || !chartConfig.group_mean_chart) {
    stateEls.chartPreview.className = 'chart-preview empty';
    stateEls.chartPreview.textContent = 'No chart preview yet';
    return;
  }
  const chart = chartConfig.group_mean_chart;
  const rows = chart.rows || [];
  const series = chart.series || [];
  const maxVal = Math.max(1, ...rows.flatMap((row) => series.map((key) => Number(row[key] || 0))));
  stateEls.chartPreview.className = 'chart-preview';
  stateEls.chartPreview.innerHTML = rows.map((row) => {
    const bars = series.map((key) => {
      const value = Number(row[key] || 0);
      const width = Math.max(4, Math.round((value / maxVal) * 100));
      return `<div class="mini-bar-row"><span>${key}</span><div class="mini-bar"><i style="width:${width}%"></i></div><strong>${value}</strong></div>`;
    }).join('');
    return `<div class="chart-card"><h3>${row.group}</h3>${bars}</div>`;
  }).join('');
}

function renderSteps(steps, activeStep, activeSubstep) {
  stateEls.steps.innerHTML = '';
  (steps || []).forEach((step, index) => {
    const card = document.createElement('div');
    card.className = `step-card ${statusClass(step.status)} ${activeStep === step.id ? 'active' : ''}`;

    const substepsHtml = (step.substeps || []).map((substep) => `
      <div class="substep ${statusClass(substep.status)} ${activeSubstep === substep.id ? 'active' : ''}">
        <span class="substep-dot"></span>
        <div>
          <strong>${substep.label || substep.id || ''}</strong>
          <small>${substep.runtime_message || ''}</small>
        </div>
        <span class="pill ${statusClass(substep.status)}">${substep.status || 'pending'}</span>
      </div>
    `).join('');

    card.innerHTML = `
      <div class="step-index">${index + 1}</div>
      <div class="step-body">
        <div class="step-top">
          <h3>${step.title || step.id || 'Unnamed step'}</h3>
          <span class="pill ${statusClass(step.status)}">${step.status || 'pending'}</span>
        </div>
        <p>${step.detail || ''}</p>
        <small>${step.runtime_message || ''}</small>
        <div class="substeps">${substepsHtml}</div>
      </div>
    `;
    stateEls.steps.appendChild(card);
  });
}

function renderPrompts(prompts) {
  stateEls.prompts.innerHTML = '';
  Object.entries(prompts || {}).forEach(([key, value]) => {
    if (!(key in promptDrafts)) {
      promptDrafts[key] = value;
    }
    const block = document.createElement('div');
    block.className = 'prompt-block';
    block.innerHTML = `<h3>${key}</h3><textarea data-prompt-key="${key}"></textarea>`;
    const textarea = block.querySelector('textarea');
    textarea.value = promptDrafts[key] ?? value;
    textarea.addEventListener('input', (event) => {
      promptDrafts[key] = event.target.value;
    });
    stateEls.prompts.appendChild(block);
  });
}

function renderImagePreview(url, emptyText, wrapEl, alt) {
  if (!url) {
    wrapEl.className = 'image-preview empty';
    wrapEl.textContent = emptyText;
    return;
  }
  const cacheBustedUrl = `${url}?t=${Date.now()}`;
  const existingImg = wrapEl.querySelector('img');
  if (existingImg && existingImg.dataset.src === url) {
    existingImg.src = cacheBustedUrl;
    return;
  }
  wrapEl.className = 'image-preview';
  wrapEl.innerHTML = `<a href="${url}" target="_blank" rel="noopener"><img src="${cacheBustedUrl}" data-src="${url}" alt="${alt}" /></a>`;
}

async function postJson(path, payload = null) {
  const response = await fetch(path, {
    method: 'POST',
    headers: payload ? { 'Content-Type': 'application/json' } : undefined,
    body: payload ? JSON.stringify(payload) : undefined,
  });
  const data = await response.json().catch(() => ({ message: 'Request failed' }));
  if (!response.ok) {
    throw new Error(data.message || data.output || `Request failed: ${response.status}`);
  }
  return data;
}

async function triggerRun(path) {
  try {
    await postJson(path);
    await refresh();
  } catch (error) {
    alert(error.message);
    showPageError(error.message);
  }
}

async function probeImage() {
  try {
    const payload = await postJson('/api/probe/image');
    alert(payload.output || 'Probe completed');
    await refresh();
  } catch (error) {
    alert(error.message);
    showPageError(error.message);
    await refresh();
  }
}

async function savePrompts() {
  try {
    const prompts = {};
    document.querySelectorAll('textarea[data-prompt-key]').forEach((el) => {
      prompts[el.dataset.promptKey] = el.value.trim();
    });
    const payload = await postJson('/api/prompts', { prompts });
    promptDrafts = { ...(payload.prompts || {}) };
    await refresh();
    alert('Prompts saved.');
  } catch (error) {
    alert(error.message);
    showPageError(error.message);
  }
}

async function saveSchema() {
  try {
    const schema = JSON.parse(stateEls.schemaEditor.value || '{}');
    if (stateEls.datasetSelect.value) {
      schema.input_file = stateEls.datasetSelect.value;
    }
    await postJson('/api/schema', { schema });
    await refresh();
    alert('Schema saved.');
  } catch (error) {
    alert(error.message);
    showPageError(error.message);
  }
}

async function saveTemplate() {
  try {
    const template = JSON.parse(stateEls.templateEditor.value || '{}');
    await postJson('/api/template', { template, template_file: stateEls.templateSelect.value || undefined });
    await refresh();
    alert('Template saved.');
  } catch (error) {
    alert(error.message);
    showPageError(error.message);
  }
}

async function uploadDataset() {
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = '.csv,.xlsx';
  input.onchange = async () => {
    const file = input.files?.[0];
    if (!file) return;
    const buffer = await file.arrayBuffer();
    const bytes = new Uint8Array(buffer);
    let binary = '';
    bytes.forEach((b) => { binary += String.fromCharCode(b); });
    const content_base64 = btoa(binary);
    try {
      await postJson('/api/datasets/upload', { file_name: file.name, content_base64 });
      await refresh();
      alert('Dataset uploaded.');
    } catch (error) {
      alert(error.message);
      showPageError(error.message);
    }
  };
  input.click();
}

async function exportHtml() {
  try {
    const payload = await postJson('/api/export/html');
    if (payload.html_report_url) {
      window.open(payload.html_report_url, '_blank');
    }
  } catch (error) {
    alert(error.message);
    showPageError(error.message);
  }
}

async function resetPrompts() {
  try {
    const payload = await postJson('/api/prompts/reset');
    promptDrafts = { ...(payload.prompts || {}) };
    await refresh();
    alert('Prompts reset.');
  } catch (error) {
    alert(error.message);
    showPageError(error.message);
  }
}

async function resetDashboard() {
  try {
    lastAssistantSuggestion = null;
    await postJson('/api/dashboard/reset');
    await refresh();
    alert('Dashboard reset.');
  } catch (error) {
    alert(error.message);
    showPageError(error.message);
  }
}

async function suggestAssistantChange() {
  const message = (stateEls.assistantMessage.value || '').trim();
  if (!message) {
    alert('Please enter a natural-language change request.');
    return;
  }
  try {
    const payload = await postJson('/api/assistant/suggest', { message });
    lastAssistantSuggestion = payload.suggestion;
    stateEls.assistantSuggestion.textContent = JSON.stringify(payload.suggestion, null, 2);
  } catch (error) {
    alert(error.message);
    showPageError(error.message);
  }
}

async function applyAssistantChange() {
  if (!lastAssistantSuggestion) {
    alert('Please generate a suggestion first.');
    return;
  }
  try {
    const result = await postJson('/api/assistant/apply', { suggestion: lastAssistantSuggestion });
    promptDrafts = { ...(result.prompts || {}) };
    await refresh();
    const appliedCount = (result.applied || []).length;
    const skipped = result.skipped || [];
    let msg = `Applied ${appliedCount} change${appliedCount === 1 ? '' : 's'}.`;
    if (skipped.length) {
      msg += `\nSkipped ${skipped.length}:\n` + skipped.map((s) => `- ${s.change?.type || '?'}: ${s.error}`).join('\n');
    }
    if (result.steps_touched) {
      msg += '\nNote: dashboard step structure was updated.';
    }
    alert(msg);
  } catch (error) {
    alert(error.message);
    showPageError(error.message);
  }
}

async function undoAssistantChange() {
  if (!confirm('Undo the most recent assistant change?')) return;
  try {
    const result = await postJson('/api/assistant/undo');
    promptDrafts = { ...(result.prompts || {}) };
    lastAssistantSuggestion = null;
    stateEls.assistantSuggestion.textContent = '';
    await refresh();
    let msg = `Undone: ${result.restored_summary || '(no summary)'}\nRemaining history: ${result.remaining_history}`;
    if (result.steps_touched) msg += '\nDashboard step structure was restored.';
    alert(msg);
  } catch (error) {
    alert(error.message);
    showPageError(error.message);
  }
}

async function refresh() {
  if (refreshBusy) return;
  refreshBusy = true;
  try {
    const response = await fetch('/api/state');
    const data = await response.json();
    const state = data.state || {};
    const running = (state.status || '').toLowerCase() === 'running';

    stateEls.status.textContent = state.status || '-';
    stateEls.mode.textContent = state.mode || '-';
    stateEls.message.textContent = state.message || '-';
    stateEls.started.textContent = state.started_at || '-';
    stateEls.updated.textContent = state.updated_at || '-';
    stateEls.activeStepBadge.textContent = state.active_step || 'No active step';
    stateEls.activeSubstepBadge.textContent = state.active_substep || 'No active substep';
    stateEls.inputCsv.textContent = state.artifacts?.input_csv || 'missing';
    stateEls.reportFlag.textContent = data.has_report ? 'ready' : 'missing';
    stateEls.boundaryFlag.textContent = data.has_boundary ? 'ready' : 'missing';
    stateEls.imageFlag.textContent = data.has_image ? 'ready' : 'missing';
    stateEls.reportPreview.textContent = data.report_preview ? JSON.stringify(data.report_preview, null, 2) : 'No report generated yet.';
    stateEls.datasetPreview.textContent = data.dataset_preview ? JSON.stringify(data.dataset_preview, null, 2) : 'No dataset preview available yet.';
    stateEls.chartConfigPreview.textContent = data.chart_config ? JSON.stringify(data.chart_config, null, 2) : 'No chart config available yet.';
    renderChartPreview(data.chart_config);

    if (data.assistant?.last_request && !stateEls.assistantMessage.value) {
      stateEls.assistantMessage.value = data.assistant.last_request;
    }
    renderOptions(stateEls.datasetSelect, data.dataset_files, data.schema?.input_file);
    renderOptions(stateEls.templateSelect, data.template_files, 'analysis_template.json');
    if (data.schema && document.activeElement !== stateEls.schemaEditor) {
      stateEls.schemaEditor.value = JSON.stringify(data.schema, null, 2);
    }
    if (data.template && document.activeElement !== stateEls.templateEditor) {
      stateEls.templateEditor.value = JSON.stringify(data.template, null, 2);
    }
    if (data.assistant?.last_suggestion) {
      lastAssistantSuggestion = data.assistant.last_suggestion;
      stateEls.assistantSuggestion.textContent = JSON.stringify(data.assistant.last_suggestion, null, 2);
    }

    stateEls.runReport.disabled = running;
    stateEls.runImage.disabled = running || !data.has_report;
    stateEls.probeImage.disabled = running;
    stateEls.exportHtml.disabled = running || !data.has_report;
    stateEls.savePrompts.disabled = running;
    stateEls.saveSchema.disabled = running;
    stateEls.saveTemplate.disabled = running;
    stateEls.uploadDataset.disabled = running;
    stateEls.resetPrompts.disabled = running;
    stateEls.assistantSuggest.disabled = running;
    stateEls.assistantApply.disabled = running || !lastAssistantSuggestion;
    stateEls.assistantUndo.disabled = running;

    renderSteps(state.steps || [], state.active_step, state.active_substep);

    const activeElement = document.activeElement;
    const editingPrompt = !!(activeElement && activeElement.matches && activeElement.matches('textarea[data-prompt-key]'));
    if (!editingPrompt) {
      promptDrafts = { ...(state.prompts || {}) };
      renderPrompts(state.prompts || {});
    }

    renderImagePreview(data.has_image ? '/preview-image' : null, 'No PPT preview yet', stateEls.imagePreviewWrap, 'ppt preview');
  } catch (error) {
    console.error(error);
    showPageError(`Frontend refresh failed: ${error.message}`);
  } finally {
    refreshBusy = false;
  }
}

stateEls.probeImage.addEventListener('click', probeImage);
stateEls.exportHtml.addEventListener('click', exportHtml);
stateEls.runReport.addEventListener('click', () => triggerRun('/api/run/report'));
stateEls.runImage.addEventListener('click', () => triggerRun('/api/run/image'));
stateEls.savePrompts.addEventListener('click', savePrompts);
stateEls.saveSchema.addEventListener('click', saveSchema);
stateEls.saveTemplate.addEventListener('click', saveTemplate);
stateEls.uploadDataset.addEventListener('click', uploadDataset);
stateEls.resetPrompts.addEventListener('click', resetPrompts);
stateEls.resetDashboard.addEventListener('click', resetDashboard);
stateEls.assistantSuggest.addEventListener('click', suggestAssistantChange);
stateEls.assistantApply.addEventListener('click', applyAssistantChange);
stateEls.assistantUndo.addEventListener('click', undoAssistantChange);


refresh();
setInterval(refresh, 2500);
