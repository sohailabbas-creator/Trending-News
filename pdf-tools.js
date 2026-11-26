(() => {
  const tool = document.querySelector(".tool-app[data-tool]");
  if (!tool) return;

  const form = tool.querySelector("form");
  const fileInput = tool.querySelector('input[type="file"]');
  const status = tool.querySelector(".tool-status");
  const download = tool.querySelector(".tool-download");
  const submit = form.querySelector('button[type="submit"]');
  let downloadUrl = "";

  const setStatus = (message, state) => {
    status.textContent = message;
    status.dataset.state = state || "";
  };

  const selectedFiles = () => Array.from(fileInput.files || []);

  const readPdf = async file => PDFLib.PDFDocument.load(await file.arrayBuffer());

  const pageNumbers = (value, pageCount) => {
    const numbers = [];
    if (!value.trim()) throw new Error("Enter at least one page number or range.");
    const parts = value.split(",").map(part => part.trim());
    if (parts.some(part => !part)) throw new Error("Enter page numbers separated by commas without empty entries.");

    for (const part of parts) {
      const match = part.match(/^(\d+)(?:\s*-\s*(\d+))?$/);
      if (!match) throw new Error("Use page numbers or ranges like 1, 3-5.");
      const first = Number(match[1]);
      const last = Number(match[2] || match[1]);
      if (first < 1 || last < first || last > pageCount) {
        throw new Error(`Page numbers must be between 1 and ${pageCount}.`);
      }
      for (let page = first; page <= last; page += 1) numbers.push(page - 1);
    }

    if (new Set(numbers).size !== numbers.length) {
      throw new Error("A page number appears more than once.");
    }
    return numbers;
  };

  const newPdfWithPages = async (source, indices) => {
    const output = await PDFLib.PDFDocument.create();
    const pages = await output.copyPages(source, indices);
    pages.forEach(page => output.addPage(page));
    return output;
  };

  const outputName = () => {
    const name = fileInput.files.length ? fileInput.files[0].name.replace(/\.[^.]+$/, "") : "sohail-tools";
    return `${name || "document"}-processed.pdf`;
  };

  const saveResult = async pdf => {
    const bytes = await pdf.save();
    if (downloadUrl) URL.revokeObjectURL(downloadUrl);
    downloadUrl = URL.createObjectURL(new Blob([bytes], { type: "application/pdf" }));
    download.href = downloadUrl;
    download.download = outputName();
    download.classList.add("visible");
    setStatus("Done. Your file was processed in this browser and is ready to download.", "success");
  };

  const process = async () => {
    const files = selectedFiles();
    const action = tool.dataset.tool;
    if (!files.length) throw new Error("Choose a file to continue.");

    if (action === "merge") {
      if (files.length < 2) throw new Error("Choose at least two PDF files to merge.");
      const output = await PDFLib.PDFDocument.create();
      for (const file of files) {
        const source = await readPdf(file);
        const pages = await output.copyPages(source, source.getPageIndices());
        pages.forEach(page => output.addPage(page));
      }
      return saveResult(output);
    }

    if (action === "jpg-to-pdf") {
      const output = await PDFLib.PDFDocument.create();
      for (const file of files) {
        const bytes = await file.arrayBuffer();
        const image = file.type === "image/png"
          ? await output.embedPng(bytes)
          : file.type === "image/jpeg" || file.type === "image/jpg"
            ? await output.embedJpg(bytes)
            : null;
        if (!image) throw new Error("Choose JPG or PNG images only.");
        const page = output.addPage([image.width, image.height]);
        page.drawImage(image, { x: 0, y: 0, width: image.width, height: image.height });
      }
      return saveResult(output);
    }

    const source = await readPdf(files[0]);
    const count = source.getPageCount();
    let output;

    if (action === "split" || action === "organize") {
      const value = tool.querySelector('input[name="pages"]').value;
      output = await newPdfWithPages(source, pageNumbers(value, count));
    } else if (action === "remove") {
      const removed = new Set(pageNumbers(tool.querySelector('input[name="pages"]').value, count));
      const remaining = source.getPageIndices().filter(page => !removed.has(page));
      if (!remaining.length) throw new Error("At least one page must remain in the output.");
      output = await newPdfWithPages(source, remaining);
    } else if (action === "rotate") {
      const selectedPages = tool.querySelector('input[name="pages"]').value.trim()
        ? pageNumbers(tool.querySelector('input[name="pages"]').value, count)
        : source.getPageIndices();
      for (const index of selectedPages) {
        const page = source.getPage(index);
        const current = page.getRotation().angle;
        page.setRotation(PDFLib.degrees((current + 90) % 360));
      }
      output = source;
    } else if (action === "add-page-numbers") {
      const font = await source.embedFont(PDFLib.StandardFonts.Helvetica);
      source.getPages().forEach((page, index) => {
        const { width } = page.getSize();
        const label = String(index + 1);
        const size = 10;
        page.drawText(label, {
          x: Math.max(12, (width - font.widthOfTextAtSize(label, size)) / 2),
          y: Math.max(2, Math.min(18, page.getHeight() - 14)),
          size,
          font,
          color: PDFLib.rgb(0.25, 0.28, 0.33)
        });
      });
      output = source;
    } else {
      throw new Error("This page is an informational guide, not an active file tool.");
    }
    await saveResult(output);
  };

  form.addEventListener("submit", async event => {
    event.preventDefault();
    download.classList.remove("visible");
    submit.disabled = true;
    setStatus("Processing locally in your browser…");
    try {
      if (!window.PDFLib) throw new Error("The PDF library could not load. Check your connection and try again.");
      await process();
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "The file could not be processed.", "error");
    } finally {
      submit.disabled = false;
    }
  });

  fileInput.addEventListener("change", () => {
    download.classList.remove("visible");
    status.textContent = "";
    if (tool.dataset.tool === "organize" && fileInput.files.length) {
      readPdf(fileInput.files[0]).then(pdf => {
        const pages = Array.from({ length: pdf.getPageCount() }, (_, index) => index + 1);
        tool.querySelector('input[name="pages"]').value = pages.join(", ");
      }).catch(() => {
        setStatus("Could not read this PDF. Check that it is a valid, unencrypted PDF.", "error");
      });
    }
  });

  window.addEventListener("pagehide", () => {
    if (downloadUrl) URL.revokeObjectURL(downloadUrl);
  });
})();
