# Unified build: illustrated guide

[中文指南](usage-zh.md) · [Back to README](../README.md)

These screenshots show the unified development build on PhotoCraft 0.20.1 (merge commit `d421251`). The published v0.4.0 ZIP predates the cutter, canvas clipboard export and shared language support in this merge. The full feature set below does not describe that older package.

## 1. Selection AI and multiple references

![English: selection AI composer, reference thumbnails and title-bar tools](../examples/usage/en/references.png)

1. Launch with `start.cmd`, open an image and create a selection.
2. Use the reference-images button to select multiple files, or drop pictures onto the AI composer. Click `×` below a thumbnail to remove that reference.
   Use **Paste reference image** or press `Ctrl+V` in the prompt to attach an image from the clipboard.
3. Refer to “reference 1” and “reference 2” in your prompt, then choose **Fill selection**, **Remove object** or **Generate image**. Codex validates actual attachment-count limits; local resource guards also apply.
4. Results become new layers with undo support. Right-click an AI result layer to adjust edge feathering.

This screenshot demonstrates inputs and attachments. No remote generation was run; it is not a generated-result example.

## 2. Long-image cutting

![English: large cutter window, red cut lines, plan controls and ZIP export](../examples/usage/en/cutter.png)

1. Click **Long image cutter** in the title bar to capture the current complete canvas.
2. Click the image or press `S` to add a cut. Drag red lines to adjust them; `Delete` removes the selected line and `Ctrl+Z` undoes a change.
3. Maximize the window or scroll through the source. Choose **Export PNG ZIP** to save the slices.
4. Import/export JSON plans to reuse cuts or exchange data with LongPicCutter.

## 3. Copy the full canvas

The **Copy image** button at the top of the first screenshot copies the full visible canvas to the system clipboard, preserving transparency. Paste into the destination application. **File → Export → Export to Clipboard** provides the same workflow without an export folder; the selection does not limit the copied area.

## 4. Switch languages

Choose **Edit → Preferences → Interface → Language**, select English or Chinese, then apply. The AI composer and cutter follow the setting; prompts and filenames retain their original text.

The geometric demo artwork was made for this project. Screenshots contain no user photos, account details or job history.
