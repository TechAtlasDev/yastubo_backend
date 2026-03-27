import inspect
import uuid
from functools import wraps
from typing import Callable
from app.modules.audit import service as audit_service


def audited(action: str, entity: str):
    def decorator(func: Callable):
        sig = inspect.signature(func)

        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Map positional arguments to their names
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            all_args = bound_args.arguments

            # Extract db
            db = all_args.get("db")

            # Try to find user information
            current_user = all_args.get("current_user") or all_args.get("user")
            user_id = getattr(current_user, "id", None) if current_user else None

            if not user_id:
                # Try common naming conventions for user ID in services
                user_id = (
                    all_args.get("created_by")
                    or all_args.get("updated_by")
                    or all_args.get("user_id")
                    or all_args.get("changed_by")
                    or all_args.get("registered_by")
                    or all_args.get("issued_by")
                    or all_args.get("cancelled_by")
                    or all_args.get("registered_by")
                )

            result = await func(*args, **kwargs)

            # If successful, log the action
            if db:
                # Try to extract entity_id from result if it's an object with id
                entity_id = getattr(result, "id", None)

                # If result is not an object but maybe the ID itself
                if not entity_id and isinstance(
                    result, (str, bytes, int, float, uuid.UUID)
                ):
                    # Check if it looks like a UUID
                    try:
                        if isinstance(result, uuid.UUID):
                            entity_id = result
                    except Exception:
                        pass

                await audit_service.log(
                    db=db,
                    action=action,
                    entity=entity,
                    user_id=user_id,
                    entity_id=entity_id,
                )

            return result

        return wrapper

    return decorator
