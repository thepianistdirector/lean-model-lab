# Fresh confirmation harmful illustration: r009

Study `negative-confirm-slice-study04`; family `record-lookup`; expected answer `CGMSA`. This is the prospectively selected descriptive illustration. Complete population outcomes remain in the accompanying request and paired tables.

There are 13 qualifying repeated harmful cases, including 11 direct lookups. Original and selected prompts independently resolve to the same answer.

## Complete original prompt

```text
RECORD-LANGUAGE v1
TASK record-lookup
RULES Last assignment wins. REF follows the final assignment of its target.
OUTPUT Resolve ASK to a VALUE. Reply with that alphabetic value only.
BEGIN
VALUE CMWGH CGCAC
VALUE CECER CCUAJ
VALUE CEUNK CPZYU
VALUE CIDED CYCHW
VALUE CTJCB CGELY
VALUE CMHBZ CPFDD
VALUE CONDH CGNKP
VALUE CGKXE CNMFD
VALUE COWPG CGMSA
VALUE CKDTJ CZLAS
VALUE CYHFU CRWVF
VALUE CJAXX CYTEA
VALUE CBANR CPOKQ
VALUE CHQPD CWTRS
VALUE CGIOA CMWFR
VALUE CKPUI CZPLD
VALUE CUNHE CAPXK
VALUE CHXJW CFSVO
VALUE COWPA CJKGJ
VALUE CMJJJ CPIVM
VALUE CKFJS CLQRP
VALUE CVTDO CUZDU
VALUE CRANO CDEAC
VALUE CWBYE CPBKQ
END
ASK COWPG
ANSWER:
```

## Complete selected prompt

```text
RECORD-LANGUAGE v1
TASK record-lookup
RULES Last assignment wins. REF follows the final assignment of its target.
OUTPUT Resolve ASK to a VALUE. Reply with that alphabetic value only.
BEGIN
VALUE COWPG CGMSA
END
ASK COWPG
ANSWER:
```

## Every native repetition

| Order | Arm | Native output | Correct | Finish |
| --- | --- | --- | --- | --- |
| AB | baseline | "CGMSA" | True | eos |
| AB | candidate | "COWPG" | False | eos |
| BA | baseline | "CGMSA" | True | eos |
| BA | candidate | "COWPG" | False | eos |

The companion `harmful-r009.json` retains token IDs reconstructed independently from the native SSE stream, native termination/cache/budget fields, all certificates, prompt counts and exported raw-file hashes. This case illustrates a mechanism; it is not a frequency estimate or an additional evaluation cohort.
