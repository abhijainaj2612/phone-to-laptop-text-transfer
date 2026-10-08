import pytest
from relay_server.connection_manager import ConnectionManager

class Socket:
    def __init__(self): self.messages=[]
    async def send_json(self, msg): self.messages.append(msg)

@pytest.mark.asyncio
async def test_pair_and_route():
    manager, socket = ConnectionManager(300), Socket()
    code = await manager.connect_pc("d1", "secret", socket)
    assert manager.pair(code) == "d1"
    assert await manager.send_text("d1", {"text":"safe"})
    assert socket.messages == [{"text":"safe"}]

@pytest.mark.asyncio
async def test_offline_device():
    assert not await ConnectionManager(300).send_text("missing", {})
