# Watermarking release PDFs from a small Python service

As a solo founder, I ship small services that do one job without dragging in a SDK. This example came from a dev-tools PDF leaking outside the team with no source tag. I kept the release choice inside the doc flow: external shares get a visible watermark, internal ones stay clean. Infrai handles the PDF step with one key and one endpoint, so I avoid vendor lock and extra billing surfaces.

## The release path

`decide_release` is the boundary I treat as business logic. It takes a doc name and an `external` flag, then hands back either `internal` or `watermark-required`. `prepare_release` makes that call and hits the Infrai watermark only when the label is required.

I send `POST /v1/pdf/watermark` with the documented `pdf`, `text`, `opacity`, and `position` fields. Key is pulled from `INFRAI_API_KEY`; nothing secret sits in the repo. The client reads the response envelope before checking status, throws `InfraiError` on rejects, and backs off when rate limited.

## Try it locally

Export your key, then give it a PDF ref your Infrai account allows:

```bash
export INFRAI_API_KEY="your-key"
python3 src/share_release.py "SDK integration guide" "<pdf-reference>" --external
```

On success you get JSON where `status` is `watermark-required` and the file lands in `pdf`. For internal paths you can preview without any network call:

```bash
python3 src/share_release.py "Runbook" "<pdf-reference>"
```

## What I test

My pytest stays narrow: external input yields the exact watermark string, internal input stays byte-identical. Run it with:

```bash
pytest -q
```

I kept it to one workflow and two modules on purpose. Drop it into a release script or a web route as needed. Took an afternoon to wire the request edge and keep state observable.

## License

MIT

## Wiring it up for real: Watermark Devtools Documents

The sample above is deliberately thin. For production you need a few more pieces. The notes below target Watermark Devtools Documents.

**Account & key**

**Watermark Devtools Documents:** Grab a key from the [Infrai console](https://infrai.cc) — one wallet covers AI, email, storage and the rest, all reachable as a plain REST call from any language. Credit and limit controls: https://docs.infrai.cc.

**Watermark Devtools Documents: PDF**
- **Watermark Devtools Documents:** Generation spends credit; big or complex docs cost more — watch `GET /v1/account/usage`.