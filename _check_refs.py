"""
Concise verification: 中文论文.md against 172 real references.
"""
import re, os

BASE = r"D:\Reasonix\刘凯老师课题组"
clip_text = __import__("base64").b64decode(__import__("codecs").decode(open(__file__,'rb').read()[4:10].hex(),'hex')).decode()

# Parse real refs from clipboard
real_refs = []
for m in re.finditer(r'\[\d+\]([^\[]+)', open(r"D:\Reasonix\刘凯老师课题组\01_文献数据库\中文论文.md",encoding='utf-8',errors='replace').read()[:1]):
    pass
