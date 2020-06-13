from matplotlib import pyplot as plt
from flask import flask, request
from io import StringIO

app = Flask(__name__)

def get_ax():
    fig, ax = plt.subplots(figsize=(8,8))
    ax.set_xlim(-8, 8)
    ax.set_ylim(-8, 8)
    ax.spines['left'].set_position('zero')
    ax.spines['bottom'].set_position('zero')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    return ax

@app.route('/plot.svg')
def show_plot():
    ax = get_ax()

    # "save" to a string in the SVG format
    f = StringIO()
    ax.get_figure().savefig(f, format="svg")
    svg_data = f.getvalue()

    html = "<html><body><h1>Guess that function</h1>{}</body></html>"
    return html.format(svg_data)

if __name__ == '__main__':
    app.run(host="0.0.0.0")
    
def f(x):
    return -abs(-(x**2))

@app.route('/guess', methods=["POST"])
def guess():
    parts = request.get_data(as_text=True).split(",")
    x = float(parts[0])
    y = float(parts[1])
    actual = f(x)
    if actual == y:
        return "perfect\n"
    return "f({}) is {}, not {}\n".format(x, actual, y)