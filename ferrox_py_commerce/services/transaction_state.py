from ferrox_py.core.provider import injectable
from ferrox_py.core.errors import FerroxError
from ferrox_py.databases.redis import RedisCacheService

@injectable()
class TransactionStateService:
    def __init__(self, redis: RedisCacheService):
        self.redis = redis

    async def check_idempotency(self, event_id: str) -> bool:
        """
        Returns True if the event has already been processed.
        Uses Redis to set a key with a 24-hour expiration.
        """
        # Ensure redis is connected
        if not self.redis.client:
            await self.redis.connect()
            
        key = f"webhook_evt:{event_id}"
        
        # setnx returns 1 if key was set (new event), 0 if it already existed
        is_new = await self.redis.client.setnx(key, "processed")
        if is_new:
            # Expire key after 24 hours to free up memory
            await self.redis.client.expire(key, 86400)
            return False
            
        return True

    async def transition_state(self, transaction_id: str, new_state: str) -> bool:
        """
        Simple State Machine: PENDING -> PAID -> FAILED.
        Returns True if transition is valid and executed.
        """
        state_key = f"tx_state:{transaction_id}"
        
        # In a real app, you would use a Redis Transaction (MULTI/EXEC) or Lua script here
        current_state = await self.redis.get(state_key)
        
        if current_state == "PAID":
            # Cannot transition out of PAID via standard webhooks (maybe refund later)
            print(f"Transaction {transaction_id} is already PAID. Ignoring {new_state}.")
            return False
            
        await self.redis.set(state_key, new_state, ex=604800) # Keep state for 7 days
        print(f"Transaction {transaction_id} transitioned to {new_state}")
        return True
