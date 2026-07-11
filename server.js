const express = require('express');
const path = require('path');
const fs = require('fs');
const crypto = require('crypto');
const app = express();
const PORT = process.env.PORT || 3000;

// Admin key for the proposal portal. Set ADMIN_KEY in Railway/env for production.
const ADMIN_KEY = process.env.ADMIN_KEY || 'changeme';

const DATA_DIR = path.join(__dirname, 'data');
const UPLOADS_DIR = path.join(DATA_DIR, 'uploads');
const DB_FILE = path.join(DATA_DIR, 'proposals.json');
fs.mkdirSync(UPLOADS_DIR, { recursive: true });

app.use(express.json({ limit: '20mb' }));
app.use(express.static(path.join(__dirname, 'public')));
app.use('/uploads', express.static(UPLOADS_DIR));

app.get('/health', (req, res) => res.send('OK'));

// ---------------------------------------------------------------------------
// Existing Lens AI photo-analysis endpoint
// ---------------------------------------------------------------------------
app.post('/api/analyze', async (req, res) => {
  const { apiKey, imageBase64, prompt } = req.body;
  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-opus-4-5-20251001',
        max_tokens: 1000,
        messages: [{ role: 'user', content: [
          { type: 'image', source: { type: 'base64', media_type: 'image/jpeg', data: imageBase64 } },
          { type: 'text', text: prompt }
        ]}]
      })
    });
    const data = await response.json();
    res.json(data);
  } catch (err) {
    res.status(500).json({ error: { message: err.message } });
  }
});

// ---------------------------------------------------------------------------
// Proposal portal — two-sided interactive proposals
//   Admin: create proposals with toggleable line items + before/after images.
//   Client: opens /p/<token>, toggles services, sees live totals + image swaps,
//           submits their selection back.
// Storage: data/proposals.json (JSON file — move to a DB/volume when it grows).
// ---------------------------------------------------------------------------
function loadDb() {
  try { return JSON.parse(fs.readFileSync(DB_FILE, 'utf8')); }
  catch { return { proposals: [] }; }
}
function saveDb(db) {
  fs.writeFileSync(DB_FILE, JSON.stringify(db, null, 2));
}
function requireAdmin(req, res, next) {
  if (req.get('x-admin-key') !== ADMIN_KEY) {
    return res.status(401).json({ error: 'bad admin key' });
  }
  next();
}
const newId = () => crypto.randomBytes(6).toString('hex');

// Upload an image (data URL) → served from /uploads/<file>
app.post('/api/admin/upload', requireAdmin, (req, res) => {
  const { dataUrl } = req.body;
  const m = /^data:image\/(png|jpe?g|webp);base64,(.+)$/.exec(dataUrl || '');
  if (!m) return res.status(400).json({ error: 'expected a png/jpeg/webp data URL' });
  const ext = m[1] === 'jpeg' ? 'jpg' : m[1];
  const file = `${newId()}.${ext}`;
  fs.writeFileSync(path.join(UPLOADS_DIR, file), Buffer.from(m[2], 'base64'));
  res.json({ url: `/uploads/${file}` });
});

// List proposals (admin)
app.get('/api/admin/proposals', requireAdmin, (req, res) => {
  res.json(loadDb().proposals);
});

// Create / update a proposal (admin)
app.post('/api/admin/proposals', requireAdmin, (req, res) => {
  const db = loadDb();
  const p = req.body;
  const items = (p.items || []).map(it => ({
    id: it.id || newId(),
    name: String(it.name || '').slice(0, 200),
    price: Number(it.price) || 0,
    desc: String(it.desc || '').slice(0, 2000),
    roi: String(it.roi || '').slice(0, 2000),          // shown as "what you lose" when toggled off
    required: !!it.required,
    beforeImage: it.beforeImage || '',                  // shown when item is OFF
    afterImage: it.afterImage || ''                     // shown when item is ON
  }));
  let existing = p.id && db.proposals.find(x => x.id === p.id);
  if (existing) {
    Object.assign(existing, {
      clientName: p.clientName || existing.clientName,
      projectName: p.projectName || existing.projectName,
      intro: p.intro ?? existing.intro,
      items
    });
  } else {
    existing = {
      id: newId(),
      token: crypto.randomBytes(12).toString('hex'),
      clientName: p.clientName || 'Client',
      projectName: p.projectName || 'Proposal',
      intro: p.intro || '',
      items,
      submission: null,
      createdAt: new Date().toISOString()
    };
    db.proposals.push(existing);
  }
  saveDb(db);
  res.json(existing);
});

app.delete('/api/admin/proposals/:id', requireAdmin, (req, res) => {
  const db = loadDb();
  db.proposals = db.proposals.filter(p => p.id !== req.params.id);
  saveDb(db);
  res.json({ ok: true });
});

// Client fetch (public, by unguessable token; admin fields stripped)
app.get('/api/p/:token', (req, res) => {
  const p = loadDb().proposals.find(x => x.token === req.params.token);
  if (!p) return res.status(404).json({ error: 'not found' });
  const { id, submission, ...pub } = p;
  res.json({ ...pub, submitted: !!submission });
});

// Client submit (public)
app.post('/api/p/:token/submit', (req, res) => {
  const db = loadDb();
  const p = db.proposals.find(x => x.token === req.params.token);
  if (!p) return res.status(404).json({ error: 'not found' });
  const selected = new Set(req.body.selectedIds || []);
  p.items.filter(it => it.required).forEach(it => selected.add(it.id));
  const chosen = p.items.filter(it => selected.has(it.id));
  p.submission = {
    selectedIds: chosen.map(it => it.id),
    total: chosen.reduce((s, it) => s + it.price, 0),
    note: String(req.body.note || '').slice(0, 2000),
    submittedAt: new Date().toISOString()
  };
  saveDb(db);
  res.json({ ok: true, total: p.submission.total });
});

// Pretty client URL
app.get('/p/:token', (req, res) =>
  res.sendFile(path.join(__dirname, 'public', 'proposal.html')));
app.get('/admin', (req, res) =>
  res.sendFile(path.join(__dirname, 'public', 'admin.html')));

app.listen(PORT, '0.0.0.0', () => console.log(`✅ LENS AI running on port ${PORT}`));
