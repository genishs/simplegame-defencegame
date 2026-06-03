/* =========================================================================
   안시성 디펜스 — 역사노트 코덱스 렌더러
   data/codex.json 을 fetch 하여 DOM 으로 렌더 (향후 게임 JSON 과 동일 패턴 검증).
   외부 의존 없음. 순수 ES 모듈.
   ========================================================================= */

const LABELS = {
  fact:           { cls: "chip--fact",         text: "사실",            mark: "●" },
  "fact-adapted": { cls: "chip--fact-adapted", text: "사실 + 게임 각색", mark: "◑" },
  legend:         { cls: "chip--legend",       text: "전승",            mark: "▲" },
  fiction:        { cls: "chip--fiction",      text: "픽션",            mark: "✦" },
};

/* ---- DOM 헬퍼: 안전한 텍스트 노드 생성 (innerHTML 미사용 → XSS 방지) ---- */
function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v == null) continue;
    if (k === "class") node.className = v;
    else if (k === "dataset") Object.assign(node.dataset, v);
    else if (k.startsWith("on") && typeof v === "function") node.addEventListener(k.slice(2), v);
    else if (k === "html") node.innerHTML = v; // ruby 마크업 전용 (신뢰된 빌더만 사용)
    else node.setAttribute(k, v);
  }
  for (const c of children.flat()) {
    if (c == null) continue;
    node.append(c.nodeType ? c : document.createTextNode(String(c)));
  }
  return node;
}

function chip(labelKey) {
  const meta = LABELS[labelKey] || LABELS.fact;
  return el("span", { class: `chip ${meta.cls}` },
    el("span", { class: "chip-mark", "aria-hidden": "true" }, meta.mark),
    meta.text
  );
}

/* ---- 코덱스 카드 그리드 ---- */
function renderCards(cards, container, openDetail) {
  container.replaceChildren();
  if (!cards.length) {
    container.append(el("li", { class: "empty-state" }, "해당하는 카드가 없습니다."));
    return;
  }
  for (const card of cards) {
    const meta = LABELS[card.label] || LABELS.fact;
    const btn = el("button", {
      class: "card",
      type: "button",
      "aria-label": `카드 ${card.id} ${card.title} — ${meta.text}. 자세히 보기`,
      onclick: () => openDetail(card),
    },
      el("span", { class: "card-num" }, `카드 ${card.id}`),
      el("h3", { class: "card-title" }, card.title),
      el("p", { class: "card-summary" }, card.summary || ""),
      el("div", { class: "card-foot" },
        chip(card.label),
        el("span", { class: "card-unlock" }, card.unlock || "")
      )
    );
    container.append(el("li", {}, btn));
  }
}

/* ---- 상세 모달 본문 빌드 ---- */
function buildDetail(card, dialog) {
  const num = dialog.querySelector(".detail-num");
  const title = dialog.querySelector(".detail-head h2");
  const chipSlot = dialog.querySelector(".detail-chip");
  const body = dialog.querySelector(".detail-body");

  num.textContent = `카드 ${card.id}`;
  title.textContent = card.title;
  chipSlot.replaceChildren(chip(card.label));
  body.replaceChildren();

  for (const para of card.body || []) {
    body.append(el("p", {}, para));
  }

  // 픽션 카드(명대사 모음) 인용 목록
  if (card.quotes) {
    const ul = el("ul", { class: "quotes" });
    for (const q of card.quotes) {
      ul.append(el("li", {},
        el("span", { class: "line" }, `“${q.line}”`),
        el("span", { class: "scene" }, q.scene)
      ));
    }
    body.append(ul);
  }

  // 출처
  body.append(el("p", { class: "detail-source" },
    el("strong", {}, "출처 "), card.source || "—"
  ));

  // 한문 원문 토글 (<details>) — ruby 한자 병기
  if (card.hanja && card.hanja.length) {
    const list = el("div", { class: "hanja-list" });
    for (const h of card.hanja) {
      list.append(el("div", { class: "hanja-item" },
        el("span", { class: "han" }, h.term),
        el("span", { class: "reading" }, h.reading),
        h.note ? el("span", { class: "note" }, h.note) : null
      ));
    }
    body.append(
      el("details", { class: "hanja" },
        el("summary", {}, "한문 원문·용어 보기"),
        list
      )
    );
  }
}

/* ---- 유닛/적 엔티티 ---- */
function renderEntities(items, container, kind) {
  container.replaceChildren();
  for (const it of items) {
    const dl = el("dl");
    for (const [k, v] of Object.entries(it.stats || {})) {
      dl.append(el("dt", {}, k), el("dd", {}, String(v)));
    }
    // ruby: 이름 옆에 한자 병기
    const heading = el("h3", {});
    heading.append(it.name);
    if (it.hanja) {
      const ruby = el("ruby");
      ruby.append(it.hanja.term, el("rt", {}, it.hanja.reading));
      heading.append(" ");
      heading.append(ruby);
    }
    container.append(
      el("li", { class: `entity ${kind}` },
        heading,
        el("p", { class: "role" }, it.role || ""),
        dl,
        it.note ? el("p", { class: "note" }, it.note) : null
      )
    );
  }
}

/* ---- 라벨 필터 ---- */
function setupFilters(cards, cardList, openDetail) {
  const buttons = document.querySelectorAll(".legend .filter-btn");
  let active = "all";
  const apply = () => {
    const filtered = active === "all" ? cards : cards.filter((c) => c.label === active);
    renderCards(filtered, cardList, openDetail);
  };
  buttons.forEach((b) => {
    b.addEventListener("click", () => {
      active = b.dataset.filter;
      buttons.forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
      apply();
    });
  });
}

/* ---- 탭 전환 ---- */
function setupTabs() {
  const tabs = [...document.querySelectorAll('[role="tab"]')];
  const select = (tab) => {
    tabs.forEach((t) => {
      const on = t === tab;
      t.setAttribute("aria-selected", String(on));
      t.tabIndex = on ? 0 : -1;
      document.getElementById(t.getAttribute("aria-controls")).hidden = !on;
    });
  };
  tabs.forEach((t, i) => {
    t.addEventListener("click", () => select(t));
    t.addEventListener("keydown", (e) => {
      if (e.key === "ArrowRight" || e.key === "ArrowLeft") {
        e.preventDefault();
        const dir = e.key === "ArrowRight" ? 1 : -1;
        const next = tabs[(i + dir + tabs.length) % tabs.length];
        next.focus();
        select(next);
      }
    });
  });
}

/* ---- 접근성 토글 (글씨크기 / 색약) + localStorage 영속 ---- */
function setupA11y() {
  const root = document.documentElement;
  const STORE = "ansiseong-a11y";
  const saved = JSON.parse(localStorage.getItem(STORE) || "{}");

  // 글씨 크기
  const sizeBtns = document.querySelectorAll("[data-fontsize-btn]");
  const setSize = (v, persist = true) => {
    root.setAttribute("data-fontsize", v);
    sizeBtns.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.fontsizeBtn === v)));
    if (persist) { saved.fontsize = v; localStorage.setItem(STORE, JSON.stringify(saved)); }
  };
  sizeBtns.forEach((b) => b.addEventListener("click", () => setSize(b.dataset.fontsizeBtn)));
  setSize(saved.fontsize || "100", false);

  // 색약 모드
  const cbBtn = document.querySelector("[data-colorblind-btn]");
  const setCB = (on, persist = true) => {
    root.setAttribute("data-colorblind", on ? "on" : "off");
    cbBtn.setAttribute("aria-pressed", String(on));
    if (persist) { saved.colorblind = on; localStorage.setItem(STORE, JSON.stringify(saved)); }
  };
  cbBtn.addEventListener("click", () => setCB(root.getAttribute("data-colorblind") !== "on"));
  setCB(!!saved.colorblind, false);
}

/* ---- 모달 제어 ---- */
function setupDialog() {
  const dialog = document.getElementById("detail-dialog");
  let lastFocus = null;

  const open = (card) => {
    buildDetail(card, dialog);
    lastFocus = document.activeElement;
    if (typeof dialog.showModal === "function") dialog.showModal();
    else dialog.setAttribute("open", "");           // <dialog> 미지원 폴백
    dialog.querySelector(".detail-close").focus();
  };
  const close = () => {
    if (typeof dialog.close === "function") dialog.close();
    else dialog.removeAttribute("open");
    if (lastFocus) lastFocus.focus();
  };

  dialog.querySelector(".detail-close").addEventListener("click", close);
  // 백드롭 클릭으로 닫기
  dialog.addEventListener("click", (e) => { if (e.target === dialog) close(); });
  return { open };
}

/* ---- 부트스트랩 ---- */
async function main() {
  setupTabs();
  setupA11y();
  const { open } = setupDialog();

  let data;
  try {
    const res = await fetch("data/codex.json");
    if (!res.ok) throw new Error(res.status);
    data = await res.json();
  } catch (err) {
    document.getElementById("codex-list").append(
      el("li", { class: "empty-state" },
        "데이터를 불러오지 못했습니다. 로컬 서버에서 열어 주세요 (예: python -m http.server). 오류: " + err.message)
    );
    return;
  }

  renderCards(data.cards, document.getElementById("codex-list"), open);
  setupFilters(data.cards, document.getElementById("codex-list"), open);
  renderEntities(data.units || [], document.getElementById("unit-list"), "ally");
  renderEntities(data.enemies || [], document.getElementById("enemy-list"), "enemy");
}

document.addEventListener("DOMContentLoaded", main);
