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
    assert b'Generate New Coupon' in resp.data


def test_create_coupon_assigns_number(client):
    resp = client.post('/create', follow_redirects=True)
    assert resp.status_code == 200
    assert b'C00001' in resp.data
    assert Coupon.query.one().number == 'C00001'


def test_serve_requeue_and_delete(client):
    client.post('/create')
    client.post('/create')
    first, second = Coupon.query.order_by(Coupon.id).all()

    resp = client.post('/manage', data={'action': 'serve', 'coupon_id': first.id},
                       follow_redirects=True)
    assert b'marked as served' in resp.data
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
    for _ in range(3):
        client.post('/create')
    data = client.get('/api/queue').get_json()
    assert data['now_serving']['number'] == 'C00001'
    assert [c['number'] for c in data['up_next']] == ['C00002', 'C00003']
    assert data['stats'] == {'pending': 3, 'served': 0, 'total': 3}


def test_display_and_404(client):
    assert client.get('/display').status_code == 200
    assert client.get('/coupon/42').status_code == 404
