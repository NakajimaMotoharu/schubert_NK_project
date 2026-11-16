import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import {FileBlob, SpreadsheetFile} from '@oai/artifact-tool';

const base = '/home/mini/codex/project1/work/pgpt-runs/PG379/wbs66-workbook-update-20261117';
const original = '/home/mini/codex/project1/work/PMO/hourly-monitor/更新判断-20261207/PGPT更新判定・短期予実.xlsx';
const bytes = await fs.readFile(original);
const hash = crypto.createHash('sha256').update(bytes).digest('hex');
const wb = await SpreadsheetFile.importXlsx(await FileBlob.load(original));
const mode = process.argv[2] ?? 'inspect';
if (mode === 'inspect') {
  await fs.writeFile(`${base}/as-issued.bin`, bytes, {flag: 'wx'});
  const info = await wb.inspect({kind: 'sheet', include: 'id,name', maxChars: 2000});
  await fs.writeFile(`${base}/before-inspect.json`, JSON.stringify({sha256: hash, info: info.ndjson}, null, 2));
  const picture = await wb.render({sheetName: 'ポイントと初週の成果', range: 'A10:G17', scale: 1, format: 'png'});
  await fs.writeFile(`${base}/before.png`, new Uint8Array(await picture.arrayBuffer()));
  console.log(JSON.stringify({actualExit: 0, mode, originalSha256: hash, sheets: info.ndjson}));
} else if (mode === 'edit') {
  const changes = JSON.parse(await fs.readFile(`${base}/changes.json`, 'utf8'));
  if (hash !== changes.originalSha256) throw new Error('Workbook changed since read-only inspection; do not overwrite.');
  for (const change of changes.cells) {
    wb.worksheets.getItem(change.sheet).getRange(change.cell).values = [[change.value]];
  }
  // Verify that the explicitly authorised early start counts when all independent
  // acceptance fields are present, but a pre-start timestamp cannot count.
  const targets = wb.worksheets.getItem('対象別の予実');
  const saved = ['F5', 'G5', 'J5'].map(cell => [cell, targets.getRange(cell).values]);
  targets.getRange('F5').values = [['受入']];
  targets.getRange('J5').values = [['充足']];
  targets.getRange('G5').values = [[changes.actualRestartJstSerial + 0.01]];
  wb.recalculate();
  const early = targets.getRange('K5').values[0][0];
  targets.getRange('G5').values = [[changes.actualRestartJstSerial - 0.01]];
  wb.recalculate();
  const beforeStart = targets.getRange('K5').values[0][0];
  for (const [cell, values] of saved) targets.getRange(cell).values = values;
  wb.recalculate();
  const restored = targets.getRange('K5').values[0][0];
  if (early !== 1 || beforeStart !== 0 || restored !== 0) throw new Error('Early-start date boundary or restored acceptance count failed.');
  const checks = await wb.inspect({kind: 'table', range: '更新判定!A5:C20', include: 'values,formulas', tableMaxRows: 16, tableMaxCols: 3, maxChars: 5500});
  const errors = await wb.inspect({kind: 'match', searchTerm: '#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!', options: {useRegex: true, maxResults: 100}, maxChars: 2000});
  await fs.writeFile(`${base}/after-inspect.json`, JSON.stringify({checks: checks.ndjson, errors: errors.ndjson, earlyAcceptanceCanary: {early, beforeStart, restored}}, null, 2));
  for (const [sheetName, range, filename] of [
    ['ポイントと初週の成果', 'A10:G17', 'after-firstweek.png'],
    ['更新判定', 'A4:C22', 'after-summary.png'],
    ['対象別の予実', 'F4:L9', 'after-targets.png'],
    ['ポイントと初週の成果', 'A4:G8', 'after-cost.png'],
  ]) {
    const picture = await wb.render({sheetName, range, scale: 1, format: 'png'});
    await fs.writeFile(`${base}/${filename}`, new Uint8Array(await picture.arrayBuffer()));
  }
  const output = await SpreadsheetFile.exportXlsx(wb);
  await output.save(`${base}/candidate.xlsx`);
  console.log(JSON.stringify({actualExit: 0, mode, cellsUpdated: changes.cells.length, candidate: `${base}/candidate.xlsx`}));
} else throw new Error('Only explicit inspect/edit modes are supported.');
