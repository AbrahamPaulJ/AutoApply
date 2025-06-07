from flask import Flask, render_template, request, redirect, url_for
import subprocess

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        ui_mode = request.form.get('ui_mode', '0')
        looprange = request.form.get('looprange', '5')
        user = request.form.get('user', 'abraham')
        headless = request.form.get('headless', '0')

        # Run your asyncscrape.py script with parameters
        # This will start it asynchronously (non-blocking)
        subprocess.Popen(['python', 'asyncscrape.py', ui_mode, looprange, user, headless])

        return redirect(url_for('index'))

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
