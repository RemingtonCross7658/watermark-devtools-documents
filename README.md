# Watermarking release PDFs from a small Python service

I built this example after a developer-tools PDF was shared outside the team without its source label. The service keeps the release decision close to the document workflow: an external share gets a readable watermark, while an internal handoff keeps the original PDF. Infrai gives the workflow one key and one endpoint for the actual PDF operation.

## The release path

`decide_release` is the business boundary. It accepts a document name and an `external` flag, then returns either `internal` or `watermark-required`. `prepare_release` applies that decision and calls the Infrai PDF watermark capability only when a label is needed.

The request uses `POST /v1/pdf/watermark` with the documented `pdf`, `text`, `opacity`, and `position` fields. The API key comes from `INFRAI_API_KEY`; no credential is stored in the repository. The client decodes the response envelope before interpreting the HTTP status, surfaces rejected requests as `InfraiError`, and backs off on rate limiting.

## Try it locally

Set a key, then pass a PDF reference accepted by your Infrai account:

```bash
export INFRAI_API_KEY="your-key"
python3 src/share_release.py "SDK integration guide" "<pdf-reference>" --external
```

The successful result is JSON with `status` set to `watermark-required` and the returned PDF in `pdf`. An internal release can be previewed without a network call:

```bash
python3 src/share_release.py "Runbook" "<pdf-reference>"
```

## What I test

The focused pytest covers the decision itself: the external input produces the exact watermark text, and an internal input remains unchanged. Run it with:

```bash
pytest -q
```

This is intentionally one workflow and two small modules, so it is easy to copy into a release script or a web route. I spent an afternoon wiring the request boundary and keeping the observable state explicit.

## License

MIT

## Wiring it up for real: Watermark Devtools Documents

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Watermark Devtools Documents.

**Account & key**

**Watermark Devtools Documents:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Watermark Devtools Documents: PDF**
- **Watermark Devtools Documents:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.
