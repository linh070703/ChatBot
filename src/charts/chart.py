from flask import (
    Blueprint,
    render_template
)

chart = Blueprint('chart', __name__)

@chart.route('/compare')
def compare():
    return render_template('iframe.html')
