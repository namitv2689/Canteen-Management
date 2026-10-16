"""Canteen Coupon Management System - Flask web application."""
import os
from datetime import datetime, timezone

from flask import (
    Flask, abort, flash, jsonify, redirect, render_template, request, url_for,
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text

db = SQLAlchemy()
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Coupon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(32), unique=True, nullable=True)
    customer_name = db.Column(db.String(80), nullable=True)
    status = db.Column(db.String(20), default='pending')  # 'pending' or 'served'
    created_at = db.Column(db.DateTime, default=utcnow)

    @property
    def display_name(self):
        # Coupons created before names were collected fall back to their number.
        return self.customer_name or self.number

    @property
    def label(self):
        """Name and number together, e.g. 'Arjun (C00002)'."""
        if self.customer_name:
            return f'{self.customer_name} ({self.number})'
        return self.number

    def to_dict(self):
        return {
            'id': self.id,
            'number': self.number,
            'customer_name': self.customer_name,
            'display_name': self.display_name,
            'label': self.label,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<Coupon {self.number} {self.status}>'


def queue_stats():
    pending = Coupon.query.filter_by(status='pending').count()
    served = Coupon.query.filter_by(status='served').count()
    return {'pending': pending, 'served': served, 'total': pending + served}


MAX_NAME_LENGTH = 80


def upgrade_schema():
    """Add columns introduced after the first release to existing databases."""
    columns = {c['name'] for c in inspect(db.engine).get_columns('coupon')}
    if 'customer_name' not in columns:
        with db.engine.begin() as conn:
            conn.execute(text('ALTER TABLE coupon ADD COLUMN customer_name VARCHAR(80)'))


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret-key'),
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            'DATABASE_URL', 'sqlite:///' + os.path.join(BASE_DIR, 'canteen.db')
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    with app.app_context():
        db.create_all()
        upgrade_schema()

    @app.context_processor
    def inject_globals():
        return {'current_year': datetime.now().year}

    @app.template_filter('localtime')
    def format_time(value, fmt='%d %b %Y, %I:%M %p'):
        if not value:
            return ''
        return value.replace(tzinfo=timezone.utc).astimezone().strftime(fmt)

    @app.route('/')
    def index():
        last = Coupon.query.order_by(Coupon.id.desc()).first()
        now_serving = (Coupon.query.filter_by(status='pending')
                       .order_by(Coupon.created_at).first())
        return render_template('index.html', last=last, now_serving=now_serving,
                               stats=queue_stats())

    @app.route('/create', methods=['POST'])
    def create_coupon():
        name = ' '.join(request.form.get('customer_name', '').split())
        if not name:
            flash('Please enter the customer name.', 'error')
            return redirect(request.referrer or url_for('index'))
        if len(name) > MAX_NAME_LENGTH:
            flash(f'Name must be at most {MAX_NAME_LENGTH} characters.', 'error')
            return redirect(request.referrer or url_for('index'))
        # Insert a row to get a unique auto-increment id, then derive the number.
        coupon = Coupon(customer_name=name)
        db.session.add(coupon)
        db.session.flush()
        coupon.number = f"C{coupon.id:05d}"
        db.session.commit()
        return redirect(url_for('coupon_detail', coupon_id=coupon.id))

    @app.route('/coupon/<int:coupon_id>')
    def coupon_detail(coupon_id):
        coupon = db.session.get(Coupon, coupon_id) or abort(404)
        ahead = 0
        if coupon.status == 'pending':
            ahead = Coupon.query.filter(Coupon.status == 'pending',
                                        Coupon.id < coupon.id).count()
        return render_template('created.html', coupon=coupon, ahead=ahead)

    @app.route('/manage', methods=['GET', 'POST'])
    def manage():
        if request.method == 'POST':
            action = request.form.get('action')
            cid = request.form.get('coupon_id', type=int)
            coupon = db.session.get(Coupon, cid) if cid else None
            if not coupon:
                flash('Coupon not found.', 'error')
            elif action == 'serve' and coupon.status == 'pending':
                coupon.status = 'served'
                db.session.commit()
                flash(f'{coupon.label} marked as served.', 'success')
            elif action == 'requeue' and coupon.status == 'served':
                coupon.status = 'pending'
                db.session.commit()
                flash(f'{coupon.label} moved back to the queue.', 'info')
            elif action == 'delete':
                name = coupon.label
                db.session.delete(coupon)
                db.session.commit()
                flash(f'Coupon for {name} deleted.', 'info')
            else:
                flash('That action could not be completed.', 'error')
            return redirect(url_for('manage'))

        pending = (Coupon.query.filter_by(status='pending')
                   .order_by(Coupon.created_at, Coupon.id).all())
        served = (Coupon.query.filter_by(status='served')
                  .order_by(Coupon.created_at.desc()).limit(20).all())
        return render_template('manage.html', pending=pending, served=served,
                               stats=queue_stats())

    @app.route('/display')
    def display():
        return render_template('display.html')

    @app.route('/api/queue')
    def api_queue():
        pending = (Coupon.query.filter_by(status='pending')
                   .order_by(Coupon.created_at, Coupon.id).limit(10).all())
        served = (Coupon.query.filter_by(status='served')
                  .order_by(Coupon.created_at.desc()).limit(5).all())
        return jsonify({
            'now_serving': pending[0].to_dict() if pending else None,
            'up_next': [c.to_dict() for c in pending[1:]],
            'recently_served': [c.to_dict() for c in served],
            'stats': queue_stats(),
        })

    @app.errorhandler(404)
    def not_found(_error):
        return render_template('404.html'), 404

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG', '1') == '1')
