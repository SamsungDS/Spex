# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause

# Server Sent Event -- maybe submit to POST endpoint, get SSEs for progress bar
import hashlib
import json
import logging
import shutil
import tempfile
from contextlib import contextmanager
from os import environ
from pathlib import Path
from typing import Any, AsyncIterator, Dict, Iterator, Tuple

import quart
from quart import Quart, abort, make_response, redirect, request, url_for
from quart.wrappers.response import Response

from spex.jsonspec.defs import JSON
from spex.jsonspec.lint import Code
from spex.jsonspec.parserargs import ParserArgs
from spex.parse import parse_spec

SPEX_CACHE = environ.get("SPEX_CACHE", "true").lower() in ("1", "y", "yes", "true")


async def render_template(tpl: str, **ctx: str) -> str:
    bundle = ctx.get("bundle", False)
    assert app.static_folder is not None
    static = Path(app.static_folder)

    if bundle:
        with open(static / Path("alpinejs.3.13.5.js")) as fh:
            ctx["alpinejs_src"] = fh.read()
        with open(static / Path("bulma-0.9.4.min.css")) as fh:
            ctx["bulma_src"] = fh.read()
    else:
        ctx["bulma_url"] = url_for("static", filename="bulma-0.9.4.min.css")
        ctx["alpinejs_url"] = url_for("static", filename="alpinejs.3.13.5.js")

    return await quart.render_template(tpl, **ctx)


def md5sum(fpath: Path, chunk_bytes: int = 4096) -> str:
    hash_md5 = hashlib.md5()
    with open(fpath, "rb") as fh:
        for chunk in iter(lambda: fh.read(chunk_bytes), b""):
            hash_md5.update(chunk)

    return hash_md5.hexdigest()


def json_to_sse(data: JSON) -> bytes:
    return f"data: {json.dumps(data)}\n\n".encode("utf-8")


@contextmanager
def temp_dir() -> Iterator[Path]:
    tmp = tempfile.TemporaryDirectory()
    tmpd = Path(tmp.name)
    try:
        yield tmpd
    finally:
        tmp.cleanup()


app = Quart("spexsrv")
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024
SPEX_CACHE_TMPDIR = "SPEX_CACHE_TMPDIR"
SPEX_CACHE_LOOKUP = "SPEX_CACHE_LOOKUP"

logger = logging.getLogger("spexsrv.server")
logger.setLevel(logging.DEBUG)

lint_codes = {entry.name: entry.value for entry in Code}


@app.before_serving
async def _app_init() -> None:
    logger.info("spexsrv initializing...")

    print(f"Cache reports? {SPEX_CACHE}")
    if SPEX_CACHE:
        print("export SPEX_CACHE=n to disable (n, no, false or 0 is acceptable)")
    app.config.update(
        {SPEX_CACHE_TMPDIR: tempfile.TemporaryDirectory(), SPEX_CACHE_LOOKUP: {}}
    )
    assert app.template_folder is not None, "expected templates_folder to be set"
    assert app.static_folder is not None, "expected static_folder to be set"
    print(f"  * Template Directory: {app.template_folder}")
    print(f"  * Static Assets Directory: {app.static_folder}")


@app.after_serving
async def _app_shutdown() -> None:
    logging.info("spexsrv shutting down...")
    app.config[SPEX_CACHE_TMPDIR].cleanup
    del app.config[SPEX_CACHE_TMPDIR]
    del app.config[SPEX_CACHE_LOOKUP]


@app.route("/")
async def index() -> str:
    return await render_template("upload-form.html", title="Upload Specification")


@app.route("/report/<hash>")
async def report(hash: str) -> str:
    # TODO: enable this part again this actually looks for the document requested
    json_fpath = app.config[SPEX_CACHE_LOOKUP].get(hash)
    if json_fpath is None or not json_fpath.is_file():
        abort(404)

    print(json_fpath)
    with open(json_fpath) as fh:
        report_json = json.load(fh)

    bundle = request.args.get("bundle", default=None, type=str) is not None

    tpl_ctx = {
        "title": "Report",
        "report_json": report_json,
        "lint_codes": lint_codes,
        "link_self": url_for("report", hash=hash, bundle=1) if not bundle else None,
        "bundle": bundle,
    }

    return await render_template("report.html", **tpl_ctx)


@app.route("/parse", methods=["POST"])
async def spec_parse() -> Response | Tuple[str, int, Dict[Any, Any]]:
    files = await request.files

    if "document" not in files:
        return "document missing", 422, {}

    if "text/event-stream" not in request.accept_mimetypes:
        abort(400)

    spec = files["document"]

    tdir = tempfile.TemporaryDirectory()
    tdir_path = Path(tdir.name)
    dst = tdir_path / spec.filename
    await spec.save(dst)
    hash = md5sum(dst)
    report_url = url_for("report", hash=hash)
    json_path = app.config[SPEX_CACHE_LOOKUP].get(hash)
    if SPEX_CACHE and json_path:
        # redirect immediately to the existing report
        return redirect(report_url)  # type: ignore

    pargs = ParserArgs(
        output_dir=Path(tdir_path),
        skip_fig_on_error=True,  # required for caching making sense
        lint_codes_ignore=[],
    )

    async def sse_events() -> AsyncIterator[bytes]:
        try:
            gen = parse_spec(dst, pargs, yield_progress=True)
            try:
                while True:
                    phase, fig_ndx, num_figs = next(gen)
                    yield json_to_sse(
                        {
                            "type": "progress-update",
                            "phase": phase,
                            "fig_ndx": fig_ndx,
                            "num_figs": num_figs,
                        }
                    )
            except StopIteration as e:
                json_fpath = e.value
                cache_entry = Path(app.config[SPEX_CACHE_TMPDIR].name) / json_fpath.name
                shutil.copy(json_fpath, cache_entry)
                print(f"hash({hash}) -> {cache_entry}")
                app.config[SPEX_CACHE_LOOKUP][hash] = cache_entry
                yield json_to_sse({"type": "report-completed", "url": report_url})
        finally:
            tdir.cleanup()

    # skip parsing..
    # then generate, then return big ass report doc
    rsp = await make_response(
        sse_events(),
        {
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Transfer-Encoding": "chunked",
        },
    )
    rsp.timeout = 60  # type: ignore
    return rsp  # type: ignore
