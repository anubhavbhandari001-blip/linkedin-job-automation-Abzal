const API_BASE = window.API_BASE || "http://127.0.0.1:8000";

const state = {
  status: "",
  search: "",
  page: 0,
  pageSize: 20,
  total: 0,
  jobs: [],
};

let searchDebounce = null;

const el = (id) => document.getElementById(id);

function fmtRelativeTime(isoString) {
  if (!isoString) return "—";
  const then = new Date(isoString);
  if (isNaN(then)) return "—";
  const diffMs = Date.now() - then.getTime();
  const diffMin = Math.floor(diffMs / 60000);
  if (diffMin < 1) return "just now";
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffHr = Math.floor(diffMin / 60);
  if (diffHr < 24) return `${diffHr}h ago`;
  const diffDay = Math.floor(diffHr / 24);
  return `${diffDay}d ago`;
}

function scoreColor(score) {
  if (score === null || score === undefined) return "var(--text-dim)";
  if (score >= 70) return "var(--mint)";
  if (score >= 40) return "var(--amber)";
  return "var(--coral)";
}

async function fetchJSON(path) {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

async function loadStats() {
  try {
    const stats = await fetchJSON("/api/stats");
    el("stat-sent").textContent = stats.sent_today ?? 0;
    el("stat-total").textContent = stats.total ?? 0;
    el("stat-avg-score").textContent =
      stats.average_match_score !== null && stats.average_match_score !== undefined
        ? stats.average_match_score
        : "—";
    el("stat-analyzed").textContent = stats.by_status?.ANALYZED ?? 0;
    el("stat-skipped").textContent = stats.by_status?.SKIPPED ?? 0;
    el("stat-failed").textContent =
      (stats.by_status?.FAILED ?? 0) + (stats.by_status?.ANALYSIS_FAILED ?? 0);

    setApiStatus(true);
  } catch (err) {
    setApiStatus(false);
  }
}

function setApiStatus(ok) {
  const badge = el("api-status");
  if (ok) {
    badge.textContent = "Connected";
    badge.className = "api-status api-status--ok";
  } else {
    badge.textContent = "API unreachable";
    badge.className = "api-status api-status--error";
  }
}

async function loadJobs() {
  const params = new URLSearchParams({
    limit: state.pageSize,
    offset: state.page * state.pageSize,
  });
  if (state.status) params.set("status", state.status);
  if (state.search) params.set("search", state.search);

  try {
    const data = await fetchJSON(`/api/jobs?${params.toString()}`);
    state.jobs = data.jobs;
    state.total = data.total;
    renderJobs();
    renderPager();
    setApiStatus(true);
  } catch (err) {
    setApiStatus(false);
    el("manifest-body").innerHTML = "";
    el("manifest-empty").hidden = false;
    el("manifest-empty").querySelector("p").textContent =
      "Can't reach the dashboard API.";
    el("manifest-empty").querySelector(".manifest__empty-sub").textContent =
      `Make sure it's running at ${API_BASE} (uvicorn api.app:app --reload).`;
  }
}

function renderJobs() {
  const body = el("manifest-body");
  const empty = el("manifest-empty");

  if (!state.jobs.length) {
    body.innerHTML = "";
    empty.hidden = false;
    empty.querySelector("p").textContent = "No jobs match this view yet.";
    empty.querySelector(".manifest__empty-sub").textContent =
      "Run the automation script from the terminal to populate this board.";
    return;
  }

  empty.hidden = true;

  body.innerHTML = state.jobs
    .map((job) => {
      const score = job.match_score;
      const scoreDisplay = score === null || score === undefined ? "—" : score;
      const barWidth = score ? Math.min(100, Math.max(0, score)) : 0;
      const status = job.status || "UNKNOWN";

      return `
        <div class="manifest__row" data-id="${job.id}">
          <div class="col col--job">
            <span class="job-title">${escapeHtml(job.job_title || "Untitled role")}</span>
            <span class="job-recruiter">${escapeHtml(job.recruiter_name || "Unknown recruiter")}</span>
          </div>
          <div class="col col--company">${escapeHtml(job.company_name || "—")}</div>
          <div class="col col--score">
            ${scoreDisplay}
            <div class="score-bar-track"><div class="score-bar-fill" style="width:${barWidth}%; background:${scoreColor(score)}"></div></div>
          </div>
          <div class="col col--status">
            <span class="status-pill status-pill--${status}">${status}</span>
          </div>
          <div class="col col--time">${fmtRelativeTime(job.processed_at)}</div>
        </div>
      `;
    })
    .join("");

  body.querySelectorAll(".manifest__row").forEach((row) => {
    row.addEventListener("click", () => openDrawer(Number(row.dataset.id)));
  });
}

function renderPager() {
  const totalPages = Math.max(1, Math.ceil(state.total / state.pageSize));
  el("page-indicator").textContent = `Page ${state.page + 1} of ${totalPages}`;
  el("prev-page").disabled = state.page === 0;
  el("next-page").disabled = state.page + 1 >= totalPages;

  const start = state.total === 0 ? 0 : state.page * state.pageSize + 1;
  const end = Math.min(state.total, (state.page + 1) * state.pageSize);
  el("result-count").textContent = `${start}–${end} of ${state.total}`;
}

function openDrawer(jobId) {
  const job = state.jobs.find((j) => j.id === jobId);
  if (!job) return;

  const content = el("drawer-content");
  content.innerHTML = `
    <h2>${escapeHtml(job.job_title || "Untitled role")}</h2>
    <div class="drawer__company">${escapeHtml(job.company_name || "—")}</div>

    <div class="drawer__field">
      <span class="drawer__field-label">Status</span>
      <span class="drawer__field-value"><span class="status-pill status-pill--${job.status}">${job.status}</span></span>
    </div>
    <div class="drawer__field">
      <span class="drawer__field-label">Match score</span>
      <span class="drawer__field-value">${job.match_score ?? "Not yet analyzed"}</span>
    </div>
    <div class="drawer__field">
      <span class="drawer__field-label">Recruiter</span>
      <span class="drawer__field-value">${escapeHtml(job.recruiter_name || "Unknown")}</span>
    </div>
    <div class="drawer__field">
      <span class="drawer__field-label">Recruiter email</span>
      <span class="drawer__field-value">${escapeHtml(job.recruiter_email || "—")}</span>
    </div>
    <div class="drawer__field">
      <span class="drawer__field-label">Location</span>
      <span class="drawer__field-value">${escapeHtml(job.location || "—")}</span>
    </div>
    <div class="drawer__field">
      <span class="drawer__field-label">Employment type</span>
      <span class="drawer__field-value">${escapeHtml(job.employment_type || "—")}</span>
    </div>
    <div class="drawer__field">
      <span class="drawer__field-label">Last processed</span>
      <span class="drawer__field-value">${job.processed_at ? new Date(job.processed_at).toLocaleString() : "—"}</span>
    </div>
    <div class="drawer__field">
      <span class="drawer__field-label">LinkedIn post</span>
      <span class="drawer__field-value">${
        job.linkedin_post_url
          ? `<a href="${job.linkedin_post_url}" target="_blank" rel="noopener">Open on LinkedIn ↗</a>`
          : "—"
      }</span>
    </div>
    ${
      job.gmail_message_id
        ? `<div class="drawer__field">
             <span class="drawer__field-label">Gmail message ID</span>
             <span class="drawer__field-value">${escapeHtml(job.gmail_message_id)}</span>
           </div>`
        : ""
    }
  `;

  document.body.classList.add("drawer-open");
}

function closeDrawer() {
  document.body.classList.remove("drawer-open");
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

function wireControls() {
  el("search-input").addEventListener("input", (e) => {
    clearTimeout(searchDebounce);
    searchDebounce = setTimeout(() => {
      state.search = e.target.value.trim();
      state.page = 0;
      loadJobs();
    }, 300);
  });

  el("status-filters").addEventListener("click", (e) => {
    const btn = e.target.closest(".status-filter");
    if (!btn) return;

    document.querySelectorAll(".status-filter").forEach((b) => b.classList.remove("status-filter--active"));
    btn.classList.add("status-filter--active");

    state.status = btn.dataset.status;
    state.page = 0;
    loadJobs();
  });

  el("prev-page").addEventListener("click", () => {
    if (state.page > 0) {
      state.page -= 1;
      loadJobs();
    }
  });

  el("next-page").addEventListener("click", () => {
    state.page += 1;
    loadJobs();
  });

  el("refresh-btn").addEventListener("click", (e) => {
    e.target.classList.add("spinning");
    Promise.all([loadStats(), loadJobs()]).finally(() => {
      setTimeout(() => e.target.classList.remove("spinning"), 400);
    });
  });

  el("drawer-close").addEventListener("click", closeDrawer);
  el("drawer-overlay").addEventListener("click", closeDrawer);
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeDrawer();
  });
}

function init() {
  wireControls();
  loadStats();
  loadJobs();

  // Light polling so the board stays current if the scraper is
  // running in another terminal while this page is open.
  setInterval(() => {
    loadStats();
    loadJobs();
  }, 30000);
}

init();
