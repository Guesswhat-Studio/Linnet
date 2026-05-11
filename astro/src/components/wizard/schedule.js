export const DAILY_SCHEDULE_DEFAULT = Object.freeze({
  time: '09:30',
  utcOffsetMinutes: 0,
  frequency: 'weekdays',
});

export const UTC_OFFSET_OPTIONS = Object.freeze([
  { value: -720, labelEn: 'UTC-12:00', labelZh: 'UTC-12:00' },
  { value: -660, labelEn: 'UTC-11:00', labelZh: 'UTC-11:00' },
  { value: -600, labelEn: 'UTC-10:00', labelZh: 'UTC-10:00' },
  { value: -540, labelEn: 'UTC-09:00', labelZh: 'UTC-09:00' },
  { value: -480, labelEn: 'UTC-08:00 (Pacific standard)', labelZh: 'UTC-08:00（太平洋标准时间）' },
  { value: -420, labelEn: 'UTC-07:00 (Mountain standard)', labelZh: 'UTC-07:00（山地标准时间）' },
  { value: -360, labelEn: 'UTC-06:00 (Central standard)', labelZh: 'UTC-06:00（中部标准时间）' },
  { value: -300, labelEn: 'UTC-05:00 (Eastern standard)', labelZh: 'UTC-05:00（东部标准时间）' },
  { value: -240, labelEn: 'UTC-04:00 (Atlantic / Eastern daylight)', labelZh: 'UTC-04:00（大西洋 / 东部夏令时）' },
  { value: -180, labelEn: 'UTC-03:00', labelZh: 'UTC-03:00' },
  { value: -120, labelEn: 'UTC-02:00', labelZh: 'UTC-02:00' },
  { value: -60, labelEn: 'UTC-01:00', labelZh: 'UTC-01:00' },
  { value: 0, labelEn: 'UTC+00:00', labelZh: 'UTC+00:00' },
  { value: 60, labelEn: 'UTC+01:00 (Central Europe standard)', labelZh: 'UTC+01:00（中欧标准时间）' },
  { value: 120, labelEn: 'UTC+02:00', labelZh: 'UTC+02:00' },
  { value: 180, labelEn: 'UTC+03:00', labelZh: 'UTC+03:00' },
  { value: 240, labelEn: 'UTC+04:00', labelZh: 'UTC+04:00' },
  { value: 300, labelEn: 'UTC+05:00', labelZh: 'UTC+05:00' },
  { value: 330, labelEn: 'UTC+05:30 (India)', labelZh: 'UTC+05:30（印度）' },
  { value: 360, labelEn: 'UTC+06:00', labelZh: 'UTC+06:00' },
  { value: 420, labelEn: 'UTC+07:00', labelZh: 'UTC+07:00' },
  { value: 480, labelEn: 'UTC+08:00 (China / Singapore)', labelZh: 'UTC+08:00（中国 / 新加坡）' },
  { value: 540, labelEn: 'UTC+09:00 (Japan / Korea)', labelZh: 'UTC+09:00（日本 / 韩国）' },
  { value: 570, labelEn: 'UTC+09:30', labelZh: 'UTC+09:30' },
  { value: 600, labelEn: 'UTC+10:00', labelZh: 'UTC+10:00' },
  { value: 660, labelEn: 'UTC+11:00', labelZh: 'UTC+11:00' },
  { value: 720, labelEn: 'UTC+12:00', labelZh: 'UTC+12:00' },
  { value: 780, labelEn: 'UTC+13:00', labelZh: 'UTC+13:00' },
  { value: 840, labelEn: 'UTC+14:00', labelZh: 'UTC+14:00' },
]);

const VALID_FREQUENCIES = new Set(['weekdays', 'daily']);

function parseTimeToMinutes(time) {
  const match = /^(\d{1,2}):(\d{2})$/.exec(String(time ?? ''));
  if (!match) return null;
  const hour = Number(match[1]);
  const minute = Number(match[2]);
  if (hour < 0 || hour > 23 || minute < 0 || minute > 59) return null;
  return hour * 60 + minute;
}

function normalizeTime(time) {
  const minutes = parseTimeToMinutes(time);
  if (minutes === null) return DAILY_SCHEDULE_DEFAULT.time;
  const hour = Math.floor(minutes / 60);
  const minute = minutes % 60;
  return `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`;
}

function normalizeOffsetMinutes(value) {
  const minutes = Number(value);
  if (!Number.isFinite(minutes)) return DAILY_SCHEDULE_DEFAULT.utcOffsetMinutes;
  if (minutes < -720 || minutes > 840) return DAILY_SCHEDULE_DEFAULT.utcOffsetMinutes;
  if (minutes % 15 !== 0) return DAILY_SCHEDULE_DEFAULT.utcOffsetMinutes;
  return minutes;
}

function normalizeFrequency(value) {
  return VALID_FREQUENCIES.has(value) ? value : DAILY_SCHEDULE_DEFAULT.frequency;
}

export function normalizeDailySchedule(input = {}) {
  return {
    time: normalizeTime(input.time),
    utcOffsetMinutes: normalizeOffsetMinutes(input.utcOffsetMinutes),
    frequency: normalizeFrequency(input.frequency),
  };
}

export function describeUtcOffset(offsetMinutes) {
  const minutes = normalizeOffsetMinutes(offsetMinutes);
  const sign = minutes >= 0 ? '+' : '-';
  const abs = Math.abs(minutes);
  const hour = Math.floor(abs / 60);
  const minute = abs % 60;
  return `UTC${sign}${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`;
}

function compactCronDays(days) {
  const sorted = [...days].sort((a, b) => a - b);
  const contiguous = sorted.every((day, index) => index === 0 || day === sorted[index - 1] + 1);
  if (contiguous) return `${sorted[0]}-${sorted[sorted.length - 1]}`;
  return sorted.join(',');
}

export function buildDailyCron(input = {}) {
  const schedule = normalizeDailySchedule(input);
  const localMinutes = parseTimeToMinutes(schedule.time) ?? parseTimeToMinutes(DAILY_SCHEDULE_DEFAULT.time);
  let utcMinutes = localMinutes - schedule.utcOffsetMinutes;
  let dayShift = 0;

  while (utcMinutes < 0) {
    utcMinutes += 24 * 60;
    dayShift -= 1;
  }
  while (utcMinutes >= 24 * 60) {
    utcMinutes -= 24 * 60;
    dayShift += 1;
  }

  const hour = Math.floor(utcMinutes / 60);
  const minute = utcMinutes % 60;
  const dow = schedule.frequency === 'daily'
    ? '*'
    : compactCronDays([1, 2, 3, 4, 5].map((day) => (day + dayShift + 7) % 7));

  return `${minute} ${hour} * * ${dow}`;
}

export function buildDailySchedulePreview(input = {}, locale = 'en') {
  const schedule = normalizeDailySchedule(input);
  const cron = buildDailyCron(schedule);
  const cadence = schedule.frequency === 'daily'
    ? (locale === 'zh' ? '每天' : 'daily')
    : (locale === 'zh' ? '工作日' : 'weekdays');
  if (locale === 'zh') {
    return `${schedule.time} ${describeUtcOffset(schedule.utcOffsetMinutes)}，${cadence}运行 -> GitHub cron: ${cron}`;
  }
  return `${schedule.time} ${describeUtcOffset(schedule.utcOffsetMinutes)}, ${cadence} -> GitHub cron: ${cron}`;
}

export function buildDailyWorkflowYaml(input = {}) {
  const schedule = normalizeDailySchedule(input);
  const cron = buildDailyCron(schedule);
  const cadence = schedule.frequency === 'daily' ? 'daily' : 'weekdays';
  const scheduleComment = `${schedule.time} ${describeUtcOffset(schedule.utcOffsetMinutes)}, ${cadence}; GitHub cron is UTC`;

  return `name: Daily Digest

on:
  schedule:
    - cron: '${cron}'   # ${scheduleComment}
  workflow_dispatch:        # manual trigger for testing

env:
  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: "true"

concurrency:
  group: daily-digest-\${{ github.ref }}
  cancel-in-progress: false

jobs:
  digest:
    runs-on: ubuntu-latest
    permissions:
      contents: write       # needed to git push
      actions: write        # needed to dispatch pages.yml after digest succeeds
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Configure git identity
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"

      - name: Sync latest branch
        run: git pull --rebase origin \${{ github.ref_name }}

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run daily pipeline
        run: |
          set -euxo pipefail
          python -u main.py --mode daily 2>&1 | tee daily-pipeline.log
        env:
          OPENROUTER_API_KEY: \${{ secrets.OPENROUTER_API_KEY }}
          API_NINJAS_KEY:     \${{ secrets.API_NINJAS_KEY }}
          FINNHUB_API_KEY:     \${{ secrets.FINNHUB_API_KEY }}
          SEC_USER_AGENT:      \${{ secrets.SEC_USER_AGENT }}
          LINNET_SEC_USER_AGENT: \${{ secrets.LINNET_SEC_USER_AGENT }}
          PYTHONUNBUFFERED: "1"
          # Optional delivery sinks
          # Set these secrets in your repo to enable the corresponding sink.
          # Leave unset or empty to skip that sink gracefully.
          SLACK_WEBHOOK_URL:    \${{ secrets.SLACK_WEBHOOK_URL }}
          SERVERCHAN_SENDKEY:   \${{ secrets.SERVERCHAN_SENDKEY }}

      - name: Upload daily pipeline log
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: daily-pipeline-log-\${{ github.run_id }}
          path: daily-pipeline.log
          if-no-files-found: warn

      - name: Commit and push outputs
        run: |
          # Generated JSON stays ignored locally, so CI force-adds it when publishing.
          git add docs/
          git add -f docs/data/
          git diff --staged --quiet || git commit -m "digest: $(date -u +%Y-%m-%d)"
          git pull --rebase -X ours origin \${{ github.ref_name }}
          git push

      - name: Trigger Pages publish
        env:
          GH_TOKEN: \${{ github.token }}
          GH_API_URL: \${{ github.api_url }}
          GH_REPOSITORY: \${{ github.repository }}
          GH_REF_NAME: \${{ github.ref_name }}
        run: |
          curl --fail-with-body -L \\
            -X POST \\
            -H "Accept: application/vnd.github+json" \\
            -H "Authorization: Bearer \${GH_TOKEN}" \\
            "\${GH_API_URL}/repos/\${GH_REPOSITORY}/actions/workflows/pages.yml/dispatches" \\
            -d "{\\"ref\\":\\"\${GH_REF_NAME}\\"}"
`;
}
