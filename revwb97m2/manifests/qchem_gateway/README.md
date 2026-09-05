# Q3 native Q-Chem gateway

`q3_native_gateway_v1.yaml` freezes the user-approved cases, interpretation,
three grids, and comparison tolerances before any Q3 result is generated or
inspected. Heavy Q-Chem outputs, archive copies, diagnostic density-variable
streams, and matrices belong under the project heavy-data root rather than in
this repository.

Q3 does not authorize production. It is complete only when the versioned
validator confirms all six closed-shell/open-shell UKS archive-read cases and
their independent full-matrix plus selected-row comparisons.

`q4_validation_v1.json` records the next immutable boundary: strict extraction
of the final complete block, transpose to 180x96, selection of rows
`(64,154,166)`, flattened 288-feature publication, source/archive hash checks,
atomic no-overwrite publication, and independently validated restart reuse for
all six Q3 cases. Heavy feature directories remain under the project
heavy-data root. Q4 completion does not authorize bulk production.
