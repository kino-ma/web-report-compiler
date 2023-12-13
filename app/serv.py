#!/usr/bin/env python

import os
import sys
import subprocess

from flask import Flask, request, render_template, send_file

from cmd import PandocCmd

TIMEOUT = 300
PDF_MIMETYPE = "application/pdf"

app = Flask(__name__)

token = os.environ.get("TOKEN")


def exec(pandoc_command: PandocCmd):
    # run code
    error = ""
    success = True
    cmd = pandoc_command.command()
    print("executing command:", cmd)
    try:
        process = subprocess.run(
            cmd, capture_output=True, encoding="utf-8", timeout=TIMEOUT
        )

        success = success and process.returncode == 0
        error = process.stderr
    except subprocess.TimeoutExpired:
        success = False
        error = "Timed out"

    return success, error


@app.route(f"/{token}", methods=["GET", "POST"])
def index():
    code = ""
    error = ""

    if request.method == "POST":
        code = request.form["code"]

        # if request has body, use it as MD input
        if not code:
            # Save MD to file
            filename = "./data/src.md"
            with open(filename, mode="r") as f:
                code = f.read()

        with open("./data/resume.md", mode="w") as f:
            f.write(code)

        # or, read original content
        command = PandocCmd()
        success, error = exec(command)

        filename = "resume.pdf"

        if success:
            response = send_file(
                filename,
                as_attachment=True,
                attachment_filename=filename,
                mimetype=PDF_MIMETYPE,
            )
            response.headers["Content-Disposition"] = "inline; filename=%s" % filename
            print("stderr:", error, file=sys.stderr)
            return response

        print("stderr:", error, file=sys.stderr)

    return render_template("index.html", code=code, error=error)


def main():
    app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
