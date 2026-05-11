import test from 'node:test';
import assert from 'node:assert/strict';

import {
  buildDailyCron,
  buildDailySchedulePreview,
  buildDailyWorkflowYaml,
  describeUtcOffset,
  normalizeDailySchedule,
} from '../src/components/wizard/schedule.js';

test('buildDailyCron keeps the default weekday digest at 09:30 UTC', () => {
  assert.equal(buildDailyCron(), '30 9 * * 1-5');
});

test('buildDailyCron converts positive UTC offsets and previous UTC day weekdays', () => {
  assert.equal(
    buildDailyCron({ time: '00:30', utcOffsetMinutes: 480, frequency: 'weekdays' }),
    '30 16 * * 0-4',
  );
});

test('buildDailyCron converts negative UTC offsets and next UTC day weekdays', () => {
  assert.equal(
    buildDailyCron({ time: '23:30', utcOffsetMinutes: -480, frequency: 'weekdays' }),
    '30 7 * * 2-6',
  );
});

test('buildDailyCron supports every day schedules', () => {
  assert.equal(
    buildDailyCron({ time: '08:15', utcOffsetMinutes: 330, frequency: 'daily' }),
    '45 2 * * *',
  );
});

test('normalizeDailySchedule falls back for invalid input', () => {
  assert.deepEqual(
    normalizeDailySchedule({ time: '99:99', utcOffsetMinutes: 9999, frequency: 'sometimes' }),
    { time: '09:30', utcOffsetMinutes: 0, frequency: 'weekdays' },
  );
});

test('preview and generated workflow include the same cron', () => {
  const schedule = { time: '08:00', utcOffsetMinutes: 480, frequency: 'weekdays' };
  assert.equal(describeUtcOffset(schedule.utcOffsetMinutes), 'UTC+08:00');
  assert.match(buildDailySchedulePreview(schedule, 'en'), /GitHub cron: 0 0 \* \* 1-5/);
  assert.match(buildDailyWorkflowYaml(schedule), /cron: '0 0 \* \* 1-5'/);
});
