# ABF fiscal-year alignment fix

ABF Annual Reports use calendar-style report labels (2021, 2022, 2023, 2024, 2025), while Nordzucker, Südzucker and Tereos are displayed with sugar-campaign-style fiscal years such as 2024/25 and 2025/26.

For cross-company financial charts, ABF Sugar report years are normalized as follows:

| ABF report year | Dashboard fiscal year label |
|---|---|
| 2021 | 2020/21 |
| 2022 | 2021/22 |
| 2023 | 2022/23 |
| 2024 | 2023/24 |
| 2025 | 2024/25 |

The original ABF label is retained in `reported_fiscal_year` / `reported_period`. This prevents the ABF line from appearing one year to the right of the other companies while keeping traceability to the original PDF.

Nordzucker 2025/26 negative margin source note: the large negative EBIT margin is not an invented metric. The Nordzucker Annual Report 2025/26 reports revenues of EUR 2,343.4m, EBIT of EUR -226.0m and EBIT margin of -9.6% in the Group management report / key-figures tables.
