// Renders Markdown from the page store and opens short content in a modal.
// A card keeps its href: without this script, or with a modifier key, the click opens the page.
const html = document.documentElement;
const store = JSON.parse(document.getElementById("store")?.textContent || "{}");
const { marked } = await import(html.dataset.marked);

let mermaidReady;
async function renderMermaid(container) {
  const nodes = [...container.querySelectorAll("pre.mermaid")];
  if (!nodes.length) return;
  mermaidReady ??= import(html.dataset.mermaid).then(({ default: mermaid }) => {
    const dark = matchMedia("(prefers-color-scheme: dark)").matches;
    mermaid.initialize({ startOnLoad: false, theme: dark ? "dark" : "neutral" });
    return mermaid;
  });
  const mermaid = await mermaidReady;
  await mermaid.run({ nodes });
}

async function renderInto(element, markdown) {
  element.innerHTML = marked.parse(markdown);
  for (const link of element.querySelectorAll('a[href^="http"]')) {
    link.target = "_blank";
    link.rel = "noopener";
  }
  await renderMermaid(element);
}

for (const element of document.querySelectorAll("[data-md]")) {
  const item = store[element.dataset.md];
  if (item) await renderInto(element, item.md);
}

const dialog = document.getElementById("modal");
const title = document.getElementById("modal-title");
const meta = document.getElementById("modal-meta");
const pageLink = document.getElementById("modal-page");
const body = document.getElementById("modal-body");

async function openModal(item) {
  title.textContent = item.title;
  meta.textContent = item.meta;
  meta.hidden = !item.meta;
  pageLink.href = item.href;
  body.replaceChildren();
  dialog.showModal();
  dialog.scrollTop = 0;
  await renderInto(body, item.md);
}

document.addEventListener("click", (event) => {
  const card = event.target.closest("a[data-modal]");
  if (!card || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
  const item = store[card.dataset.modal];
  if (!item) return;
  event.preventDefault();
  openModal(item);
});

document.getElementById("modal-close").addEventListener("click", () => dialog.close());
// A click on the backdrop has the dialog itself as target.
dialog.addEventListener("click", (event) => {
  if (event.target === dialog) dialog.close();
});
