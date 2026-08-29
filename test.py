# app.py
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'  # change for production
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'canteen.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Coupon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(32), unique=True, nullable=True)
    status = db.Column(db.String(20), default='pending')  # 'pending' or 'served'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Coupon {self.number} {self.status}>'

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET'])
def index():
    last = Coupon.query.order_by(Coupon.id.desc()).first()
    return render_template('index.html', last=last)

@app.route('/create', methods=['POST'])
def create_coupon():
    # Insert a row to get a unique auto-increment id
    c = Coupon()
    db.session.add(c)
    db.session.commit()
    # Format coupon number from the id (e.g., C00001)
    c.number = f"C{c.id:05d}"
    db.session.commit()
    return render_template('created.html', coupon=c)

@app.route('/manage', methods=['GET', 'POST'])
def manage():
    if request.method == 'POST':
        action = request.form.get('action')
        cid = request.form.get('coupon_id')
        if cid:
            coupon = Coupon.query.get(int(cid))
            if coupon:
                if action == 'serve':
                    coupon.status = 'served'
                    db.session.commit()
                elif action == 'delete':
                    db.session.delete(coupon)
                    db.session.commit()
        return redirect(url_for('manage'))
    pending = Coupon.query.filter_by(status='pending').order_by(Coupon.created_at).all()
    served = Coupon.query.filter_by(status='served').order_by(Coupon.created_at.desc()).limit(20).all()
    return render_template('manage.html', pending=pending, served=served)

if __name__ == '__main__':
    app.run(debug=True)