# JNI / Native String Decoding (Java char behavior)

When decompiling an app that uses string obfuscation (such as XORing characters against an array), replicating that logic in Python requires attention to how Java handles strings.

Java `char` is a 16-bit Unicode character, whereas Python strings handle characters fundamentally differently under the hood, but `ord()` can return larger values.

When you see Java code like:
```java
char[] cArr = {'a', 193, ...};
sb.append((char) (str.charAt(i) ^ cArr[i % 265]));
```

The correct Python replication needs a bitwise mask to mimic the `(char)` cast which truncates to 16 bits (0-65535):

```python
def decode_string(str_val):
    cArr = [97, 193, ...] # Replicate array
    res = ""
    for i in range(len(str_val)):
        char_val = ord(str_val[i])
        key_val = cArr[i % len(cArr)]
        # Mask with 0xFFFF to mimic Java (char) cast behavior
        res += chr((char_val ^ key_val) & 0xFFFF)
    return res
```

Failure to mask correctly with `0xFFFF` (e.g. using `0xFF` or none at all) will result in garbage data or UnicodeDecodeErrors when characters exceed typical ASCII boundaries but need to remain within standard 16-bit space.