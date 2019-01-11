#! /usr/bin/env python



# usage example:
# for x in ../ryu/tests/unit/ofproto/json/**/*.json;do echo $x;./normalize_json.py < $x > xx&& mv xx $x;done

import json
import sys

j = sys.stdin.read()
d = json.loads(j)
print json.dumps(d, ensure_ascii=True, indent=3, sort_keys=True)
