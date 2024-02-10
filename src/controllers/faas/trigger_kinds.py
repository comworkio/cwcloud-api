from utils.triggers import _supported_triggers_kinds

def get_all_triggers_kinds():
    return {
        'status': 'ok',
        'code': 200,
        'kinds': _supported_triggers_kinds
    }
