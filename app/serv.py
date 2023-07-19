#!/usr/bin/env python

from flask import Flask, request, render_template, send_file
import os
import sys
import hashlib
import subprocess

TIMEOUT = 300
PDF_MIMETYPE = "application/pdf"

app = Flask(__name__)
cmd = 'pandoc -F pandoc-crossref /app/resume.md -o /app/resume.pdf --citeproc --bibliography=/root/src/resume.bib --pdf-engine lualatex -V luatexjapresetoptions=ipa -N'.split(
#cmd = 'pandoc -F pandoc-crossref /app/resume.md -o /app/resume.pdf --bibliography=/root/src/resume.bib --pdf-engine lualatex -V luatexjapresetoptions=ipa -N'.split(
    ' ')

token = os.environ.get('TOKEN')


def exec():
    # run code
    error = ''
    success = True
    try:
        process = subprocess.run(
            cmd,
            capture_output=True,
            encoding='utf-8',
            timeout=TIMEOUT)

        success = success and  process.returncode == 0
        error = process.stderr
    except subprocess.TimeoutExpired as e:
        success = False
        error = 'Timed out'

    return success, error


@app.route(f"/{token}", methods=['GET', 'POST'])
def index():
    code = ''
    error = ''

    if request.method == 'POST':
        code = request.form["code"]

        # if request has body, use it as MD input
        if not code:
            # Save MD to file
            filename = '/root/src/resume.md'
            with open(filename, mode='r') as f:
                code = f.read()

        with open('resume.md', mode='w') as f:
            f.write(code)

        # or, read original content
        success, error = exec()

        filename = "resume.pdf"

        if success:
            response = send_file(filename, as_attachment=True,
                                 attachment_filename=filename,
                                 mimetype=PDF_MIMETYPE)
            response.headers['Content-Disposition'] = 'inline; filename=%s' % filename
            print('stderr:', error, file=sys.stderr)
            return response

        print('stderr:', error, file=sys.stderr)

    return render_template('index.html', code=code, error=error)


def main():
    app.run(
        host="0.0.0.0",
        port=5000)
    
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000)
