from typing import List, Dict, Union


# def test_refactor(row: int, actions: []):
#     schema: List[int] = []
#     if row == 1:
#         for cnt in range(count):
#             schema.append(1)
#     elif row == 2:
#         for cnt in actions:
#             if (cnt == 0 or (cnt % 2 == 0 and cnt != count - 1)) and count != 1:
#                 schema.append(2)
#             else:
#                 if cnt == count - 1 and cnt % 2 == 0:
#                     schema.append(1)

def refactor_keyboard(row: int, actions) -> List[int]:
    count = len(actions)
    schema: List[int] = []
    if row == 1:
        for cnt in range(count):
            schema.append(1)
    elif row == 2:
        for cnt in range(count):
            if (cnt == 0 or (cnt % 2 == 0 and cnt != count - 1)) \
                    and count != 1:
                schema.append(2)
            else:
                if cnt == count - 1 and cnt % 2 == 0:
                    schema.append(1)

    elif row == 3:
        for cnt in range(count):
            if (cnt == 0 or (cnt % 3 == 0 and cnt != count - 1) and cnt != count - 2) \
                    and count != 1 and count != 2:
                schema.append(3)
            else:
                if cnt == count - 2 and cnt % 3 == 0:
                    schema.append(2)
                elif cnt == count - 1 and cnt % 3 == 0:
                    schema.append(1)

    elif row == 4:
        for cnt in range(count):
            if (cnt == 0 or (
                    cnt % 4 == 0 and cnt != count - 1 and cnt != count - 1 and cnt != count - 3)) \
                    and count != 1 and count != 2 and count != 3:
                schema.append(4)
            else:
                if cnt == count - 3 and cnt % 4 == 0:
                    schema.append(3)
                elif cnt == count - 2 and cnt % 4 == 0:
                    schema.append(2)
                elif cnt == count - 1 and cnt % 4 == 0:
                    schema.append(1)

    return schema