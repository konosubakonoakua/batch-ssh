```bash
❯ python ./src/batch_ssh.py .\archives\ip\ip-hiaf-blm.txt --scripts .\scripts\boot\boot-duplicate-blm-calib-params.sh

                                               Execution Summary
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Host         ┃ Target                                            ┃ Status     ┃ Message                     ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 10.10.26.61  │ .\scripts\boot\boot-duplicate-blm-calib-params.sh │ ✅ SUCCESS │                             │
│ 10.10.25.58  │ .\scripts\boot\boot-duplicate-blm-calib-params.sh │ ✅ SUCCESS │                             │
│ 10.10.26.47  │ .\scripts\boot\boot-duplicate-blm-calib-params.sh │ ✅ SUCCESS │                             │
│ 10.10.28.54  │ .\scripts\boot\boot-duplicate-blm-calib-params.sh │ ✅ SUCCESS │                             │
│ 10.10.34.134 │ .\scripts\boot\boot-duplicate-blm-calib-params.sh │ ✅ SUCCESS │                             │
│ 10.10.35.141 │ .\scripts\boot\boot-duplicate-blm-calib-params.sh │ ✅ SUCCESS │                             │
│ 10.10.43.135 │ .\scripts\boot\boot-duplicate-blm-calib-params.sh │ ✅ SUCCESS │                             │
│ 10.10.43.138 │ .\scripts\boot\boot-duplicate-blm-calib-params.sh │ ✅ SUCCESS │                             │
│ 10.10.42.139 │ .\scripts\boot\boot-duplicate-blm-calib-params.sh │ ✅ SUCCESS │                             │
│ 10.10.34.133 │ .\scripts\boot\boot-duplicate-blm-calib-params.sh │ ✅ SUCCESS │                             │
│ 10.10.26.73  │ .\scripts\boot\boot-duplicate-blm-calib-params.sh │ ✅ SUCCESS │                             │
│ 10.10.42.138 │ .\scripts\boot\boot-duplicate-blm-calib-params.sh │ ✅ SUCCESS │                             │
│ 10.10.43.136 │ .\scripts\boot\boot-duplicate-blm-calib-params.sh │ ✅ SUCCESS │                             │
│ 10.10.35.142 │ .\scripts\boot\boot-duplicate-blm-calib-params.sh │ ✅ SUCCESS │                             │
│ 10.10.35.140 │ .\scripts\boot\boot-duplicate-blm-calib-params.sh │ ✅ SUCCESS │                             │
│ 10.10.43.134 │ .\scripts\boot\boot-duplicate-blm-calib-params.sh │ ✅ SUCCESS │                             │
│ 10.10.44.141 │ .\scripts\boot\boot-duplicate-blm-calib-params.sh │ ✅ SUCCESS │                             │
│ 10.10.43.137 │ .\scripts\boot\boot-duplicate-blm-calib-params.sh │ ✅ SUCCESS │                             │
│ 10.10.44.140 │ .\scripts\boot\boot-duplicate-blm-calib-params.sh │ ✅ SUCCESS │                             │
│ 10.10.45.161 │ .\scripts\boot\boot-duplicate-blm-calib-params.sh │ ✅ SUCCESS │                             │
│ 10.10.31.151 │ .\scripts\boot\boot-duplicate-blm-calib-params.sh │ ✅ SUCCESS │                             │
│ 10.10.31.152 │ .\scripts\boot\boot-duplicate-blm-calib-params.sh │ ✅ SUCCESS │                             │
│ 10.10.31.153 │ .\scripts\boot\boot-duplicate-blm-calib-params.sh │ ✅ SUCCESS │                             │
│ 10.10.31.154 │ .\scripts\boot\boot-duplicate-blm-calib-params.sh │ ✅ SUCCESS │                             │
│ 10.10.31.156 │ .\scripts\boot\boot-duplicate-blm-calib-params.sh │ ✅ SUCCESS │                             │
│ 10.10.33.137 │ .\scripts\boot\boot-duplicate-blm-calib-params.sh │ ✅ SUCCESS │                             │
│ 10.10.33.136 │ .\scripts\boot\boot-duplicate-blm-calib-params.sh │ ✅ SUCCESS │                             │
│ 10.10.65.131 │ .\scripts\boot\boot-duplicate-blm-calib-params.sh │ ✅ SUCCESS │                             │
│ 10.10.65.130 │ .\scripts\boot\boot-duplicate-blm-calib-params.sh │ ✅ SUCCESS │                             │
│ 10.10.32.142 │ .\scripts\boot\boot-duplicate-blm-calib-params.sh │ ✅ SUCCESS │                             │
│ 10.10.62.140 │ .\scripts\boot\boot-duplicate-blm-calib-params.sh │ ✅ SUCCESS │                             │
│ 10.10.63.137 │ .\scripts\boot\boot-duplicate-blm-calib-params.sh │ ✅ SUCCESS │                             │
│ 10.10.32.143 │ .\scripts\boot\boot-duplicate-blm-calib-params.sh │ ✅ SUCCESS │                             │
│ 10.10.61.137 │ .\scripts\boot\boot-duplicate-blm-calib-params.sh │ ✅ SUCCESS │                             │
│ 10.10.61.138 │ .\scripts\boot\boot-duplicate-blm-calib-params.sh │ ✅ SUCCESS │                             │
│ 10.10.33.138 │ .\scripts\boot\boot-duplicate-blm-calib-params.sh │ ✅ SUCCESS │                             │
│ 10.10.62.139 │ .\scripts\boot\boot-duplicate-blm-calib-params.sh │ ✅ SUCCESS │                             │
│ 10.10.31.155 │ .\scripts\boot\boot-duplicate-blm-calib-params.sh │ ✅ SUCCESS │                             │
│ 10.10.63.138 │ None                                              │ ❌ FAIL    │ Connection error: timed out │
│ 10.10.65.140 │ None                                              │ ❌ FAIL    │ Connection error: timed out │
└──────────────┴───────────────────────────────────────────────────┴────────────┴─────────────────────────────┘
```
