# Technical Debt Log — Ground Control Station

## Overview
This document identifies code smells and technical debt found in the 
inherited `legacy_stats.py` module (Week 12 workshop). Each smell is 
documented with an explanation of why it is problematic and how it was 
or should be addressed.

---

## Code Smell 1: Manual JSON Validation (Framework Misuse)

**Location**: `legacy_stats.py` — `calc_stats` function, top of function

**The Problem**:
```python
def calc_stats(data: dict):
    try:
        d = data["dist"]
        b = data["batt"]
    except KeyError as e:
        return {"error": f"Missing field: {e}"}, 400
```

**Why it is bad**: FastAPI provides automatic request validation using 
Pydantic models. Manually catching `KeyError` exceptions is error-prone, 
verbose, and bypasses the framework's built-in validation system. It also 
returns a plain dict with a status code tuple, which is not how FastAPI 
routes should return responses.

**Fix**: Replace `data: dict` with a Pydantic `BaseModel`:
```python
class MissionInput(BaseModel):
    dist: float
    batt: float
    type: int
    payload: float = 0

@router.post("/api/mission_stats")
def calc_stats(data: MissionInput):
    ...
```

---

## Code Smell 2: High Cyclomatic Complexity (Deeply Nested Ifs)

**Location**: `legacy_stats.py` — nested if/else blocks

**The Problem**: The function contains deeply nested conditional logic:
```python
if d > 0 and b > 0:
    if t == 1:
        if b > 20:
            score = ...
        else:
            score = ...
    elif t == 2:
        if p > 50:
            ...
```

**Why it is bad**: High cyclomatic complexity (the template CI pipeline 
enforces `--max-complexity=5`) makes code hard to read, test, and maintain. 
Every nested branch doubles the number of test cases needed for full coverage.

**Fix**: Use **Guard Clauses** to return early on invalid data, flattening 
the structure:
```python
if d <= 0 or b <= 0:
    return {"error": "Invalid mission data"}
if t == 1:
    score = ...
    return {"score": min(score, 100)}
```

---

## Code Smell 3: SQL Injection Vulnerability

**Location**: `legacy_stats.py` — database query

**The Problem**:
```python
query = f"SELECT * FROM missions WHERE type = {t}"
cursor.execute(query)
```

**Why it is bad**: This is a **critical security vulnerability**. An attacker 
could pass `type = 1; DROP TABLE missions` as input, destroying the database. 
This is known as a SQL Injection attack and is listed in the OWASP Top 10 
most critical web security risks.

**Fix**: Always use parameterised queries:
```python
cursor.execute("SELECT * FROM missions WHERE type = ?", (t,))
```

---

## Code Smell 4: Duplicated Score Capping Logic

**Location**: `legacy_stats.py` — repeated in multiple branches

**The Problem**:
```python
if score > 100:
    score = 100
# ... repeated again later
if score > 100:
    score = 100
```

**Why it is bad**: Duplicated logic violates the **DRY (Don't Repeat 
Yourself)** principle. If the capping rule changes (e.g., max score 
becomes 150), it must be updated in multiple places, risking inconsistency.

**Fix**: Use Python's built-in `min()` function once at the end:
```python
return {"score": min(score, 100)}
```

---

## Resolution Status

| Smell | Severity | Status |
|---|---|---|
| Manual JSON validation | Medium | ⚠️ Identified — Pydantic refactor recommended |
| High cyclomatic complexity | High | ⚠️ Identified — Guard clauses recommended |
| SQL Injection | Critical | ⚠️ Identified — Parameterised queries required |
| Duplicated score capping | Low | ⚠️ Identified — min() function recommended |