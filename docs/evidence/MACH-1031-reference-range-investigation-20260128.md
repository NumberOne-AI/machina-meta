# MACH-1031 Reference Range Investigation Report

**Date**: 2026-01-28
**Jira**: [MACH-1031](https://numberone.atlassian.net/browse/MACH-1031)
**Reporter**: Mike Morioka
**Investigator**: dbeal

## Summary

Investigation of reported issue: "No range values are found in any of the medical reports" on preview-92 environment for Boston Heart Dec 2025 automation run.

**Status**: ✅ **RESOLVED**

**Root Cause**: Wrong frontend Docker image deployed on preview-92. The `dem2-infra` kustomization was using `newTag: latest` instead of the preview-specific tag.

**Resolution**: Updated `preview-dbeal-docproc-dev` tag in dem2-webui, which triggered CI/CD workflow to update dem2-infra with correct image tag.

## Environment Tested

- **preview-92** (tusdi-preview-92 namespace)
- Port forwarding: PostgreSQL, Neo4j, Redis, Backend API

## Backend Investigation Results

### 1. Neo4j Node Counts (preview-92)

| Node Type | Count |
|-----------|-------|
| RangeIntervalNode | 3,042 |
| ReferenceRangeNode | 1,400 |
| ObservationValueNode | 1,375 |

### 2. Observation-to-Range Matching (preview-92)

| Metric | Count | Percentage |
|--------|-------|------------|
| Total observations | 1,375 | 100% |
| With MATCHES_INTERVAL | 1,212 | 88% |
| Without MATCHES_INTERVAL | 163 | 12% |

**Unmatched observations** are primarily:
- Genotype markers (rs10789038, rs1001179, etc.) - no numeric ranges expected
- Heavy metals below detection limit (Thorium, Nickel, Platinum `<0.01`)
- Specialty tests (Oxidized phospholipids, Satratoxin G)

### 3. Boston Heart Dec 2025 Specific Analysis

**Document**: `Boston Heart Dec - 2025.pdf`
**UUID**: `18308da6-9736-4b9d-a631-e314d1bccfa3`
**Processing Status**: `completed`

| Metric | Count | Percentage |
|--------|-------|------------|
| Total observations | 105 | 100% |
| With ranges | 93 | 88.5% |
| Without ranges | 12 | 11.5% |

### 4. Sample Data with Ranges (Boston Heart Dec 2025)

```
| Biomarker                    | Value   | Unit    | Range                        | Category |
|------------------------------|---------|---------|------------------------------|----------|
| AA/EPA Ratio                 | 2.53    | 1       | <5.88 5.88-14.29 >14.29      | Normal   |
| Alpha-Linolenic Acid         | 20.0    | µg/mL   | <= 30.0                      | Low      |
| Alanine Aminotransferase     | 64.0    | U/L     | >= 40                        | High     |
| Aspartate Aminotransferase   | 42.0    | U/L     | >= 40                        | High     |
| Albumin                      | 4.6     | g/dL    | >= 3.5                       | High     |
| Alkaline phosphatase         | 70.0    | U/L     | <130 130-200 >200 U/L        | Normal   |
| Apolipoprotein B             | 63.0    | mg/dL   | <80 80-120 >120 mg/dL        | Normal   |
| Cobalamin                    | 826.0   | pg/mL   | >700 500-700 <500 pg/mL      | Normal   |
| Arachidonic acid             | 263.0   | µg/mL   | >= 250.0                     | High     |
```

### 5. Observations Without Ranges (expected)

```
| Biomarker                                    | Value | Unit     | Reason        |
|----------------------------------------------|-------|----------|---------------|
| 4q25 Atrial Fibrillation Risk (rs10033464)   | G/G   | 1        | Genotype      |
| 4q25 Atrial Fibrillation Risk (rs2200733)    | C/C   | 1        | Genotype      |
| 9p21 CVD Risk (rs10757278)                   | A/G   | 1        | Genotype      |
| 9p21 CVD Risk (rs1333049)                    | C/G   | 1        | Genotype      |
| Basophils                                    | 0.9   | %        | Missing range |
```

### 6. All Boston Heart Documents on preview-92

```
| Document Name                  | Report Date | Status    |
|--------------------------------|-------------|-----------|
| Boston Heart July 2021.pdf     | 2021-07-10  | completed |
| Boston Heart - May 2024.pdf    | 2024-05-24  | completed |
| Boston Heart - Sep 2024.pdf    | 2024-09-13  | completed |
| Boston Heart June 2025.PDF     | 2025-07-03  | completed |
| Boston Heart Dec - 2025.pdf    | 2025-12-30  | completed |
| Boston Heart Dec - 2025-2.png  | 2025-12-30  | completed |
| Boston Heart Dec - 2025-3.png  | 2025-12-30  | completed |
| (+ more page images)           |             |           |
```

## Comparison: Local vs Preview-92

| Metric | Local (Boston Heart Jul 2021) | Preview-92 (All Docs) |
|--------|-------------------------------|----------------------|
| Total observations | 74 | 1,375 |
| With ranges | 70 (95%) | 1,212 (88%) |
| Without ranges | 4 (5%) | 163 (12%) |
| RangeIntervalNode count | 503 | 3,042 |
| ReferenceRangeNode count | ~20 | 1,400 |

## Neo4j Queries Used

```cypher
-- Count RangeIntervalNode
MATCH (ri:RangeIntervalNode) RETURN count(ri) as total
-- Result: 3042

-- Count ReferenceRangeNode
MATCH (rr:ReferenceRangeNode) RETURN count(rr) as total
-- Result: 1400

-- Count observations with/without ranges
MATCH (ov:ObservationValueNode)
WHERE NOT (ov)-[:MATCHES_INTERVAL]->()
RETURN count(ov) as unmatched_observations
-- Result: 163

-- Boston Heart Dec 2025 observations with ranges
MATCH (ov:ObservationValueNode)-[:INSTANCE_OF]->(ot:ObservationTypeNode)
WHERE ov.source_id = '18308da6-9736-4b9d-a631-e314d1bccfa3'
OPTIONAL MATCH (ov)-[:MATCHES_INTERVAL]->(ri:RangeIntervalNode)
RETURN ot.name as biomarker, ov.value_numeric, ov.unit,
       ri.interval_notation, ri.category
LIMIT 20

-- Count matched/unmatched for Boston Heart Dec 2025
MATCH (ov:ObservationValueNode)
WHERE ov.source_id = '18308da6-9736-4b9d-a631-e314d1bccfa3'
OPTIONAL MATCH (ov)-[:MATCHES_INTERVAL]->(ri:RangeIntervalNode)
RETURN CASE WHEN ri IS NOT NULL THEN 'has_range' ELSE 'no_range' END as status,
       count(*) as count
-- Result: has_range: 93, no_range: 12
```

## UI Investigation

### Initial UI State (Before Fix)

Tested on `preview-92.n1-machina.dev/markers` using Playwright browser automation:

**Table View (markers list)**:
- Name column showed: `Potassium` / `1` / `Unit: mmol/L`
- Expected: `Potassium` / `1` / `Range: 3.5-5.0 mmol/L` / `Unit: mmol/L`
- The "Range: ..." line was **completely missing**

**Detail Dialog (click on marker)**:
- Latest Value: 4.4 mmol/L ✅
- Value History chart: displayed correctly ✅
- Reference Ranges section: **N/A, N/A, N/A** ❌

### Root Cause Analysis

Checked `dem2-infra` repository, branch `preview/dbeal-docproc-dev`:

```yaml
# k8s/overlays/preview/kustomization.yaml
images:
  - name: us-central1-docker.pkg.dev/n1-machina1/tusdi/tusdi-api:latest
    newTag: preview-dbeal-docproc-dev-e9c0334b112f7b82e7971b646a00e56828812860  # ✅ Correct

  - name: us-central1-docker.pkg.dev/n1-machina1/tusdi/tusdi-webui:latest
    newTag: latest  # ❌ WRONG - should be preview tag
```

**Problem**: Backend was using correct preview tag, but frontend was using `latest` which didn't have the range display code.

### Resolution

1. **Updated dem2-webui tag**: Moved `preview-dbeal-docproc-dev` tag from `be6ab90` (Jan 22) to `034e098` (Jan 27)
   ```bash
   cd repos/dem2-webui
   git tag -d preview-dbeal-docproc-dev
   git tag preview-dbeal-docproc-dev origin/dbeal-docproc-dev
   git push origin preview-dbeal-docproc-dev --force
   ```

2. **CI/CD Workflow Triggered**: `n1-bot-dev` automatically updated dem2-infra:
   ```
   03f256e chore: update webui image to preview-dbeal-docproc-dev-034e0981d54579fb513d99f7e2a8335f45ff6602 for preview environment
   ```

3. **ArgoCD Deployed**: New frontend image deployed to preview-92

### Verified Fix

After deployment, UI now shows ranges correctly:

| Marker | Range Displayed |
|--------|-----------------|
| Potassium | `Range: 3.5-5.3` ✅ |
| Estradiol | `Range: <=39.8` ✅ |
| Total Testosterone | `Range: 187.72-684.19` ✅ |
| Free T3 | `Range: 2.0-4.4` ✅ |
| Total Cholesterol | `Range: <200` ✅ |
| Uric Acid | `Range: 4.0-8.0` ✅ |
| Calcium | `Range: 8.6-10.3` ✅ |
| Triglycerides | `Range: <150` ✅ |
| Sodium | `Range: 135-146` ✅ |
| Ferritin | `Range: 22-322 ng/mL` ✅ |
| Albumin | `Range: 3.6-5.1` ✅ |
| Insulin | `Range: Optimal <10, Borderline 10-15, Increased Risk >15 µU/mL` ✅ |

## Conclusions

1. **Backend extraction is working correctly** - 88% of observations have range matches
2. **Boston Heart Dec 2025 specifically has ranges** - 93/105 observations (88.5%) have ranges
3. **Unmatched observations are expected** - genotypes and specialty tests without standard ranges
4. **Root cause was deployment issue** - wrong frontend Docker image (`latest` vs preview tag)
5. **Issue resolved** - updating preview tag triggered CI/CD to deploy correct frontend

## Raw Data

### Unmatched Biomarkers (preview-92 overall)

```
| Biomarker                                    | Value   | Unit                  | Count |
|----------------------------------------------|---------|-----------------------|-------|
| Oxidized phospholipids on apolipoprotein B   | <0.8    | nmol/L                | 5     |
| Basophils                                    | 0.9     | %                     | 3     |
| rs10789038                                   | A/G     | Genotype              | 2     |
| Thorium                                      | <0.01   | ug/g                  | 2     |
| rs1001179                                    | C/C     | Genotype              | 2     |
| rs1050450                                    | C/C     | Genotype              | 2     |
| Nickel                                       | <0.1    | ug/g                  | 2     |
| Bismuth                                      | <0.1    | ug/g                  | 2     |
| Platinum                                     | <0.05   | ug/g                  | 2     |
| Satratoxin G                                 | <0.05   | ng/g                  | 2     |
| Uranium                                      | <0.01   | ug/g                  | 2     |
| 8-iso-prostaglandin F2α                      | <0.05   | ug/g                  | 2     |
| Tartaric Acid                                | <dl     | mmol/mol creatinine   | 2     |
| rs1048943                                    | A/A     | Genotype              | 2     |
| Palladium                                    | <0.1    | ug/g                  | 2     |
```
