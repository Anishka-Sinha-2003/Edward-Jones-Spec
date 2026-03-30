(function () {
  const form = document.getElementById("upload-form");
  const fileInput = document.getElementById("pdf-file");
  const fieldsInput = document.getElementById("fields");
  const statusEl = document.getElementById("status");
  const submitBtn = document.getElementById("submit-btn");

  const resultsEmpty = document.getElementById("results-empty");
  const resultsLoading = document.getElementById("results-loading");
  const resultsSuccess = document.getElementById("results-success");
  const resultsError = document.getElementById("results-error");
  const resultsRows = document.getElementById("results-rows");
  const summaryTime = document.getElementById("summary-time");
  const summaryId = document.getElementById("summary-id");
  const errorTitle = document.getElementById("error-title");
  const errorMessage = document.getElementById("error-message");
  const technicalDetails = document.getElementById("technical-details");
  const technicalJson = document.getElementById("technical-json");

  const STATUS_COPY = {
    present: { label: "Present", desc: "This field appears to be filled or signed." },
    absent: { label: "Not present", desc: "This field looks empty or marked void." },
    uncertain: { label: "Unclear", desc: "We could not classify this field with high confidence." },
  };

  function showEmpty() {
    resultsEmpty.hidden = false;
    resultsLoading.hidden = true;
    resultsSuccess.hidden = true;
    resultsError.hidden = true;
    technicalDetails.hidden = true;
  }

  function showLoading() {
    resultsEmpty.hidden = true;
    resultsLoading.hidden = false;
    resultsSuccess.hidden = true;
    resultsError.hidden = true;
    technicalDetails.hidden = true;
  }

  function showError(title, message, raw) {
    resultsEmpty.hidden = true;
    resultsLoading.hidden = true;
    resultsSuccess.hidden = true;
    resultsError.hidden = false;
    errorTitle.textContent = title;
    errorMessage.textContent = message;
    if (raw) {
      technicalJson.textContent =
        typeof raw === "string" ? raw : JSON.stringify(raw, null, 2);
      technicalDetails.hidden = false;
    } else {
      technicalDetails.hidden = true;
    }
  }

  function formatTime(ms) {
    if (ms == null || ms === "") return "";
    const n = Number(ms);
    if (n < 1000) return "Completed in " + n + " ms";
    return "Completed in " + (n / 1000).toFixed(1) + " s";
  }

  function renderSuccess(data, requestId) {
    resultsEmpty.hidden = true;
    resultsLoading.hidden = true;
    resultsError.hidden = true;
    resultsSuccess.hidden = false;

    summaryTime.textContent = formatTime(data.processing_time_ms);
    summaryId.textContent = requestId ? "Ref: " + requestId : "";

    resultsRows.innerHTML = "";
    const results = data.results || [];
    results.forEach(function (row) {
      const st = row.status || "uncertain";
      const info = STATUS_COPY[st] || STATUS_COPY.uncertain;
      const pct = Math.round((Number(row.confidence) || 0) * 100);
      const li = document.createElement("li");
      li.className = "result-row";
      li.innerHTML =
        '<div class="result-row-head">' +
        '<span class="result-field-name">' +
        escapeHtml(row.field_name || "Field") +
        "</span>" +
        '<span class="status-pill status-' +
        escapeHtml(st) +
        '">' +
        escapeHtml(info.label) +
        "</span>" +
        "</div>" +
        '<p class="result-desc">' +
        escapeHtml(info.desc) +
        "</p>" +
        '<div class="confidence-wrap">' +
        '<span class="confidence-label">Confidence</span>' +
        '<div class="confidence-bar" role="progressbar" aria-valuenow="' +
        pct +
        '" aria-valuemin="0" aria-valuemax="100">' +
        '<span class="confidence-fill" style="width:' +
        pct +
        '%"></span>' +
        "</div>" +
        '<span class="confidence-pct">' +
        pct +
        "%</span>" +
        "</div>";
      resultsRows.appendChild(li);
    });

    technicalJson.textContent = JSON.stringify(data, null, 2);
    technicalDetails.hidden = false;
  }

  function escapeHtml(s) {
    const d = document.createElement("div");
    d.textContent = s;
    return d.innerHTML;
  }

  function friendlyErrorFromCode(code) {
    const map = {
      INVALID_PDF_FORMAT: "That file does not look like a valid PDF.",
      INVALID_FILE_TYPE: "Please upload a PDF file.",
      FILE_REQUIRED: "Please choose a PDF to upload.",
      FIELDS_INVALID: "One or more field names are not allowed. Use letters, numbers, and underscores only.",
      PDF_TOO_LARGE: "This file is too large. Maximum size is 50 MB.",
      PDF_PARSING_ERROR: "We could not read this PDF. It may be damaged or password-protected.",
      DETECTION_TIMEOUT: "The scan took too long. Try again with a smaller file.",
      DETECTOR_ERROR: "The scanner encountered an error. Try again later.",
    };
    return map[code] || "Something went wrong. Please try again.";
  }

  showEmpty();

  form.addEventListener("submit", async function (e) {
    e.preventDefault();
    const file = fileInput.files && fileInput.files[0];
    if (!file) {
      statusEl.textContent = "Please choose a PDF file.";
      return;
    }

    const fd = new FormData();
    fd.append("file", file, file.name);
    const fields = (fieldsInput.value || "").trim();
    if (fields) {
      fd.append("fields", fields);
    }

    statusEl.textContent = "Uploading and analyzing your document…";
    submitBtn.disabled = true;
    showLoading();

    try {
      const res = await fetch("/api/v1/detect", {
        method: "POST",
        body: fd,
      });
      const rid = res.headers.get("X-Request-ID") || "";
      const data = await res.json();

      if (!res.ok) {
        const err = data.error || {};
        const code = err.code || "";
        const friendly = friendlyErrorFromCode(code) || err.message || "Request failed.";
        showError("We couldn’t complete the scan", friendly, {
          httpStatus: res.status,
          requestId: rid,
          code: code,
          detail: err.message,
        });
        statusEl.textContent = "";
        return;
      }

      renderSuccess(data, rid);
      statusEl.textContent = "Done.";
    } catch (err) {
      showError(
        "Connection problem",
        "Check your network and that the service is running, then try again.",
        String(err)
      );
      statusEl.textContent = "";
    } finally {
      submitBtn.disabled = false;
    }
  });
})();
