class ScopeEntry:
    def __init__(self, scope_type: str, semantic_stack_start_index: int):
        self.scope_type = scope_type
        self.semantic_stack_start_index = semantic_stack_start_index
