Multi-Image Upload Plan (Default Limits)

Goals
- Allow up to 9 images per question.
- Enforce per-image size limit: 5 MB.
- Enforce total request size cap: ~50 MB.
- Keep paste and drag-and-drop behaviors, now multi-image aware.

Frontend Changes
- Update upload input to support multiple files and update the label/hint text.
- Replace single-image preview with a grid preview (thumbnails + remove buttons).
- Update paste and drag-and-drop handlers to accept multiple images.
- Validate count and size client-side; show clear error messages.

Backend Changes (Flask)
- Update /api/query/image to read request.files.getlist("image") (and accept legacy single file).
- Validate max count and per-image size; return 400 on violations.
- Save all images and store list fields in session JSON:
  - image_paths (filenames)
  - image_filepaths (absolute or upload folder paths)
- Increase MAX_CONTENT_LENGTH to 50 MB.

Doubao Client Changes
- Add multi-image message builder that inserts multiple image_url entries in messages[1].content.
- Update solve_with_image and stream_with_reasoning to accept image_paths list.
- Preserve existing single-image behavior for backward compatibility.

Streaming + Deep Think
- Use image_filepaths list for image_stream and image_deep flows.
- Ensure both normal and deep_think flows pass all images to Doubao.

Production Config
- Update run_production.py max_request_body_size to 50 MB.

Testing + Docs
- Add a script under tests/api to upload multiple images and verify success.
- Document limits and supported formats in a short README note.
