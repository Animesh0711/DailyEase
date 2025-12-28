// ========== Dashboard Functions ==========
// API_BASE is defined in config.js
let selectedNewspapers = [];  // Changed to array for multiple selection
let selectedMilk = null;
// Milk brand quantities stored as number of 0.5L units per type
let selectedMilkBrands = {
    "Chitale Bandhu": { cow: 0, buffalo: 0 },
    "Phadke Doodh": { cow: 0, buffalo: 0 },
    "Shriram Dairy": { cow: 0, buffalo: 0 },
    "Amul": { cow: 0, buffalo: 0 }
};

// Unit prices per 0.5L per day
const milkUnitPrices = {
    cow: 29,      // Rs.29 per 0.5L per day
    buffalo: 35   // Rs.35 per 0.5L per day
};
let selectedMagazines = [];
let selectedSubscription = null; // subscription id to manage calendar clicks
let currentNewspapers = [];
let currentSubscriptions = [];
let stripe = null;
let stripeElements = null;
let cardElement = null;
let razorpay = null;
let lastSubscriptionResponse = null;  // Store response from create-subscription endpoint

document.addEventListener("DOMContentLoaded", async function () {
    const userId = localStorage.getItem("user_id");
    if (!userId) {
        window.location.href = "login.html";
        return;
    }

    const userName = localStorage.getItem("user_name");
    document.getElementById("userGreeting").textContent = `👤 ${userName}`;

    await loadSubscriptions(userId);
    await loadNewspapers();
    await loadMilkPackages();
    await loadMagazines();
    await loadDeliveryCalendar(userId);

    // Initialize tab switching
    setupTabs();
    await initStripe();
    await initRazorpay();
});

// Preview theme removed

// ========== Tab Setup ==========
function setupTabs() {
    const tabs = document.querySelectorAll(".tab-btn");
    if (tabs.length > 0) {
        tabs[0].classList.add("active");
        const firstTab = document.querySelector(".tab-content");
        if (firstTab) {
            firstTab.classList.add("active");
        }
    }
}

function switchTab(tabName) {
    document.querySelectorAll(".tab-btn").forEach(btn => btn.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach(tab => tab.classList.remove("active"));

    event.target.classList.add("active");
    const tabElement = document.getElementById(tabName + "-tab");
    if (tabElement) {
        tabElement.classList.add("active");
        if (tabName === 'manage') displayManageList();
    }
}

// ========== Subscriptions Functions ==========
async function loadSubscriptions(userId) {
    try {
        const response = await fetch(`${API_BASE}/subscriptions/${userId}`);
        if (response.ok) {
            const subscriptions = await response.json();
            displaySubscriptions(subscriptions);
            populateSubscriptionSelector(subscriptions);
            // after loading subscriptions, also load payments
            await loadPayments(userId);
        }
    } catch (error) {
        console.error("Error loading subscriptions:", error);
    }
}

function displaySubscriptions(subscriptions) {
    const container = document.getElementById("subscriptionsList");
    currentSubscriptions = subscriptions;

    if (subscriptions.length === 0) {
        container.innerHTML = "<p class='loading'>No active subscriptions. Create one to get started!</p>";
        return;
    }

    container.innerHTML = subscriptions.map(sub => `
        <div class="subscription-card">
            <h3>${sub.newspaper_id ? "📰 Newspaper" : "🥛 Milk"} Subscription</h3>
            <p><strong>Frequency:</strong> <span>${sub.frequency.toUpperCase()}</span></p>
            <p><strong>Cost:</strong> <span>₹${sub.total_cost.toFixed(2)}</span></p>
            <p>
                <strong>Status:</strong> 
                <span class="badge ${sub.is_paused ? 'badge-paused' : 'badge-active'}">
                    ${sub.is_paused ? '⏸ Paused' : '✅ Active'}
                </span>
            </p>
            ${sub.paused_until ? `<p><strong>Paused Until:</strong> <span>${new Date(sub.paused_until).toLocaleDateString()}</span></p>` : ''}
            <div class="card-actions">
                ${!sub.is_paused ?
            `<button class="btn btn-secondary btn-small" onclick="pauseSubscription(${sub.id})">⏸ Pause</button>` :
            `<button class="btn btn-secondary btn-small" onclick="resumeSubscription(${sub.id})">▶ Resume</button>`
        }
            </div>
        </div>
    `).join("");
}

// ========== Payments / Invoices ==========
async function loadPayments(userId) {
    try {
        const r = await fetch(`${API_BASE}/payments/history/${userId}`);
        if (!r.ok) { document.getElementById('paymentsList').innerText = 'Failed to load payments'; return; }
        const payments = await r.json();
        displayPayments(payments);
    } catch (e) { console.error(e); document.getElementById('paymentsList').innerText = 'Error loading payments'; }
}

function displayPayments(payments) {
    const container = document.getElementById('paymentsList');
    if (!container) return;
    if (!payments || payments.length === 0) { container.innerHTML = '<p>No payments yet.</p>'; return; }
    container.innerHTML = payments.map(p => {
        const status = p.status || 'pending';
        return `
            <div class="payment-card">
                <p><strong>Amount:</strong> Rs.${p.amount}</p>
                <p><strong>Status:</strong> ${status}</p>
                <p><strong>Subscription:</strong> ${p.subscription_id || '-'}</p>
                ${status !== 'completed' ? `<button class="btn btn-primary btn-small" onclick="retryPayment(${p.id}, ${p.subscription_id || 'null'}, ${p.amount})">Retry Payment</button>` : ''}
            </div>
        `;
    }).join('');
}

async function retryPayment(paymentId, subscriptionId, amount) {
    const userId = localStorage.getItem('user_id');
    if (!confirm('Retry payment of Rs.' + amount + '?')) return;
    try {
        const r = await fetch(`${API_BASE}/payments/create-payment-intent`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ amount: amount, user_id: parseInt(userId), subscription_id: subscriptionId })
        });
        if (!r.ok) { const err = await r.json(); alert('Failed: ' + (err.detail || r.statusText)); return; }
        const data = await r.json();
        if (!data.client_secret) { alert('Payment created server-side; please configure Stripe'); return; }

        if (!stripe) await initStripe();
        if (!cardElement) {
            stripeElements = stripe.elements();
            cardElement = stripeElements.create('card');
            cardElement.mount('#stripe-card-element');
        }

        const res = await stripe.confirmCardPayment(data.client_secret, { payment_method: { card: cardElement } });
        if (res.error) { alert('Payment failed: ' + res.error.message); return; }
        if (res.paymentIntent && res.paymentIntent.status === 'succeeded') {
            // call confirm on server for the paymentId returned (data.payment_id)
            const confirmResp = await fetch(`${API_BASE}/payments/confirm-payment/${data.payment_id}`, { method: 'POST' });
            if (!confirmResp.ok) { alert('Server confirm failed'); return; }
            alert('Payment succeeded');
            loadPayments(userId);
            loadSubscriptions(userId);
        }
    } catch (e) { console.error(e); alert('Retry failed'); }
}

async function pauseSubscription(subscriptionId) {
    const days = prompt("Pause for how many days?", "7");
    if (!days) return;

    try {
        const response = await fetch(
            `${API_BASE}/subscriptions/${subscriptionId}/pause?pause_days=${days}`,
            { method: "POST" }
        );

        if (response.ok) {
            alert("Subscription paused successfully!");
            location.reload();
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Failed to pause subscription");
    }
}

async function resumeSubscription(subscriptionId) {
    try {
        const response = await fetch(
            `${API_BASE}/subscriptions/${subscriptionId}/resume`,
            { method: "POST" }
        );

        if (response.ok) {
            alert("Subscription resumed successfully!");
            location.reload();
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Failed to resume subscription");
    }
}

// ========== Newspapers Functions ==========
async function loadNewspapers() {
    try {
        const response = await fetch(`${API_BASE}/newspapers/`);
        if (response.ok) {
            currentNewspapers = await response.json();
            displayNewspapersList(currentNewspapers);
        }
    } catch (error) {
        console.error("Error loading newspapers:", error);
    }
}

function displayNewspapersList(newspapers) {
    const container = document.getElementById("newspapersList");
    if (!container) return;

    container.innerHTML = newspapers.map(paper => `
        <div class="item-card ${selectedNewspapers.includes(paper.id) ? 'selected' : ''}" onclick="selectNewspaper(${paper.id})">
            <h4>📰 ${paper.name}</h4>
            <p><strong>${paper.language}</strong> - ${paper.genre}</p>
            <p>₹${paper.price_daily}/day</p>
            <p>₹${paper.price_weekly}/week</p>
            <p class="item-price">₹${paper.price_monthly}/month</p>
        </div>
    `).join("");
}

function selectNewspaper(id) {
    const idx = selectedNewspapers.indexOf(id);
    if (idx > -1) {
        selectedNewspapers.splice(idx, 1);
    } else {
        selectedNewspapers.push(id);
    }
    displayNewspapersList(currentNewspapers);
    updatePricePreview();
}

function filterNewspapers() {
    // Filters removed - keep original list display
    displayNewspapersList(currentNewspapers);
}

// ========== Milk Functions ==========
async function loadMilkPackages() {
    try {
        const response = await fetch(`${API_BASE}/milk/`);
        if (response.ok) {
            // keep package fetch for compatibility (not required for brand-based selection)
            await response.json();
            displayMilkBrands();
        }
    } catch (error) {
        console.error("Error loading milk packages:", error);
    }
}
function displayMilkBrands() {
    const container = document.getElementById('milkBrands');
    if (!container) return;
    const brands = Object.keys(selectedMilkBrands);
    container.innerHTML = brands.map(brand => {
        const qtyCow = selectedMilkBrands[brand].cow;
        const qtyBuff = selectedMilkBrands[brand].buffalo;
        return `
        <div class="milk-brand-card">
            <h4>🥛 ${brand}</h4>
            <div class="milk-rows">
                <div class="milk-row">
                    <span class="milk-type">Cow</span>
                    <button class="btn-qty" onclick="decrementMilk('${brand}','cow')">-</button>
                    <span id="${brand.replace(/\s+/g, '_')}_cow_qty">${(qtyCow * 0.5).toFixed(1)}L</span>
                    <span style="margin-left:8px;color:#444">Price: <strong id="${brand.replace(/\s+/g, '_')}_cow_price">Rs.0.00</strong></span>
                    <button class="btn-qty" onclick="incrementMilk('${brand}','cow')">+</button>
                </div>
                <div class="milk-row">
                    <span class="milk-type">Buffalo</span>
                    <button class="btn-qty" onclick="decrementMilk('${brand}','buffalo')">-</button>
                    <span id="${brand.replace(/\s+/g, '_')}_buffalo_qty">${(qtyBuff * 0.5).toFixed(1)}L</span>
                    <span style="margin-left:8px;color:#444">Price: <strong id="${brand.replace(/\s+/g, '_')}_buffalo_price">Rs.0.00</strong></span>
                    <button class="btn-qty" onclick="incrementMilk('${brand}','buffalo')">+</button>
                </div>
            </div>
        </div>
        `;
    }).join('');
    // Initialize price displays
    updateMilkTotals();
}

function incrementMilk(brand, type) {
    selectedMilkBrands[brand][type] += 1; // one unit = 0.5L
    document.getElementById(`${brand.replace(/\s+/g, '_')}_${type}_qty`).textContent = (selectedMilkBrands[brand][type] * 0.5).toFixed(1) + 'L';
    updatePricePreview();
    updateMilkTotals();
}

function decrementMilk(brand, type) {
    if (selectedMilkBrands[brand][type] > 0) selectedMilkBrands[brand][type] -= 1;
    document.getElementById(`${brand.replace(/\s+/g, '_')}_${type}_qty`).textContent = (selectedMilkBrands[brand][type] * 0.5).toFixed(1) + 'L';
    updatePricePreview();
    updateMilkTotals();
}

function updateMilkTotals() {
    let total = 0;
    Object.keys(selectedMilkBrands).forEach(brand => {
        const slug = brand.replace(/\s+/g, '_');
        const cowUnits = selectedMilkBrands[brand].cow || 0;
        const buffUnits = selectedMilkBrands[brand].buffalo || 0;
        const cowPrice = cowUnits * milkUnitPrices.cow;
        const buffPrice = buffUnits * milkUnitPrices.buffalo;
        total += cowPrice + buffPrice;
        const cowEl = document.getElementById(`${slug}_cow_price`);
        const buffEl = document.getElementById(`${slug}_buffalo_price`);
        if (cowEl) cowEl.textContent = `Rs.${cowPrice.toFixed(2)}`;
        if (buffEl) buffEl.textContent = `Rs.${buffPrice.toFixed(2)}`;
    });
    const totalEl = document.getElementById('milkTotalAmount');
    if (totalEl) totalEl.textContent = `Rs.${total.toFixed(2)}`;
}

// ========== Magazines Functions ==========
async function loadMagazines() {
    try {
        const response = await fetch(`${API_BASE}/magazines/`);
        if (response.ok) {
            const magazines = await response.json();
            displayMagazinesList(magazines);
        }
    } catch (error) {
        console.error("Error loading magazines:", error);
    }
}

function displayMagazinesList(magazines) {
    const container = document.getElementById("magazinesList");
    if (!container) return;

    // Render magazines as informational (non-selectable). Mark complementary on Sundays.
    container.innerHTML = magazines.map(mag => `
        <div class="item-card">
            <h4>📚 ${mag.name}</h4>
            <p><strong>${mag.language}</strong> - ${mag.genre}</p>
            <p style="color:#777; font-size:0.95rem">★ Complementary on Sundays</p>
        </div>
    `).join("");
}

// ========== Calendar Functions ==========
async function loadDeliveryCalendar(userId) {
    try {
        const response = await fetch(`${API_BASE}/subscriptions/calendar/${userId}`);
        if (response.ok) {
            const calendar = await response.json();
            displayCalendar(calendar);
        }
    } catch (error) {
        console.error("Error loading calendar:", error);
    }
}

function displayCalendar(calendar) {
    const container = document.getElementById("deliveryCalendar");
    if (!container) return;

    // Render 2025 calendar as monthly tables (4 months per row)
    const year = 2025;
    const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

    let html = '<div class="calendar-grid">';

    for (let m = 0; m < 12; m++) {
        const firstDay = new Date(year, m, 1);
        const lastDay = new Date(year, m + 1, 0);

        html += `<div class="month-calendar">
            <div class="month-header">${monthNames[m]} ${year}</div>
            <table class="month-table">
            <thead><tr>`;

        // Day headers
        dayNames.forEach(d => { html += `<th>${d}</th>`; });
        html += '</tr></thead><tbody><tr>';

        // Empty cells for days before 1st
        for (let i = 0; i < firstDay.getDay(); i++) {
            html += '<td class="empty"></td>';
        }

        let cellCount = firstDay.getDay();

        // Calendar days
        for (let day = 1; day <= lastDay.getDate(); day++) {
            if (cellCount > 0 && cellCount % 7 === 0) {
                html += '</tr><tr>';
            }
            const dateKey = `${year}-${String(m + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
            const events = calendar[dateKey] || [];
            const hasDelivery = events.length > 0;
            html += `<td class="calendar-cell ${hasDelivery ? 'marked' : ''}" data-date="${dateKey}" onclick="handleCalendarDateClick(event)">
                <span class="day-num">${day}</span>
                ${hasDelivery ? '<span class="indicator">📦</span>' : ''}
            </td>`;
            cellCount++;
        }

        // Empty cells at end
        while (cellCount % 7 !== 0) {
            html += '<td class="empty"></td>';
            cellCount++;
        }

        html += '</tr></tbody></table></div>';
    }

    html += '</div>';
    container.innerHTML = html;

    // Populate subscription selector
    populateSubscriptionSelector(currentSubscriptions);
    const sel = document.getElementById('subscriptionSelector');
    if (sel) {
        sel.addEventListener('change', (e) => { selectedSubscription = e.target.value ? parseInt(e.target.value) : null; });
    }
}

function showCalendarTableView() {
    document.getElementById('deliveryCalendar').style.display = 'block';
}

// Removed Table View button; the function is now unused. Keeping no-op to avoid errors if invoked elsewhere.

function handleCalendarDateClick(e) {
    const el = e.currentTarget || e.target.closest('[data-date]');
    if (!el) return;
    const date = el.getAttribute('data-date');
    if (!selectedSubscription) {
        alert('Select a subscription from the dropdown above to mark/unmark deliveries for that subscription.');
        return;
    }
    toggleDelivery(selectedSubscription, date);
}

async function toggleDelivery(subscriptionId, dateStr) {
    const userId = localStorage.getItem('user_id');
    try {
        const r = await fetch(`${API_BASE}/subscriptions/${subscriptionId}/toggle-delivery`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ date: dateStr })
        });
        if (!r.ok) { const j = await r.json(); alert('Failed: ' + (j.detail || r.statusText)); return; }
        const data = await r.json();
        // refresh calendar
        await loadDeliveryCalendar(userId);
    } catch (err) { console.error(err); alert('Failed to toggle delivery'); }
}

function populateSubscriptionSelector(subscriptions) {
    const sel = document.getElementById('subscriptionSelector');
    if (!sel) return;
    // clear existing
    sel.innerHTML = '<option value="">-- Select --</option>';
    subscriptions.forEach(s => {
        const label = `#${s.id} · ₹${s.total_cost.toFixed(2)} · ${s.frequency}`;
        const opt = document.createElement('option'); opt.value = s.id; opt.textContent = label; sel.appendChild(opt);
    });
}

function displayManageList() {
    // used inside the Manage tab to show subscription pause/resume controls
    const container = document.getElementById('manageList');
    if (!container) return;
    if (!currentSubscriptions || currentSubscriptions.length === 0) { container.innerHTML = '<p>No subscriptions found.</p>'; return; }
    container.innerHTML = currentSubscriptions.map(s => {
        return `
            <div class="manage-row">
                <div>#${s.id} — ${s.frequency.toUpperCase()} — ₹${s.total_cost.toFixed(2)}</div>
                <div>
                    ${!s.is_paused ? `<button class="btn btn-secondary btn-small" onclick="pauseSubscription(${s.id})">Pause</button>` :
                `<button class="btn btn-secondary btn-small" onclick="resumeSubscription(${s.id})">Resume</button>`}
                </div>
            </div>
        `;
    }).join('');
}

// ========== Modal Functions ==========
function openNewSubscriptionModal() {
    document.getElementById("subscriptionModal").classList.add("active");
    // refresh manage list when opening modal
    displayManageList();
}

function openPaymentModal() {
    document.getElementById("paymentModal").classList.add("active");
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove("active");
}

window.onclick = function (event) {
    if (event.target.classList.contains("modal")) {
        event.target.classList.remove("active");
    }
}

async function createSubscription() {
    const userId = localStorage.getItem("user_id");
    const frequency = document.getElementById("frequency").value;

    // At least one newspaper is mandatory
    if (!selectedNewspapers || selectedNewspapers.length === 0) {
        alert("Please select at least one newspaper (mandatory)");
        return;
    }

    try {
        // create subscription and payment intent/order
        const response = await fetch(`${API_BASE}/subscriptions/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_id: parseInt(userId),
                newspaper_ids: selectedNewspapers,
                milk_package_id: selectedMilk,
                milk_details: selectedMilkBrands,
                frequency: frequency
            })
        });

        if (!response.ok) {
            const err = await response.json();
            alert(`Subscription failed: ${err.detail || response.statusText}`);
            return;
        }

        const data = await response.json();
        lastSubscriptionResponse = data;  // Store for Razorpay payment

        // Route based on payment method returned
        if (data.payment_method === 'razorpay' && data.razorpay_order_id) {
            document.getElementById('razorpay-container').style.display = 'block';
            alert('Payment method: Razorpay. Click "Pay with Razorpay" button to proceed.');
            return;
        } else if (data.payment_method === 'stripe' && data.client_secret) {
            // Stripe flow
            document.getElementById('stripe-card-element').style.display = 'block';
            if (!stripe) await initStripe();

            if (!cardElement) {
                stripeElements = stripe.elements();
                cardElement = stripeElements.create('card');
                cardElement.mount('#stripe-card-element');
            }

            const result = await stripe.confirmCardPayment(data.client_secret, {
                payment_method: { card: cardElement }
            });

            if (result.error) {
                alert('Payment failed: ' + result.error.message);
                return;
            }

            if (result.paymentIntent && result.paymentIntent.status === 'succeeded') {
                const confirmResp = await fetch(`${API_BASE}/payments/confirm-payment/${data.payment_id}`, { method: 'POST' });
                if (!confirmResp.ok) {
                    const err = await confirmResp.json();
                    alert('Payment confirmation failed: ' + (err.detail || confirmResp.statusText));
                    return;
                }

                alert('Subscription created and payment completed successfully!');
                closeModal('subscriptionModal');
                location.reload();
            } else {
                alert('Payment was not completed.');
            }
        } else {
            // Pending or error
            alert('Subscription created but payment processor unavailable. Status: ' + data.payment_method);
            closeModal('subscriptionModal');
            location.reload();
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to create subscription');
    }
}

async function initiateRazorpayPayment() {
    if (!lastSubscriptionResponse) {
        alert('No pending payment. Create a subscription first.');
        return;
    }

    const data = lastSubscriptionResponse;
    const userId = localStorage.getItem("user_id");
    const userName = localStorage.getItem("user_name") || "User";

    const options = {
        key: data.razorpay_public_key || "",  // Will be empty if not configured
        amount: parseInt(data.amount * 100),  // in paise
        currency: "INR",
        order_id: data.razorpay_order_id,
        handler: async function (response) {
            // Payment successful; verify on server
            try {
                const verifyResp = await fetch(`${API_BASE}/payments/verify-razorpay`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        payment_id: data.payment_id,
                        razorpay_payment_id: response.razorpay_payment_id,
                        razorpay_order_id: response.razorpay_order_id,
                        razorpay_signature: response.razorpay_signature
                    })
                });
                if (!verifyResp.ok) {
                    const err = await verifyResp.json();
                    alert('Payment verification failed: ' + (err.detail || verifyResp.statusText));
                    return;
                }
                alert('✅ Payment successful! Subscription created.');
                closeModal('subscriptionModal');
                location.reload();
            } catch (e) {
                console.error(e);
                alert('Payment completed but verification failed. Please contact support.');
            }
        },
        prefill: {
            name: userName,
            email: localStorage.getItem("user_email") || ""
        },
        theme: { color: "#667eea" }
    };

    const rzp = new Razorpay(options);
    rzp.open();
}

async function initStripe() {
    try {
        const r = await fetch(`${API_BASE}/config`);
        if (!r.ok) return;
        const cfg = await r.json();
        const key = cfg.stripe_public_key;
        if (!key) return;
        stripe = Stripe(key);
    } catch (e) {
        console.error('Stripe init failed', e);
    }
}

async function initRazorpay() {
    try {
        const r = await fetch(`${API_BASE}/config`);
        if (!r.ok) return;
        const cfg = await r.json();
        // Razorpay script is already loaded; we just ensure config is fetched
        console.log('Razorpay init complete (script loaded)');
    } catch (e) {
        console.error('Razorpay init failed', e);
    }
}

// ========== Payment Functions ==========
async function processPayment() {
    alert('Payments are now handled in the subscription modal.');
}

// ========== Price Preview Helpers ==========
function updatePricePreview() {
    const previewEl = document.getElementById('pricePreviewContent');
    if (!previewEl) return;
    const freq = document.getElementById('frequency') ? document.getElementById('frequency').value : 'monthly';

    if (!selectedNewspapers || selectedNewspapers.length === 0) {
        previewEl.innerHTML = 'Select newspapers to see price (Weekdays: Rs.4 / Weekends: Rs.7)';
        return;
    }

    const wd = 4, we = 7;
    let paperPrice = 0;
    if (freq === 'daily') paperPrice = wd * selectedNewspapers.length;
    else if (freq === 'weekly') paperPrice = (wd * 5 + we * 2) * selectedNewspapers.length;
    else paperPrice = (wd * 5 + we * 2) * 4 * selectedNewspapers.length;  // monthly

    // Compute milk price from selectedMilkBrands (units of 0.5L)
    let milkUnitsTotal = 0;
    let milkPrice = 0;
    Object.keys(selectedMilkBrands).forEach(brand => {
        const cowUnits = selectedMilkBrands[brand].cow || 0;
        const buffUnits = selectedMilkBrands[brand].buffalo || 0;
        milkUnitsTotal += cowUnits + buffUnits;
        milkPrice += cowUnits * milkUnitPrices.cow;
        milkPrice += buffUnits * milkUnitPrices.buffalo;
    });

    if (milkUnitsTotal > 0) {
        // milkPrice currently per-day for units (0.5L); scale by frequency
        let milkTotal = 0;
        if (freq === 'daily') milkTotal = milkPrice;
        else if (freq === 'weekly') milkTotal = milkPrice * 7;
        else milkTotal = milkPrice * 30; // approximate month

        let total = paperPrice + milkTotal;
        // Apply 20% discount if milk is included
        total = total * 0.8;
        previewEl.innerHTML = `Newspapers: Rs.${paperPrice} <br> Milk: Rs.${milkTotal.toFixed(2)} <br> <strong>20% Discount (with milk)</strong><br>Total: Rs.${total.toFixed(2)}`;
    } else {
        previewEl.innerHTML = `Newspapers: Rs.${paperPrice} <br> Milk: - <br> Total: Rs.${paperPrice.toFixed(2)}`;
    }
}

document.addEventListener('change', (e) => {
    if (!e.target) return;
    if (e.target.id === 'frequency') updatePricePreview();
});
