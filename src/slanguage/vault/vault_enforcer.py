
class VaultCategoryError(Exception):
    pass

class OmniLockTriggered(Exception):
    pass

class VaultCategoryEnforcer:
    def __init__(self, operator_name="slanguage"):
        self.operator = operator_name
        self.entity_categories = {}
        self.construct_requirements = {}

    def grant_category(self, entity: str, category: str):
        self.entity_categories.setdefault(entity, set()).add(category)

    def bind_construct(self, construct: str, categories):
        self.construct_requirements[construct] = set(categories)

    def get_granted(self, entity: str) -> set:
        return set(self.entity_categories.get(entity, set()))

    def get_required(self, construct: str) -> set:
        return set(self.construct_requirements.get(construct, set()))

    def check_access(self, entity: str, construct: str):
        if entity == self.operator:
            return True

        if construct not in self.construct_requirements:
            raise VaultCategoryError(f"Construct '{construct}' has no category binding.")

        required = self.construct_requirements[construct]
        granted = self.entity_categories.get(entity, set())

        if not required.intersection(granted):
            raise OmniLockTriggered(
                f"OMNI-LOCK: '{entity}' lacks categories {required} for '{construct}'."
            )

        return True
