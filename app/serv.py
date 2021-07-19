from flask import Flask, request, render_template, send_file
import os
import hashlib
import subprocess

TIMEOUT = 60
PDF_MIMETYPE = "application/pdf"

app = Flask(__name__)
cmd = 'pandoc -F pandoc-crossref /app/report.md -o /app/report.pdf --pdf-engine lualatex -V luatexjapresetoptions=ipa -N'.split(
    ' ')

token = os.environ.get('TOKEN')


def exec():
    # run code
    error = ''
    try:
        process = subprocess.run(
            cmd,
            capture_output=True,
            encoding='utf-8',
            timeout=TIMEOUT)

        error = process.stderr
    except subprocess.TimeoutExpired as e:
        error = 'Timed out'

    return error


@app.route(f"/{token}", methods=['GET', 'POST'])
def index():
    code = ''
    error = ''

    if request.method == 'POST':
        code = request.form["code"]

        # if request has body, use it as MD input
        if not code:
            # Save MD to file
            filename = '/root/src/report.md'
            with open(filename, mode='r') as f:
                code = f.read()

        with open('report.md', mode='w') as f:
            f.write(code)

        # or, read original content
        error = exec()

        filename = "report.pdf"

        if not error:
            response = send_file(filename, as_attachment=True,
                                 attachment_filename=filename,
                                 mimetype=PDF_MIMETYPE)
            response.headers['Content-Disposition'] = 'inline; filename=%s' % filename
            return response

    return render_template('index.html', code=code, error=error)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000)
