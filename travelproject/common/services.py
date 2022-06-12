from typing import List, Dict, Any, Tuple

from travelproject.common.types import DjangoModelType


def model_update(
    *, instance: DjangoModelType, fields: List[str], data: Dict[str, Any], **kwargs
) -> Tuple[DjangoModelType, bool]:
    has_updated = False

    exclude = None
    if kwargs.get("exclude"):
        exclude = kwargs.get("exclude")

    for field in fields:

        if field not in data:
            continue

        if getattr(instance, field) != data[field]:
            has_updated = True
            setattr(instance, field, data[field])

    if has_updated:
        instance.full_clean(exclude)
        instance.save(update_fields=fields)

    return instance, has_updated
