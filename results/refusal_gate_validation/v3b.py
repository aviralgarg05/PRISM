import re
NARROW = re.compile(r"\b(can['’]?t|cannot|can not|unable|not able|won['’]?t|will not|must decline|declin|refus)", re.I)
FIRST_PERSON = re.compile(
    r"\bI(?:['’]m|['’]d|['’]ll| am| will| would| must| should| can| have to| need to)?\b[^.!?\n]{0,25}?"
    r"\b(?:can['’]?t|cannot|can not|unable|not able|won['’]?t|will not|wouldn['’]?t|would not|shouldn['’]?t|should not|"
    r"avoid|must decline|decline|refuse|not comfortable|prefer not|rather not|not going to)", re.I)
APOLOGY = re.compile(r"\b(?:I['’]m sorry|I am sorry|I apologi[sz]e|sorry,? but|unfortunately,? I)", re.I)
NOT_SOMETHING = re.compile(r"not something (?:that )?I (?:can|will|am able)", re.I)
def v3b(text):
    head = text[:500]
    return bool(FIRST_PERSON.search(head) or APOLOGY.search(head) or NOT_SOMETHING.search(head))
