
def make_authenticated_post(
        authenticated_client,
        url,
        data=None,
        content_type='application/json',
        headers=None,
):
    headers = headers or {}
    headers['Authorization'] = f'Bearer {authenticated_client.access_token}'
    return authenticated_client.post(
        url,
        data=data,
        content_type=content_type,
        headers=headers,
    )


def make_authenticated_put(
        authenticated_client,
        url,
        data=None,
        content_type='application/json',
        headers=None,
):
    headers = headers or {}
    headers['Authorization'] = f'Bearer {authenticated_client.access_token}'
    return authenticated_client.put(
        url,
        data=data,
        content_type=content_type,
        headers=headers,
    )


def make_authenticated_delete(
        authenticated_client,
        url,
        data=None,
        content_type='application/json',
        headers=None,
):
    headers = headers or {}
    headers['Authorization'] = f'Bearer {authenticated_client.access_token}'
    return authenticated_client.delete(
        url,
        data=data,
        content_type=content_type,
        headers=headers,
    )
