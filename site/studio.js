'use strict';
(() => {
  const KEY = 'freeclaw-studio-v02-projects';
  const MAX_FILE = 1024 * 1024;
  const templates = {
    'docs/product-brief.md': '# Product Brief\n\n**Status:** Draft - human approval required\n\n## Problema e evidências\n[Descreva o problema]\n\n## Usuários e objetivos\n[Descreva o público e indicadores]\n\n## Escopo e exclusões\n[Defina o MVP]\n\n## Riscos e restrições\n[Descreva riscos, privacidade e custos]\n\n## Aprovação humana\nPendente\n',
    'docs/prd.md': '# Product Requirements Document\n\n**Status:** Draft - human approval required\n\n| ID | Requisito | Critério de aceite | Status |\n|---|---|---|---|\n| RF-001 | [Comportamento observável] | AC-001 | Draft |\n| RNF-001 | [Qualidade mensurável] | [Método de teste] | Draft |\n\n## Questões abertas\n[Decisões pendentes]\n',
    'docs/hld.md': '# High-Level Design\n\n**Status:** Draft\n\n## Componentes\n[Descreva componentes e limites de confiança]\n\n## Diagrama\n[Documente a arquitetura]\n\n## Decisões e alternativas\n[Registrar ADR]\n',
    'docs/lld.md': '# Low-Level Design\n\n**Status:** Draft\n\n## Interfaces\n[Endpoints, entradas e saídas]\n\n## Entidades e regras\n[Modelo de dados e validações]\n\n## Estratégia de testes\n[Critérios de aceite e evidências]\n',
    'specs/feature-spec.md': '# Feature Specification\n\n**Status:** Draft\n**Requirement:** RF-001\n\n## User story\nComo [papel], quero [funcionalidade], para [resultado].\n\n## Acceptance criteria\n- AC-001: Given ... When ... Then ...\n\n## Revisão humana\nPendente\n'
  };
  const $ = id => document.getElementById(id);
  const docPaths = Object.keys(templates);
  let projects = [];
  let active = '';
  let timer;
  function id() { return 'p-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 8); }
  function newProject(name, goal) {
    const docs = {};
    for (const [path, body] of Object.entries(templates)) docs[path] = body;
    docs['docs/product-brief.md'] = docs['docs/product-brief.md'].replace('# Product Brief', '# Product Brief - ' + name);
    if (goal) docs['docs/product-brief.md'] = docs['docs/product-brief.md'].replace('[Descreva o problema]', goal);
    return { id: id(), name, goal, docs, tasks: [], createdAt: new Date().toISOString() };
  }
  function validProject(p) {
    return p && typeof p === 'object' && typeof p.id === 'string' && typeof p.name === 'string' && p.name.length <= 90 &&
      typeof p.goal === 'string' && p.goal.length <= 280 &&
      p.docs && typeof p.docs === 'object' && !Array.isArray(p.docs) &&
      docPaths.every(k => typeof p.docs[k] === 'string' && p.docs[k].length < 200000) &&
      Array.isArray(p.tasks) && p.tasks.length <= 500 &&
      p.tasks.every(t => t && typeof t.id === 'string' && typeof t.title === 'string' && t.title.length <= 180 && typeof t.done === 'boolean');
  }
  function load() {
    try {
      const raw = JSON.parse(localStorage.getItem(KEY) || '[]');
      projects = Array.isArray(raw) ? raw.filter(validProject).slice(0, 40) : [];
    } catch { projects = []; toast('Backup local não pôde ser lido.'); }
    if (!projects.length) projects = [newProject('Sistema Acadêmico - exemplo', 'Gerenciar estudantes fictícios seguindo SPECTION')];
    active = projects[0].id;
    persist();
  }
  function current() { return projects.find(p => p.id === active) || projects[0]; }
  function persist() {
    try { localStorage.setItem(KEY, JSON.stringify(projects)); return true; }
    catch { toast('Não foi possível salvar. Exporte um backup e verifique o espaço do navegador.'); return false; }
  }
  function toast(message) {
    const el = $('toast'); el.textContent = message; el.classList.add('show');
    clearTimeout(timer); timer = setTimeout(() => el.classList.remove('show'), 3600);
  }
  function render() {
    const select = $('project-select'); select.replaceChildren();
    for (const p of projects) {
      const o = new Option(p.name, p.id); select.add(o);
    }
    if (!projects.some(p => p.id === active)) active = projects[0].id;
    select.value = active;
    const docSelect = $('doc-select'); const selectedDoc = docSelect.value;
    docSelect.replaceChildren();
    for (const path of docPaths) docSelect.add(new Option(path, path));
    docSelect.value = docPaths.includes(selectedDoc) ? selectedDoc : docPaths[0];
    $('doc-editor').value = current().docs[docSelect.value];
    $('project-count').textContent = String(projects.length);
    $('document-count').textContent = String(Object.keys(current().docs).length);
    $('task-count').textContent = current().tasks.filter(t => t.done).length + ' / ' + current().tasks.length;
    renderTasks();
  }
  function renderTasks() {
    const list = $('task-list'); list.replaceChildren();
    if (!current().tasks.length) {
      const empty = document.createElement('li'); empty.textContent = 'Nenhuma tarefa cadastrada neste projeto.'; list.append(empty);
    }
    for (const task of current().tasks) {
      const li = document.createElement('li');
      const label = document.createElement('label');
      const cb = document.createElement('input'); cb.type = 'checkbox'; cb.checked = task.done;
      const span = document.createElement('span'); span.textContent = task.title; if (task.done) span.classList.add('complete');
      cb.addEventListener('change', () => { task.done = cb.checked; persist(); render(); });
      label.append(cb, span);
      const remove = document.createElement('button'); remove.className = 'btn danger'; remove.type = 'button'; remove.textContent = 'Excluir';
      remove.setAttribute('aria-label', 'Excluir tarefa ' + task.title);
      remove.addEventListener('click', () => { current().tasks = current().tasks.filter(t => t.id !== task.id); persist(); render(); });
      li.append(label, remove); list.append(li);
    }
  }
  function changeView(view) {
    document.querySelectorAll('.view').forEach(x => x.classList.toggle('hidden', x.id !== view));
    document.querySelectorAll('.nav').forEach(x => x.classList.toggle('active', x.dataset.view === view));
  }
  function download(filename, content, type) {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob); const a = document.createElement('a');
    a.href = url; a.download = filename; document.body.append(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  function slug(name) {
    return name.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 55) || 'projeto';
  }
  function exportDocs() {
    const p = current(); const parts = ['# SPECTION - ' + p.name, '', '> Pacote Markdown exportado do FreeClaw AI Studio. Divida pelos caminhos indicados antes de usar com o kit SPECTION.', ''];
    for (const [path, body] of Object.entries(p.docs)) {
      parts.push('---', '', '## Arquivo: ' + path, '', body, '');
    }
    parts.push('---', '', '## Tarefas', '', ...p.tasks.map(t => '- [' + (t.done ? 'x' : ' ') + '] ' + t.title));
    download(slug(p.name) + '-spection.md', parts.join('\n'), 'text/markdown;charset=utf-8');
  }
  document.querySelectorAll('.nav').forEach(b => b.addEventListener('click', () => changeView(b.dataset.view)));
  document.querySelectorAll('.jump').forEach(b => b.addEventListener('click', () => changeView(b.dataset.target)));
  $('project-select').addEventListener('change', e => { active = e.target.value; render(); });
  $('create-project').addEventListener('click', () => {
    const name = $('project-name').value.trim(), goal = $('project-goal').value.trim();
    if (!name) { toast('Informe um nome para o projeto.'); $('project-name').focus(); return; }
    if (projects.length >= 40) { toast('Limite local de 40 projetos. Exporte e limpe projetos antes de continuar.'); return; }
    const p = newProject(name, goal); projects.push(p); active = p.id; persist(); render();
    $('project-name').value = ''; $('project-goal').value = ''; toast('Projeto criado localmente.'); changeView('specifications');
  });
  $('delete-project').addEventListener('click', () => {
    const p = current(); if (!confirm('Excluir o projeto "' + p.name + '" deste navegador? Exporte um backup antes.')) return;
    projects = projects.filter(x => x.id !== p.id);
    if (!projects.length) projects = [newProject('Novo projeto', '')];
    active = projects[0].id; persist(); render(); toast('Projeto removido do armazenamento local.');
  });
  $('doc-select').addEventListener('change', e => { $('doc-editor').value = current().docs[e.target.value]; });
  $('doc-editor').addEventListener('input', e => {
    current().docs[$('doc-select').value] = e.target.value;
    $('save-state').textContent = persist() ? 'Salvo neste navegador' : 'Erro de armazenamento';
  });
  $('download-doc').addEventListener('click', () => {
    const file = $('doc-select').value.split('/').pop(); download(slug(current().name) + '-' + file, current().docs[$('doc-select').value], 'text/markdown;charset=utf-8');
  });
  $('task-form').addEventListener('submit', e => {
    e.preventDefault(); const title = $('task-title').value.trim(); if (!title) return;
    if (current().tasks.length >= 500) { toast('Limite de tarefas atingido.'); return; }
    current().tasks.push({ id: id(), title, done: false }); $('task-title').value = ''; persist(); render();
  });
  $('export-json').addEventListener('click', () => download('freeclaw-studio-backup.json', JSON.stringify({ format: 'freeclaw-studio-v02', projects }, null, 2), 'application/json;charset=utf-8'));
  $('export-md').addEventListener('click', exportDocs);
  $('import-json').addEventListener('change', async e => {
    const file = e.target.files[0]; if (!file) return;
    try {
      if (file.size > MAX_FILE) throw new Error('Arquivo excede 1 MB');
      const data = JSON.parse(await file.text());
      if (data.format !== 'freeclaw-studio-v02' || !Array.isArray(data.projects) || data.projects.length > 40 || !data.projects.every(validProject)) throw new Error('Formato de backup inválido');
      if (!confirm('Substituir os projetos locais pelo conteúdo do backup?')) return;
      projects = data.projects.length ? data.projects : [newProject('Novo projeto', '')]; active = projects[0].id;
      persist(); render(); toast('Backup importado.');
    } catch(err) { toast('Falha na importação: ' + err.message); }
    finally { e.target.value = ''; }
  });
  load(); render();
})();