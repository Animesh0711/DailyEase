// API_BASE is defined in config.js

document.addEventListener('DOMContentLoaded', () => {
    loadAdminNewspapers();
    loadAdminMilk();

    document.getElementById('addNewspaperForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const form = e.target;
        const payload = Object.fromEntries(new FormData(form).entries());
        // convert numeric fields
        payload.price_daily = parseFloat(payload.price_daily);
        payload.price_weekly = parseFloat(payload.price_weekly);
        payload.price_monthly = parseFloat(payload.price_monthly);
        const res = await fetch(`${API_BASE}/admin/newspapers`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
        if (res.ok) { alert('Added'); form.reset(); loadAdminNewspapers(); }
    });

    document.getElementById('addMilkForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const form = e.target;
        const payload = Object.fromEntries(new FormData(form).entries());
        payload.quantity_ml = parseInt(payload.quantity_ml);
        payload.price_daily = parseFloat(payload.price_daily);
        payload.price_weekly = parseFloat(payload.price_weekly);
        payload.price_monthly = parseFloat(payload.price_monthly);
        const res = await fetch(`${API_BASE}/admin/milk`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
        if (res.ok) { alert('Added'); form.reset(); loadAdminMilk(); }
    });
});

async function loadAdminNewspapers() {
    const r = await fetch(`${API_BASE}/newspapers/`);
    const list = await r.json();
    const container = document.getElementById('newspapersAdmin');
    container.innerHTML = list.map(n => `
        <div class="admin-card">
            <strong>${n.name}</strong> — ${n.language} / ${n.genre} — Rs.${n.price_daily}/day
            <button onclick="deleteNewspaper(${n.id})" class="btn btn-secondary btn-small">Deactivate</button>
        </div>
    `).join('');
}

async function deleteNewspaper(id) {
    if (!confirm('Deactivate this newspaper?')) return;
    const r = await fetch(`${API_BASE}/admin/newspapers/${id}`, { method: 'DELETE' });
    if (r.ok) loadAdminNewspapers();
}

async function loadAdminMilk() {
    const r = await fetch(`${API_BASE}/milk/`);
    const list = await r.json();
    const container = document.getElementById('milkAdmin');
    container.innerHTML = list.map(m => `
        <div class="admin-card">
            <strong>${m.name}</strong> — ${m.quantity_ml}ml — Rs.${m.price_daily}/day
            <button onclick="deleteMilk(${m.id})" class="btn btn-secondary btn-small">Deactivate</button>
        </div>
    `).join('');
}

async function deleteMilk(id) {
    if (!confirm('Deactivate this milk package?')) return;
    const r = await fetch(`${API_BASE}/admin/milk/${id}`, { method: 'DELETE' });
    if (r.ok) loadAdminMilk();
}
