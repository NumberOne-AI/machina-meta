# MACH-1031 Reference Range Investigation Report

**Date**: 2026-01-28
**Jira**: [MACH-1031](https://numberone.atlassian.net/browse/MACH-1031)
**Reporter**: Mike Morioka
**Investigator**: dbeal

## Summary

Investigation of reported issue: "No range values are found in any of the medical reports" on preview-92 environment for Boston Heart Dec 2025 automation run.

**Finding**: Backend data is healthy. Reference ranges ARE being extracted and stored correctly. Issue may be UI-related or a misinterpretation of the data.

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

## Conclusions

1. **Backend extraction is working correctly** - 88% of observations have range matches
2. **Boston Heart Dec 2025 specifically has ranges** - 93/105 observations (88.5%) have ranges
3. **Unmatched observations are expected** - genotypes and specialty tests without standard ranges
4. **Issue may be UI-related** - need to verify frontend display

## Next Steps

1. [ ] Check UI on preview-92 to see if ranges are displayed
2. [ ] Compare API response for observations endpoint
3. [ ] Verify frontend is correctly reading range data from API
4. [ ] Clarify with reporter what specific markers were missing ranges

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
