# Fresh confirmation beneficial illustration: r003

Study `negative-confirm-slice-study04`; family `record-lookup`; expected answer `CAMYD`. This is the prospectively selected descriptive illustration. Complete population outcomes remain in the accompanying request and paired tables.

There are 24 qualifying repeated beneficial cases, including 12 direct lookups. Original and selected prompts independently resolve to the same answer.

## Complete original prompt

```text
RECORD-LANGUAGE v1
TASK record-lookup
RULES Last assignment wins. REF follows the final assignment of its target.
OUTPUT Resolve ASK to a VALUE. Reply with that alphabetic value only.
BEGIN
VALUE COUKW CAMYD
VALUE CKITI CDJNH
VALUE CDGIF CXEQT
VALUE CIVLT CJFFQ
VALUE CYEYG CDXYQ
VALUE CHEID CMVAO
VALUE CFVJS CZHMY
VALUE CNXML CLSGD
VALUE CPOIL CLRQM
VALUE COIDA CAGHW
VALUE CZEBQ CTVII
VALUE CYGMN CKKRX
VALUE CNNYD COXUT
VALUE CJVOX CCEYQ
VALUE CFYKO CIDBP
VALUE CMEDF CKZFP
VALUE CRENP CMDZO
VALUE CDQFK CADKL
VALUE CWCQK COKSJ
VALUE CQXOM CMCXO
VALUE CYLWJ CGVHC
VALUE COUKA CEISL
VALUE CZLCA CSJPE
VALUE CHNGW CSNDB
END
ASK COUKW
ANSWER:
```

## Complete selected prompt

```text
RECORD-LANGUAGE v1
TASK record-lookup
RULES Last assignment wins. REF follows the final assignment of its target.
OUTPUT Resolve ASK to a VALUE. Reply with that alphabetic value only.
BEGIN
VALUE COUKW CAMYD
END
ASK COUKW
ANSWER:
```

## Every native repetition

| Order | Arm | Native output | Correct | Finish |
| --- | --- | --- | --- | --- |
| AB | baseline | "COKSW" | False | eos |
| AB | candidate | "CAMYD" | True | eos |
| BA | baseline | "COKSW" | False | eos |
| BA | candidate | "CAMYD" | True | eos |

The companion `beneficial-r003.json` retains token IDs reconstructed independently from the native SSE stream, native termination/cache/budget fields, all certificates, prompt counts and exported raw-file hashes. This case illustrates a mechanism; it is not a frequency estimate or an additional evaluation cohort.
