let currentEvents = [];
let selectedEventId = null;

async function loadDashboard() {
  const method = document.getElementById("method-filter").value;
  const search = encodeURIComponent(
    document.getElementById("search-input").value,
  );
  const res = await fetch(`/api/events?method=${method}&q=${search}`);
  const data = await res.json();

  currentEvents = data.events;
  renderStats(data.stats);

  if (!selectedEventId && currentEvents.length > 0) {
    selectedEventId = currentEvents[0].id;
  }
  renderEventList();
  renderInspector();
}

function renderStats(s) {
  const items = [
    {
      label: "Captured Webhooks",
      value: s.total_captured,
      color: "text-amber-400",
    },
    {
      label: "POST Payloads",
      value: s.post_requests,
      color: "text-emerald-400",
    },
    { label: "Unique Routes", value: s.unique_routes, color: "text-sky-400" },
    { label: "JSON Bodies", value: s.json_payloads, color: "text-purple-400" },
  ];
  document.getElementById("stats-bar").innerHTML = items
    .map(
      (i) => `
    <div class="bg-neutral-900/70 border border-neutral-800 rounded-xl p-4">
      <span class="text-[10px] uppercase text-neutral-500 block">${i.label}</span>
      <span class="text-2xl font-bold ${i.color} mt-1 block">${i.value}</span>
    </div>
  `,
    )
    .join("");
}

function renderEventList() {
  const container = document.getElementById("event-list");
  if (currentEvents.length === 0) {
    container.innerHTML = `<div class="text-center py-12 text-xs text-neutral-500">No webhook events captured yet.</div>`;
    return;
  }

  container.innerHTML = currentEvents
    .map((evt) => {
      const active = evt.id === selectedEventId;
      return `
      <div onclick="selectEvent('${evt.id}')" class="p-3.5 rounded-xl border cursor-pointer transition-all ${
        active
          ? "bg-amber-500/10 border-amber-500/50"
          : "bg-neutral-950 border-neutral-800 hover:border-neutral-700"
      }">
        <div class="flex items-center justify-between text-xs">
          <span class="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[10px] font-bold">${evt.method}</span>
          <span class="text-[10px] text-neutral-500">${evt.timestamp}</span>
        </div>
        <div class="text-xs font-bold text-neutral-100 mt-2 truncate">${evt.endpoint}</div>
        <div class="text-[10px] text-neutral-500 mt-1">Source IP: ${evt.source_ip} &bull; ID: ${evt.id}</div>
      </div>
    `;
    })
    .join("");
}

function selectEvent(id) {
  selectedEventId = id;
  renderEventList();
  renderInspector();
}

function renderInspector() {
  const pane = document.getElementById("inspector-pane");
  const evt = currentEvents.find((e) => e.id === selectedEventId);
  if (!evt) {
    pane.innerHTML = `<div class="text-center py-20 text-xs text-neutral-500">Select an event to inspect details.</div>`;
    return;
  }

  const headersRows = Object.entries(evt.headers)
    .map(
      ([k, v]) => `
    <tr class="border-b border-neutral-800/80">
      <td class="py-2 pr-4 text-amber-400 font-semibold">${k}</td>
      <td class="py-2 text-neutral-300 break-all">${v}</td>
    </tr>
  `,
    )
    .join("");

  const formattedBody =
    typeof evt.payload === "object"
      ? JSON.stringify(evt.payload, null, 2)
      : evt.payload;

  pane.innerHTML = `
    <div class="flex flex-wrap items-center justify-between gap-2 border-b border-neutral-800 pb-4">
      <div>
        <span class="text-xs font-bold text-amber-400">${evt.method} ${evt.endpoint}</span>
        <p class="text-[11px] text-neutral-400 mt-0.5">Event ID: ${evt.id} &bull; Captured at ${evt.timestamp}</p>
      </div>
      <button onclick="copyCurl('${evt.id}')" class="bg-neutral-800 hover:bg-neutral-700 text-neutral-200 text-[11px] px-3 py-1.5 rounded-lg transition-colors">
        Copy as cURL
      </button>
    </div>

    <div class="space-y-2">
      <h3 class="text-[11px] font-bold uppercase tracking-wider text-neutral-400">HTTP Request Headers</h3>
      <div class="bg-neutral-950 border border-neutral-800 rounded-xl p-3 overflow-x-auto">
        <table class="w-full text-left text-[11px]"><tbody>${headersRows}</tbody></table>
      </div>
    </div>

    <div class="space-y-2">
      <h3 class="text-[11px] font-bold uppercase tracking-wider text-neutral-400">Parsed Request Body (${evt.content_type})</h3>
      <pre class="bg-neutral-950 border border-neutral-800 rounded-xl p-4 text-xs text-emerald-300 overflow-x-auto"><code>${formattedBody}</code></pre>
    </div>
  `;
}

function copyCurl(id) {
  const evt = currentEvents.find((e) => e.id === id);
  if (!evt) return;
  const bodyStr = JSON.stringify(evt.payload);
  const cmd = `curl -X ${evt.method} http://localhost:8080${evt.endpoint} -H "Content-Type: ${evt.content_type}" -d '${bodyStr}'`;
  navigator.clipboard.writeText(cmd);
  alert("cURL replay command copied to clipboard!");
}

async function simulateWebhook() {
  const res = await fetch("/api/simulate", { method: "POST" });
  const created = await res.json();
  selectedEventId = created.id;
  loadDashboard();
}

async function clearEvents() {
  await fetch("/api/events", { method: "DELETE" });
  selectedEventId = null;
  loadDashboard();
}

loadDashboard();
