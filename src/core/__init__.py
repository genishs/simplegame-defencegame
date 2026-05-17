"""core 패키지: 엔진 인프라(외부 의존 없는 코어 서비스).

이 패키지는 ``tkinter``를 사용하지만, 다른 ``src.*`` 서브패키지를 import 하지 않는다.
(의존 방향 규칙: core ← systems ← entities ← scenes ← ui)
"""
from __future__ import annotations
