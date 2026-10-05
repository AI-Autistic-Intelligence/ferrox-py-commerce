import pytest
from ferrox_py_commerce.services.transaction_state import TransactionStateService

class MockRedisClient:
    def __init__(self):
        self.store = {}
        self.expirations = {}
        
    async def setnx(self, key, value):
        if key in self.store:
            return 0
        self.store[key] = value
        return 1
        
    async def expire(self, key, seconds):
        self.expirations[key] = seconds
        return True
        
    async def get(self, key):
        return self.store.get(key)
        
    async def set(self, key, value, ex=None):
        self.store[key] = value
        if ex:
            self.expirations[key] = ex
        return True

class MockRedis:
    def __init__(self):
        self.client = MockRedisClient()
        
    async def connect(self):
        pass
        
    async def get(self, key):
        return await self.client.get(key)
        
    async def set(self, key, value, ex=None):
        return await self.client.set(key, value, ex)

@pytest.fixture
def state_service():
    return TransactionStateService(MockRedis())

@pytest.mark.asyncio
async def test_check_idempotency(state_service):
    # First time should be false (not duplicate)
    assert await state_service.check_idempotency("evt_1") is False
    
    # Second time should be true (duplicate)
    assert await state_service.check_idempotency("evt_1") is True

@pytest.mark.asyncio
async def test_transition_state(state_service):
    assert await state_service.transition_state("tx_1", "PAID") is True
    assert await state_service.transition_state("tx_1", "FAILED") is False
