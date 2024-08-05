import pytest
import respx
import tenacity

from prometheus_communicator.http import arequest


class TestArequest:
    @pytest.mark.asyncio
    async def test_success(self, respx_mock: respx.MockRouter):
        respx_mock.get("https://example.com").respond(text="Hello, world!")

        response = await arequest("GET", "https://example.com")

        assert response.text == "Hello, world!"
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_retry(self, respx_mock: respx.MockRouter):
        route = respx_mock.get("https://example.com").respond(status_code=418)

        with pytest.raises(tenacity.RetryError):
            await arequest("GET", "https://example.com", wait_multiplier=0)

        assert route.call_count == 3

    @pytest.mark.asyncio
    async def test_integration(self):
        response = await arequest(
            "POST", "https://httpbin.org/post", json={"key": "foobar"}
        )

        assert response.status_code == 200

        resp_data = response.json()
        assert resp_data["url"] == "https://httpbin.org/post"
        assert resp_data["json"] == {"key": "foobar"}
