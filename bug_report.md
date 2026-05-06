# Bug Report — Insider Threat ML Project

## Critical Issues

### BUG-001 — Appendices C, D, and E missing or overwritten
**Status:** Needs verification  
**Impact:** Final paper may be incomplete.  
**Fix:** Rebuild appendix order:

- Appendix A — CloudTrail Parser Script
- Appendix B — Feature Engineering Script
- Appendix C — Isolation Forest Training Script
- Appendix D — Advanced Threat Detection / Severity Scoring
- Appendix E — Sample Output Data
- Appendix F — AWS PowerShell Environment Setup

---

### BUG-002 — GitHub package may not include latest paper appendices
**Status:** Likely issue  
**Impact:** Portfolio repo may not match final submission.  
**Fix:** Add a `/paper/appendices/` folder with structured appendix files.

---

### BUG-003 — AWS PowerShell commands had Bash syntax mixed in
**Status:** Confirmed  
**Impact:** Commands failed in PowerShell.  
**Fix:** Use backticks (`) instead of backslashes (\) for line continuation.

---

### BUG-004 — File written to system32 caused permission error
**Status:** Confirmed  
**Impact:** Policy file creation failed.  
**Fix:** Use a user directory like Downloads.

---

## High Priority Issues

### BUG-005 — CloudTrail trail not found
**Status:** Confirmed  
**Fix:** Ensure correct order:
1. Create trail  
2. Start logging

---

### BUG-006 — S3 bucket policy incorrect for CloudTrail
**Status:** Confirmed  
**Fix:** Ensure proper permissions and correct bucket ARN.

---

### BUG-007 — GitHub upload structure incorrect
**Status:** Process issue  
**Fix:** Upload extracted project contents, not ZIP.

---

### BUG-008 — Missing .gitignore
**Status:** Needs verification  
**Fix:** Add standard Python and security ignores.

---

## Medium Priority Issues

### BUG-009 — Inconsistent output file naming
**Fix:** Standardize output file names.

---

### BUG-010 — Severity scoring not fully integrated
**Fix:** Ensure consistency across code, paper, and outputs.

---

### BUG-011 — References not aligned with citations
**Fix:** Add in-text citations for all references.

---

### BUG-012 — Architecture diagram mismatch
**Fix:** Align diagram with actual AWS components used.

---

## Portfolio Issues

### BUG-013 — README needs polish
**Fix:** Add full project overview, architecture, and usage.

---

### BUG-014 — Weak or missing tests
**Fix:** Add unit tests for pipeline components.

---

### BUG-015 — Repo structure not separated
**Fix:** Separate docs, src, outputs, and tests.

---

## Recommended Fix Order

1. Rebuild appendices  
2. Verify severity scoring integration  
3. Clean repo structure  
4. Add .gitignore  
5. Finalize README  
6. Add diagrams/screenshots  
7. Add final paper to docs  
8. Push clean repo  
9. Verify CI/CD

---

## Final Assessment

Main risks:
- Version drift between code, paper, and repo
- Missing or inconsistent appendices

Ensure all components reflect the same final system version.
