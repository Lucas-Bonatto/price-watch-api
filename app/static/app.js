const fallbackData = {
  product: {
    id: 1,
    name: "A Light in the Attic",
    target_price: 40,
  },
  history: [
    { id: 1, product_id: 1, price: 51.77, available: true, checked_at: "2026-09-01T12:05:00Z" },
    { id: 2, product_id: 1, price: 46.9, available: true, checked_at: "2026-09-05T12:05:00Z" },
    { id: 3, product_id: 1, price: 39.99, available: true, checked_at: "2026-09-10T12:05:00Z" },
  ],
  alert: {
    alert_triggered: true,
    current_price: 39.99,
    target_price: 40,
  },
};

const moneyFormatter = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
});

const dateFormatter = new Intl.DateTimeFormat("pt-BR", {
  day: "2-digit",
  month: "short",
  timeZone: "UTC",
});

function byDateAscending(first, second) {
  return new Date(first.checked_at) - new Date(second.checked_at);
}

function formatDate(date) {
  return dateFormatter.format(new Date(date)).replace(".", "");
}

function setStatus(isOnline) {
  const label = isOnline ? "API online" : "Demonstração disponível";
  document.querySelector("#header-status-text").textContent = label;
  document.querySelector("#api-status-text").textContent = label;

  if (!isOnline) {
    document.querySelectorAll(".status-dot").forEach((dot) => {
      dot.classList.add("is-warning");
    });
  }
}

function createResponseExample(product, history) {
  const latest = history.at(-1);

  return [
    {
      id: latest.id ?? history.length,
      product_id: latest.product_id ?? product.id,
      price: Number(latest.price),
      available: latest.available ?? true,
      checked_at: latest.checked_at,
    },
  ];
}

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function syntaxHighlightJson(json) {
  const escapedJson = escapeHtml(json);

  return escapedJson.replace(
    /(&quot;.*?&quot;)(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d+)?/g,
    (match, stringToken, colon) => {
      if (stringToken) {
        const tokenClass = colon ? "json-key" : "json-string";
        return `<span class="${tokenClass}">${stringToken}</span>${colon ?? ""}`;
      }

      const tokenClass = /true|false/.test(match)
        ? "json-boolean"
        : match === "null"
          ? "json-null"
          : "json-number";
      return `<span class="${tokenClass}">${match}</span>`;
    },
  );
}

function renderResponse(product, history) {
  const response = createResponseExample(product, history);
  const code = document.querySelector("#response-code");
  const responseText = JSON.stringify(response, null, 2);
  code.dataset.raw = responseText;
  code.innerHTML = syntaxHighlightJson(responseText);
}

function renderSummary(product, history, alert) {
  const latest = history.at(-1);
  document.querySelector("#product-name").textContent = product.name;
  document.querySelector("#target-price").textContent = moneyFormatter.format(
    product.target_price,
  );
  document.querySelector("#latest-date").textContent = formatDate(latest.checked_at);
  document.querySelector("#latest-price").textContent = moneyFormatter.format(
    latest.price,
  );

  const chip = document.querySelector("#alert-chip");
  chip.textContent = alert.alert_triggered ? "Meta atingida" : "Em monitoramento";
  chip.classList.toggle("is-monitoring", !alert.alert_triggered);
}

function renderChart(product, history) {
  const context = document.querySelector("#price-chart");
  const prices = history.map((entry) => Number(entry.price));
  const labels = history.map((entry) => formatDate(entry.checked_at));

  if (!window.Chart) {
    context.replaceWith(
      Object.assign(document.createElement("p"), {
        className: "chart-fallback",
        textContent: `Histórico: ${prices.map((price) => moneyFormatter.format(price)).join(" • ")}`,
      }),
    );
    return;
  }

  new window.Chart(context, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Preço registrado",
          data: prices,
          borderColor: "#1261d8",
          backgroundColor: "rgba(18, 97, 216, 0.10)",
          pointBackgroundColor: "#1261d8",
          pointBorderColor: "#fbfaf7",
          pointBorderWidth: 3,
          pointRadius: 5,
          pointHoverRadius: 7,
          borderWidth: 3,
          fill: true,
          tension: 0.32,
        },
        {
          label: "Preço-alvo",
          data: labels.map(() => Number(product.target_price)),
          borderColor: "#ff4f52",
          pointRadius: 0,
          borderWidth: 2,
          borderDash: [8, 7],
          fill: false,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: "index",
        intersect: false,
      },
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          backgroundColor: "#091125",
          padding: 12,
          displayColors: false,
          callbacks: {
            label: (item) => `${item.dataset.label}: ${moneyFormatter.format(item.raw)}`,
          },
        },
      },
      scales: {
        x: {
          grid: {
            color: "rgba(9, 17, 37, 0.08)",
          },
          border: {
            display: false,
          },
          ticks: {
            color: "#5c6880",
            font: {
              family: "DM Sans",
              size: 12,
            },
          },
        },
        y: {
          suggestedMin: Math.max(0, Math.min(...prices, product.target_price) - 5),
          suggestedMax: Math.max(...prices, product.target_price) + 5,
          grid: {
            color: "rgba(9, 17, 37, 0.08)",
          },
          border: {
            display: false,
          },
          ticks: {
            color: "#5c6880",
            callback: (value) => `R$ ${value}`,
            font: {
              family: "DM Sans",
              size: 12,
            },
          },
        },
      },
    },
  });
}

async function fetchJson(path) {
  const response = await fetch(path, {
    headers: {
      Accept: "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`A consulta a ${path} retornou ${response.status}.`);
  }

  return response.json();
}

async function loadDemo() {
  let data = fallbackData;
  let isOnline = false;

  try {
    const [health, products] = await Promise.all([
      fetchJson("/health"),
      fetchJson("/products"),
    ]);
    const product = products[0];

    if (!product) {
      throw new Error("A demonstração ainda não possui produtos.");
    }

    const [history, alert] = await Promise.all([
      fetchJson(`/products/${product.id}/history`),
      fetchJson(`/products/${product.id}/alert`),
    ]);

    if (!history.length) {
      throw new Error("A demonstração ainda não possui histórico.");
    }

    data = {
      product,
      history: history.sort(byDateAscending),
      alert,
    };
    isOnline = health.status === "ok";
  } catch (error) {
    console.warn("Não foi possível carregar os dados ao vivo; usando a amostra local.", error);
  }

  setStatus(isOnline);
  renderSummary(data.product, data.history, data.alert);
  renderResponse(data.product, data.history);
  renderChart(data.product, data.history);
}

function enableCopyButton() {
  const button = document.querySelector("#copy-response");
  button.addEventListener("click", async () => {
    const code = document.querySelector("#response-code");
    const label = button.querySelector("span");

    try {
      await navigator.clipboard.writeText(code.dataset.raw || code.textContent);
      label.textContent = "Copiado";
      button.classList.add("is-copied");
      window.setTimeout(() => {
        label.textContent = "Copiar";
        button.classList.remove("is-copied");
      }, 1800);
    } catch (error) {
      label.textContent = "Selecione o texto";
      console.warn("O navegador bloqueou a cópia automática.", error);
    }
  });
}

enableCopyButton();
loadDemo();
