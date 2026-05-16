# 隐私分级策略

> 由 `metadata/privacy_policy.yaml` 自动渲染。

## P0 · 非敏感公开分析字段
- DWD/DWS/ADS：允许
- 报告：允许
- LLM 上下文：允许
- 示例字段：product_code, province, city, dpd_bucket

## P1 · 业务内部键
- DWD/DWS/ADS：允许
- 报告：允许
- LLM 上下文：允许
- 示例字段：customer_id, loan_id, case_id, vendor_id, collector_id

## P2 · 脱敏个人字段
- DWD/DWS/ADS：允许
- 报告：允许
- LLM 上下文：允许
- 示例字段：mobile_masked, note_text_masked, transcript_masked

## P3 · 哈希或密文字段
- DWD/DWS/ADS：允许
- 报告：禁止
- LLM 上下文：禁止
- 示例字段：customer_id_hash, id_no_hash, mobile_hash, bank_card_hash

## P4 · 明文 PII
- DWD/DWS/ADS：禁止
- 报告：禁止
- LLM 上下文：禁止
- 示例字段：customer_name, id_no, mobile_no, bank_card_no, address

## 强制规则
- P4 不得进入 DWD/DWS/ADS。
- P4 不得进入报告。
- P4 不得进入 LLM 上下文。
- P4 只允许在 synthetic_data/raw_secure/ 中存在。
- 默认不生成 raw_secure，除非显式使用 --with-raw。
