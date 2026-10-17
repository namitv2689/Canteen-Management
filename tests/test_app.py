import pytest

from app import Coupon, create_app, db


@pytest.fixture
def client(tmp_path):
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + str(tmp_path / 'test.db'),
    })
    with app.test_client() as client:
        with app.app_context():
            yield client


def test_home_page_renders(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'name="customer_name"' in resp.data


def create(client, name='Asha'):
    return client.post('/create', data={'customer_name': name})


def test_create_coupon_stores_customer_name(client):
    resp = client.post('/create', data={'customer_name': '  Ravi   Kumar '},
                       follow_redirects=True)
    assert resp.status_code == 200
    assert b'Ravi Kumar' in resp.data
    assert b'C00001' in resp.data
    coupon = Coupon.query.one()
    assert coupon.number == 'C00001'
    assert coupon.customer_name == 'Ravi Kumar'


def test_create_coupon_requires_name(client):
    resp = client.post('/create', data={'customer_name': '   '}, follow_redirects=True)
    assert b'Please enter the customer name' in resp.data
    assert Coupon.query.count() == 0

    create(client, 'x' * 81)
    assert Coupon.query.count() == 0


def test_name_falls_back_to_number(client):
    db.session.add(Coupon(number='C00009'))
    db.session.commit()
    coupon = Coupon.query.one()
    assert coupon.display_name == 'C00009'
    assert coupon.label == 'C00009'


def test_existing_database_gets_name_column(tmp_path):
    import sqlite3
    path = tmp_path / 'old.db'
    conn = sqlite3.connect(path)
    conn.execute('CREATE TABLE coupon (id INTEGER PRIMARY KEY, number VARCHAR(32) UNIQUE, '
                 'status VARCHAR(20), created_at DATETIME)')
    conn.execute("INSERT INTO coupon VALUES (1, 'C00001', 'served', '2026-08-29 13:00:12')")
    conn.commit()
    conn.close()

    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': f'sqlite:///{path}'})
    with app.app_context():
        assert db.session.get(Coupon, 1).display_name == 'C00001'


def test_serve_requeue_and_delete(client):
    create(client, 'Asha')
    create(client, 'Ben')
    first, second = Coupon.query.order_by(Coupon.id).all()

    resp = client.post('/manage', data={'action': 'serve', 'coupon_id': first.id},
                       follow_redirects=True)
    assert b'Asha (C00001) marked as served' in resp.data
    assert db.session.get(Coupon, first.id).status == 'served'

    client.post('/manage', data={'action': 'requeue', 'coupon_id': first.id})
    assert db.session.get(Coupon, first.id).status == 'pending'

    client.post('/manage', data={'action': 'delete', 'coupon_id': second.id})
    assert db.session.get(Coupon, second.id) is None


def test_manage_handles_missing_coupon(client):
    resp = client.post('/manage', data={'action': 'serve', 'coupon_id': 999},
                       follow_redirects=True)
    assert b'Coupon not found' in resp.data


def test_api_queue(client):
    for name in ('Asha', 'Ben', 'Chen'):
        create(client, name)
    data = client.get('/api/queue').get_json()
    assert data['now_serving']['display_name'] == 'Asha'
    assert data['now_serving']['number'] == 'C00001'
    assert data['now_serving']['label'] == 'Asha (C00001)'
    assert [c['display_name'] for c in data['up_next']] == ['Ben', 'Chen']
    assert data['stats'] == {'pending': 3, 'served': 0, 'total': 3}


def test_display_and_404(client):
    assert client.get('/display').status_code == 200
    assert client.get('/coupon/42').status_code == 404
