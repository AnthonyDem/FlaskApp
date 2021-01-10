from app import client

def test_post():
    data = {
        'name': 'first test',
        'description': 'this is first test',
    }

    res = client.post('/videos', json=data)

    assert res.status_code == 200
    assert res.get_json()['name'] == data['name']